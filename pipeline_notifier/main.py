import os
import cherrypy
from flask import Flask, json

from pipeline_notifier.routes import setup_routes
from pipeline_notifier.pipeline_model import Pipeline, BuildStep
from pipeline_notifier.hipchat_notifier import HipchatNotifier

def build_app():
    app = Flask("Pipeline Notifier")

    pipelines_config = json.loads(os.environ["PIPELINE_NOTIFIER_PIPELINES"])
    notifier = HipchatNotifier("", 123)
    pipelines = build_pipelines(pipelines_config, notifier)

    setup_routes(app, pipelines, None)
    return app

def build_pipelines(pipelines_config, notifier):
    return [Pipeline(config["name"],
                     [BuildStep(step) for step in config["steps"]],
                     notifier)
            for config in pipelines_config]

def run_server(app):
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
    app = build_app()
    run_server(app)