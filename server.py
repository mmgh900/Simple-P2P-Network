from bottle import route, run, response
from json import dumps
import yaml
from multiprocessing import Process
import requests


config = yaml.safe_load(open('Config.yml', "r"))
nodes = yaml.safe_load(open('NodeFiles.yml', "r"))


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
        if node_name == friend_name:
            return friend_port
    
    nearest_node = 2
    nearest_node_address = findTheAddress(2)

    url = f'http://localhost:{nearest_node_address}/get_port/{node_name}'
    resp = requests.get(url=url)
    data = resp.json() # Check the JSON Response Content documentation below
    print(data)

def getTheFile(file_name):
    owner = whereIsTheFile(file_name)

    # Check to see if we have the file in our own computer
    if owner == config['node_number']:
        print('We have the file already')
        return 
    
    address = findTheAddress(owner)
    return address


@route('/get_port/{node_name}')
def getPort(node_name):
    rv = [{"id": 1, "name": "Test Item 1"}, {"id": 2, "name": "Test Item 2"}]
    response.content_type = 'application/json'
    return dumps(rv)


def request():
    print(getTheFile('file6'))

def runServer():
    run(host='localhost', port=config['node_port'])


if __name__ == '__main__':
  p1 = Process(target=runServer)
  p1.start()
  p2 = Process(target=request)
  p2.start()
  p1.join()
  p2.join()

