# このプログラムを動かすために必要なクラス
from gamelib.game.SceneManager import SceneManager
from gamelib.game.Game import Game
class Core:
    def __init__(self):
        # このプログラムの中核トンを渡す
        self.game = Game()

    def get_scene_manager(self):
        return SceneManager.get_instance()
    def update(self, dt):
        self.game.update(dt)
    def render(self, screen):
        self.game.render(screen)
    def handle_event(self, event):
        self.game.handle_event(event)