from gamelib.network.syncs.NetworkScene import NetworkScene
from gamelib.game.utility.Coroutine import WaitForSeconds
from ..game_objects.server_objects.Field import Field
from ..game_objects.server_objects.ui.TetrisPanel import TetrisPanel
from gamelib.game.game_object.utility_object.FrameRate import FrameRate
from gamelib.game.core.Camera import Camera
import pygame
import time
class TetrisScene(NetworkScene):
    def __init__(self, screen):
        super().__init__("TetrisScene", screen)

    def start(self):
        self.init()
        self.menu = self.add_object(TetrisPanel())

        self.camera = self.add_camera(Camera(self.canvas, name="camera0"))
        self.field0 = self.add_object(Field("field0", number=0))
        self.field1 = self.add_object(Field("field1", number=1))

        self.fps = self.add_object(FrameRate(self.canvas))

        if self.network_manager.is_server:
            # ゲームの開始を遅れさせる
            self.generate_block_pattern()
            self.coroutine_manager.start_coroutine(self.start_game_delay)
        super().start()
    def init(self):
        self.start_count = 5
        self.is_alive_field_0 = False
        self.is_alive_field_1 = False
        self.end_game = False

    def start_game_delay(self):
        """ゲーム開始を5秒遅らせて全クライアントに通知"""
        print("🎮 ゲーム開始の準備中... 5秒後に開始")
        for _ in range(self.start_count):
            self.network_manager.broadcast({"type": "count_game", "count": (self.start_count - _) }, True)
            yield WaitForSeconds(1)  # **5秒待機**
        self.network_manager.broadcast({"type": "start_game"}, True)

        print("🚀 ゲームスタート！")
    def update(self, dt):
        super().update(dt)
        if self.network_manager.is_server and not self.end_game:
            if self.field0.is_alive and not self.field1.is_alive:
                # ゲーム終了の合図
                self.network_manager.broadcast({"type": "end_game", "win": 0}, True)
                self.field0.running = False
                self.end_game = True


                self.coroutine_manager.start_coroutine(self.return_lobby_menu)
            if self.field1.is_alive and not self.field0.is_alive:
                # ゲーム終了の合図
                self.network_manager.broadcast({"type": "end_game", "win": 1}, True)
                self.field1.running = False
                self.end_game = True

                self.coroutine_manager.start_coroutine(self.return_lobby_menu)
    def return_lobby_menu(self):
        yield WaitForSeconds(3)
        self.network_manager.scene_manager.set_active_network_scene("LobbyScene")
    def receive_message(self, message):
        return super().receive_message(message)


    def generate_block_pattern(self):
        """server側でブロックの生成patternを作成する"""
        self.seed = int(time.time())


