from gamelib.network.syncs.game_objects.NetworkPanel import NetworkPanel
from gamelib.game.ui.ui_objects.MeshText import MeshText
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory

class LobbyPanel(NetworkPanel):
    def __init__(self, canvas, name="LobbyPanel", active=True, parent=None):
        super().__init__(canvas, name, active, parent)
        self.network_manager = NetworkManager.get_instance()

    def start(self):
        self.join_user = self.add_ui(MeshText(self.canvas, "JoinUsers", "KH-Dot-Dougenzaka-12.ttf", "", 40, alignment="right", position=(10, 30)))
        self.state = self.add_ui(MeshText(self.canvas, "JoinUsers", "KH-Dot-Dougenzaka-12.ttf", "", 60, alignment="right", position=("center", "center+300")))
    def update(self, dt):
        super().update(dt)
        members = self.network_manager.steam.get_all_lobby_members(self.network_manager.lobby_id)
        text = "users : "
        for user in members:
            steam_name = self.network_manager.steam.get_steam_name(user)
            text += f"{steam_name}  "
        self.join_user.set_text(text)

        if len(members) <= 1:
            self.state.set_text("参加者を待っています...")

NetworkObjectFactory.register_class(LobbyPanel)