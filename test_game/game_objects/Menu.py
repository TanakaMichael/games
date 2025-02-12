from gamelib.game.game_object.Panel import Panel
from gamelib.game.ui.ui_objects.MeshButtonText import MeshButtonText
from gamelib.game.ui.ui_objects.MeshText import MeshText
from gamelib.game.ui.ui_objects.InputBox import InputBox
from gamelib.game.ui.component.FadeAnimation import FadeAnimation
from gamelib.game.ui.component.MoveAnimation import MoveAnimation
class Menu(Panel):
    def __init__(self, canvas, name, active=False, parent=None):
        super().__init__(canvas, name, active, parent)
    def start(self):
        super().start()
        self.title = self.add_ui(MeshText(self.canvas, "Title", "KH-Dot-Dougenzaka-12.ttf", "Tetris", position=("center", "top-120"), font_height=140))
        title_animation = self.title.add_component(MoveAnimation, target_position=("center", "top+140"), duration=0.3)
        self.server_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="Server", position=("left-250", "top+300"), ui_text="Server", font_height=80, font_alignment="center", correction_background_scale=(1.2,1.2), fixed_background_size=(500, 100)))
        self.client_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="Client", position=("right+250", "top+400"), ui_text="Client", font_height=80, font_alignment="center", correction_background_scale=(1.2,1.2), fixed_background_size=(500, 100)))
        self.server_btn.on_pressed = self.server_pressed
        self.client_btn.on_pressed = self.client_pressed
        server_animation = self.server_btn.add_component(MoveAnimation, target_position=("center", "top+400"), duration=0.4)
        client_animation = self.client_btn.add_component(MoveAnimation, target_position=("center", "top+600"), duration=0.4, finish_animation=lambda: title_animation.start())
        server_animation.start()
        client_animation.start()

        self.input_box = self.add_ui(InputBox(canvas=self.canvas, name="input", position=("right-100", "bottom-100"), default_text="入力！", font_height=80, background_size=(300,90)))
    def server_pressed(self):
        self.scene.get_object("ServerMenu").set_active(True)
        self.set_active(False)
    def client_pressed(self):
        self.scene.get_object("ClientMenu").set_active(True)
        self.set_active(False)