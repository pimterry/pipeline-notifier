from flask import json
from pipeline_notifier.pipeline_model import Pipeline

def setup_routes(app, pipelines):
    @app.route('/status')
    def status():
        return json.dumps({
            "status": "ok",
            "pipelines": [
                p.status for p in pipelines
            ]
        })