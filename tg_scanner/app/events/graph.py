from flask_socketio import Namespace
from  tg_scanner.app.modules import TGScanner


class Graph(Namespace):

    def __init__(self, namespace):
        super(Graph, self).__init__(namespace)

        self.scanner = TGScanner()
        self.scanner.update = self.update
        self.scanner.add_node_list = self.add_node_list
        self.scanner.remove_node_list = self.remove_node_list
        self.scanner.set_text = self.set_text

    def on_connect(self):
        print('Client connected!')
        self.scanner.start()
        pass

    def on_disconnect(self):
        print('Client disconnected!')
        pass

    def update(self, data):
        self.emit('update_graph', data)

    def add_node_list(self, data):
        self.emit('add_node_list', data)

    def remove_node_list(self):
        self.emit('remove_node_list')

    def set_text(self, id_text):
        self.emit('set_text', id_text)
