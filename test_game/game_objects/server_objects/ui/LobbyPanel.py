from gamelib.network.syncs.game_objects.NetworkPanel import NetworkPanel
from gamelib.game.ui.ui_objects.MeshText import MeshText
from gamelib.game.ui.ui_objects.MeshButtonText import MeshButtonText
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory

class LobbyPanel(NetworkPanel):
    def __init__(self, name="LobbyPanel", active=True, parent=None, network_id=None, steam_id=None):
        super().__init__(name, active, parent, network_id, steam_id)
        self.network_manager = NetworkManager.get_instance()
        self.canvas = self.network_manager.scene_manager.current_scene.canvas

    def start(self):
        self.join_user = self.add_ui(MeshText(self.canvas, "JoinUsers", "KH-Dot-Dougenzaka-12.ttf", "", 40, alignment="right", position=(10, 30)))
        self.state = self.add_ui(MeshText(self.canvas, "JoinUsers", "KH-Dot-Dougenzaka-12.ttf", "", 60, alignment="center", position=("center", "center"), rotation=30))
        self.start_btn = self.add_ui(MeshButtonText(self.canvas, "Start", position=(300, "bottom-200"), ui_text="StartGame"))
        self.start_btn.on_click = self.on_start
        super().start()
    def update(self, dt):
        super().update(dt)
        if self.initialized:
            members = self.network_manager.steam.get_all_lobby_members(self.network_manager.lobby_id)
            text = "users : "
            for user in members:
                steam_name = self.network_manager.steam.get_steam_name(user)
                text += f"{steam_name}  "
            self.join_user.set_text(text)

            if len(members) <= 1:
                self.state.set_text("(デバッグモード)参加者を待っています...")
                self.start_btn.set_active(True)
            else:
                self.state.set_text("ゲーム開始可能です！")
                if self.network_manager.is_server:
                    self.start_btn.set_active(True)
    def on_start(self):
        self.network_manager.scene_manager.set_active_network_scene("TetrisScene")
        

NetworkObjectFactory.register_class(LobbyPanel)