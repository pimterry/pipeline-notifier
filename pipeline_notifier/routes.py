def setup_routes(app, pipelines):
    @app.route('/')
    def hello():
        return 'Hello World!'