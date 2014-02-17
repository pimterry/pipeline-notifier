from flask import json

def setup_routes(app, pipelines, notifier):
    @app.route('/status')
    def status():
        return json.dumps({
            "status": "ok",
            "pipelines": [
                p.status for p in pipelines
            ]
        })