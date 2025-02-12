from gamelib.game.game_object.Panel import Panel
from gamelib.game.ui.ui_objects.MeshButtonText import MeshButtonText
from gamelib.network.syncs.NetworkSceneManager import NetworkSceneManager
from gamelib.game.ui.ui_objects.InputBox import InputBox
from gamelib.game.ui.component.FadeAnimation import FadeAnimation
from gamelib.game.ui.component.MoveAnimation import MoveAnimation
class ServerMenu(Panel):
    def __init__(self, canvas, name, active=False, parent=None):
        super().__init__(canvas, name, active, parent)
    def start(self):
        super().start()
        self.create_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="Create", position=("right-250", "bottom-120"), ui_text="Create", font_height=60, font_alignment="center", correction_background_scale=(1.2,1.2)))
        self.cancel_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="Cancel", position=("right-600", "bottom-120"), ui_text="Cancel", font_height=60, font_alignment="center", correction_background_scale=(1.2,1.2)))
        self.create_btn.on_pressed = self.on_create_pressed
        self.cancel_btn.on_pressed = self.on_cancel_pressed
    def on_create_pressed(self):
        self.create_server()
    def on_cancel_pressed(self):
        self.scene.get_object("MainMenu").set_active(True)
        self.set_active(False)

    def create_server(self):
        from gamelib.network.NetworkManager import NetworkManager
        self.network_manager = NetworkManager.get_instance()
        # サーバーをセットアップする
        if self.network_manager.setup_server(2, 2):
            self.network_manager.scene_manager.set_active_scene("LobbyScene")
            self.set_active(False)
