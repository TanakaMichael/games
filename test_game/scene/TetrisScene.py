from gamelib.network.syncs.NetworkScene import NetworkScene
from gamelib.game.utility.Coroutine import WaitForSeconds
from ..game_objects.server_objects.Field import Field
from ..game_objects.server_objects.ui.TetrisPanel import TetrisPanel
from gamelib.game.game_object.utility_object.FrameRate import FrameRate
import pygame
import time
class TetrisScene(NetworkScene):
    def __init__(self, screen):
        super().__init__("TetrisScene", screen)
        self.start_count = 5
    def start(self):
        self.menu = self.add_object(TetrisPanel())
        self.field1 = self.add_object(Field(number=0))
        self.field2 = self.add_object(Field(number=1))

        self.fps = self.add_object(FrameRate(self.canvas))

        if self.network_manager.is_server:
            # ゲームの開始を遅れさせる
            
            self.coroutine_manager.start_coroutine(self.start_game_delay)
        super().start()

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
    def generate_block_pattern(self):
        """server側でブロックの生成patternを作成する"""
        self.seed = int(time.time())


