import os
import cherrypy
from pipeline_notifier.routes import setup_routes
from flask import Flask

app = Flask("Pipeline Notifier")
setup_routes(app, [])

def run_server():
    cherrypy.tree.graft(app, '/')

    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': int(os.environ.get('PORT', '8080')),
        'server.socket_host': '0.0.0.0'
    })

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    run_server()