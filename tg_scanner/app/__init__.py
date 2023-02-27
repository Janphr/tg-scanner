import socket
import threading

from flask import Flask
from flask_socketio import SocketIO

from .views import IndexView
from .events import *


class App(threading.Thread):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)

    def register_views(self):
        # Register all Views per Namespace
        IndexView.register(self.app, route_base='/')

    def register_events(self):
        # Register all Events per Namespace
        self.socketio.on_namespace(Graph('/graph'))

    def run_app(self, host='localhost', port=5000):
        # set host to 'localhost' for a local only application.
        # default finds the first available address in local network
        if host == 'localhost':
            return self.app.run(debug=True, use_reloader=False)
        i = 2
        while True:
            try:
                self.app.run(debug=True, use_reloader=False, host=host + str(i), port=port)
            except socket.error as e:
                if e.errno == 98:
                    port += 1
                elif e.errno == 99 or e.errno == 10049:
                    i += 1
                else:
                    raise
            else:
                break

    def run(self):

        self.register_views()
        self.register_events()

        # No caching at all for API endpoints.
        @self.app.after_request
        def add_header(response):
            # response.cache_control.no_store = True
            response.headers[
                'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response

        self.run_app()
