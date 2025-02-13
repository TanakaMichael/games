from gamelib.network.syncs.game_objects.NetworkPanel import NetworkPanel
from gamelib.game.ui.ui_objects.MeshText import MeshText
from gamelib.game.utility.Coroutine import WaitForSeconds
from gamelib.game.ui.component.MoveAnimation import MoveAnimation
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
from gamelib.game.InputManager import InputManager
class TetrisPanel(NetworkPanel):
    def __init__(self, name="LobbyPanel", active=True, parent=None, network_id=None, steam_id=None):
        super().__init__(name, active, parent, network_id, steam_id)
        self.network_manager = NetworkManager.get_instance()
        self.canvas = self.network_manager.scene_manager.current_scene.canvas

        self.input_manager = InputManager.get_instance()
        # 操作のためのactionを取得する
        self.move_right_action = self.input_manager.get_action("MoveRight")
        self.move_left_action = self.input_manager.get_action("MoveLeft")
    def start(self):
        self.join_user = self.add_ui(MeshText(self.canvas, "JoinUsers", "KH-Dot-Dougenzaka-12.ttf", "", 40, alignment="right", position=(10, 30)))
        self.state = self.add_ui(MeshText(self.canvas, "State", "KH-Dot-Dougenzaka-12.ttf", "", 100, alignment="center", position=("center", "center-300")))
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
            if self.move_left_action.get_on_press():
                print("move it!")
    def receive_message(self, message):
        super().receive_message(message)
        if message.get("type") == "count_game":
            self.state.set_text(f"{message['count']}")
        elif message.get("type") == "start_game":
            self.state.set_text("start!")
            self.coroutine_manager.start_coroutine(self.visible_state)
    def visible_state(self):
        self.state_animation = self.state.add_component(MoveAnimation, target_position=("center", "top-100"))
        yield WaitForSeconds(1)
        self.state_animation.start()
        

NetworkObjectFactory.register_class(TetrisPanel)