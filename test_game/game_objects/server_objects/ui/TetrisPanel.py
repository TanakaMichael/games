from gamelib.network.syncs.game_objects.NetworkPanel import NetworkPanel
from gamelib.game.ui.ui_objects.MeshText import MeshText
from gamelib.game.utility.Coroutine import WaitForSeconds
from gamelib.game.ui.component.MoveAnimation import MoveAnimation
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
from gamelib.game.ui.component.MoveAnimation import MoveAnimation, ease_in_out_sine
from gamelib.game.InputManager import InputManager
import pygame
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
        self.field0 = self.add_ui(MeshText(self.canvas, "field0", "KH-Dot-Dougenzaka-12.ttf", "", 100, rotation=30))
        self.field1 = self.add_ui(MeshText(self.canvas, "field1", "KH-Dot-Dougenzaka-12.ttf", "", 100, rotation=30))

        self.field0_animation = self.field0.add_component(MoveAnimation)
        self.field1_animation = self.field1.add_component(MoveAnimation)
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
        elif message.get("type") == "end_game" and message.get("win") == 0:
            field = self.scene.get_object("field0")
            camera = self.scene.get_camera("camera0")
            center, _ = camera.world_to_screen(pygame.Vector2(field.transform.global_position.x + (field.mino_size * field.width) / 2, field.transform.global_position.y + 100))

            self.field0.rect_transform.set_local_position((center.x, -100))
            self.field0_animation.start_to_target_animation(center, ease_function=ease_in_out_sine)
            self.field0.rect_transform.set_local_rotation(0)

            self.field0.set_text("Winner!")
        elif message.get("type") == "end_game" and message.get("win") == 1:
            field = self.scene.get_object("field1")
            camera = self.scene.get_camera("camera0")
            center, _ = camera.world_to_screen(pygame.Vector2(field.transform.global_position.x + (field.mino_size * field.width) / 2, field.transform.global_position.y + 100))

            self.field1.rect_transform.set_local_position((center.x, -100))
            self.field1_animation.start_to_target_animation(center, ease_function=ease_in_out_sine)
            self.field1.rect_transform.set_local_rotation(0)

            self.field1.set_text("Winner!")


        elif message.get("type") == "game_over" and message.get("field_number") == 0:
            field = self.scene.get_object("field0")
            camera = self.scene.get_camera("camera0")
            center, _ = camera.world_to_screen(field.transform.global_position)
            self.field0.rect_transform.set_local_position(center)
            self.field0.set_text("Loser!")
        elif message.get("type") == "game_over" and message.get("field_number") == 1:
            field = self.scene.get_object("field1")
            camera = self.scene.get_camera("camera0")
            center, _ = camera.world_to_screen(field.transform.global_position)
            self.field1.rect_transform.set_local_position(center)
            self.field1.set_text("Loser!")

    def visible_state(self):
        self.state_animation = self.state.add_component(MoveAnimation, target_position=("center", "top-100"))
        yield WaitForSeconds(1)
        self.state_animation.start()
        

NetworkObjectFactory.register_class(TetrisPanel)