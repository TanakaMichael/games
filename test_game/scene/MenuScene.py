from gamelib.game.core.Scene import Scene
from ..game_objects.Menu import Menu
from gamelib.game.core.Camera import Camera
from gamelib.game.game_object.utility_object.DebugCamera import DebugCamera
from ..game_objects.TestPlayer import TestPlayer
from gamelib.game.game_object.utility_object.FrameRate import FrameRate
from ..game_objects.ClientMenu import ClientMenu
from ..game_objects.ServerMenu import ServerMenu
from gamelib.game.core.Layer.objects.Background import Background
from gamelib.game.core.Layer.Layer import Layer

class MenuScene(Scene):
    def __init__(self, screen):
        super().__init__("MenuScene", screen)
        self.camera = self.add_camera(DebugCamera(self.canvas))
        self.main_menu = self.add_object(Menu(self.canvas, name="MainMenu", active=True))
        self.client_menu = self.add_object(ClientMenu(self.canvas, name="ClientMenu", active=False))
        self.server_menu = self.add_object(ServerMenu(self.canvas, name="ServerMenu", active=False))
        #self.test_player = self.add_object(TestPlayer(name="TestPlayer"))
        self.fps = self.add_object(FrameRate(self.canvas, name="FrameRate", active=True))

        #self.background = self.camera.layer_manager.add_layer(Layer("background", 0.5))
        #self.background.add_object(Background("test_game/game_objects/R.jpg"))
    def start(self):
        super().start()