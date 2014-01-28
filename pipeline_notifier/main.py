import os
import cherrypy
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

def run_server():
    cherrypy.tree.graft(app, '/')

    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': 8080,
        'server.socket_host': '0.0.0.0'
    })

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    run_server()