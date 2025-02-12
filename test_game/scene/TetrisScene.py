from gamelib.network.syncs.NetworkScene import NetworkScene

class TetrisScene(NetworkScene):
    def __init__(self, screen):
        super().__init__("TetrisScene", screen)
    def start(self):
        #self.field1 = self.

        self.menu = self.add_object()
