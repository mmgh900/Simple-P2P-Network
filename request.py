from bottle import route, run, response, static_file
from json import dumps
import yaml
from multiprocessing import Process
import requests
import sys
from pathlib import Path


peer_number = sys.argv[1]
try:
    requested_file = sys.argv[2]
except:
    requested_file = None

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


@route('/get_port/<node_name>')
def getPort(node_name):
    response.content_type = 'application/json'
    return dumps({"node_name": node_name, "node_port": findTheAddress(node_name), 'visited_nodes': []})

@route('/get_file/<file_name>')
def getFile(file_name):
    response.content_type = 'application/json'
    return static_file(file_name, root=config['owned_files_dir'])


def runServer():
    run(host='localhost', port=config['node_port'])


if __name__ == '__main__':

    port = config['node_port']
    if(is_port_in_use(port)):
        if bool(requested_file):
            getTheFile(requested_file)
        else:
            print(f'Your are already listening on port {port}...')
    else:
        if bool(requested_file):
            p1 = Process(target=getTheFile(requested_file))
            p1.start()
            p2 = Process(target=runServer)
            p2.start()
            p1.join()
            p2.join()
        else:
            runServer()
