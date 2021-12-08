from bottle import route, run, response, static_file

@route('/')
def getPort():
    return 'hi'


run(host='192.168.43.249', port=80)