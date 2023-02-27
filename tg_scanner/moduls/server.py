import threading


class Server(threading.Thread):

    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        self.app.run_server(debug=True, use_reloader=False)
