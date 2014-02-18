from flask import json
import flask
from pipeline_notifier import incoming_notifications

def setup_routes(app, pipelines):
    @app.route('/status')
    def status():
        return json.dumps({
            "status": "ok",
            "pipelines": [
                p.status for p in pipelines
            ]
        })

    @app.route('/bitbucket', methods=['POST'])
    def bitbucket():
        notification = incoming_notifications.BitbucketNotification(json.loads(flask.request.form['payload']))
        for pipeline in pipelines:
            for commit in notification.commits:
                pipeline.add_commit(commit)