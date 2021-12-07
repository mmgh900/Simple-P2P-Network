

from bottle import route, run, response, static_file
from json import dumps
import yaml
from multiprocessing import Process
import requests
import sys
from pathlib import Path
import threading

peer_number = 4

config = yaml.safe_load(open(f'Config{peer_number}.yml', "r"))
nodes = yaml.safe_load(open('NodeFiles.yml', "r"))
number_of_peers = len(nodes['node_files'])


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def whereIsTheFile(file_name):
    for node in nodes['node_files']:
        node_name = node['node_name']
        node_files = node['node_files']

        if file_name in node_files:
            return node_name


def findTheAddress(node_name):
    for friend in config['friend_nodes']:
        friend_name = friend['node_name']
        friend_port = friend['node_port']
        if str(node_name) == str(friend_name):
            return friend_port



    nearest_node = int(config['node_number'] + 1 % number_of_peers)
    nearest_node_address = findTheAddress(nearest_node)

    url = f'http://localhost:{nearest_node_address}/get_port/{node_name}'
    resp = requests.get(url=url)
    data = resp.json()  # Check the JSON Response Content documentation below
    return data['node_port']


def getTheFile(file_name):
    owner = whereIsTheFile(file_name)

    out_put_folder = config['new_files_dir']
    # Check to see if we have the file in our own computer
    if owner == config['node_number']:
        print('We have the file already')
        return

    address = findTheAddress(owner)
    url = f'http://localhost:{address}/get_file/{file_name}'
    resp = requests.get(url=url)
    Path(out_put_folder).mkdir(parents=True, exist_ok=True)
    with open(f'./{out_put_folder}/{file_name}', 'wb') as file:
        file.write(resp.content)

    # update Config the new file has been owned by this peer
    config["owned_files"].append(file_name)
    with open(f'Config{peer_number}.yml', 'w') as configFile:
        yaml.dump(config, configFile)

    # update NodeFiles the new file is also available in this peer
    for node in nodes['node_files']:
        node_name = node['node_name']
        node_files = node['node_files']

        if peer_number == node_name:
            node_files.append(file_name)
            node['node_files'] = node_files
            break

    with open(r'NodeFiles.yml', 'w') as nodefilec:
        yaml.dump(nodes, nodefilec)

    print(f"{file_name} succesfully downloaded into {config['new_files_dir']}")


@route('/get_port/<node_name>')
def getPort(node_name):
    response.content_type = 'application/json'
    return dumps({"node_name": node_name, "node_port": findTheAddress(node_name)})

@route('/get_file/<file_name>')
def getFile(file_name):
    response.content_type = 'application/json'
    return static_file(file_name, root=config['owned_files_dir'])


def runServer():
    run(host='localhost', port=config['node_port'])


def command():
    while True:
        cmd = input(">> ")
        part = cmd.split()
        if part[0] == "request":
            name = part[1]
            go_get_file = threading.Thread(target=getTheFile(name))
            go_get_file.start()
        elif part[0] == "exit":
            print("disconnected")
            exit(0)
        else:
            print("wrong command")

if __name__ == '__main__':

    port = config['node_port']
    if is_port_in_use(port):
            print(f'Your are already listening on port {port}...')
    else:
        go_run_server = threading.Thread(target=runServer)
        go_run_server.start()
        command()



# node_files:
#   - node_name: 1
#     node_files:
#       - "file1"
#       - "file2"
#       - "file3"
#   - node_name: 2
#     node_files:
#       - "file4"
#       - "file5"
#   - node_name: 3
#     node_files:
#       - "file6"
#   - node_name: 4
#     node_files:
#       - "file7"
#       - "file8"
