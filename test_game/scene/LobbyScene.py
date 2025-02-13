from gamelib.network.syncs.NetworkScene import NetworkScene
from ..game_objects.server_objects.ui.LobbyPanel import LobbyPanel

class LobbyScene(NetworkScene):
    def __init__(self, screen):
        super().__init__("LobbyScene", screen)
    def start(self):
        self.game_ui = self.add_object(LobbyPanel())
        super().start()
