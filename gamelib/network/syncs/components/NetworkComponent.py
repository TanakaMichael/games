from ....game.component.Component import Component

class NetworkComponent(Component):
    def __init__(self, game_object):
        super().__init__(game_object)
    def receive_message(self, message):
        pass
    def force_sync(self):
        pass