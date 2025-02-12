import pygame
from gamelib.Core import Core
from gamelib.network.syncs.NetworkSceneManager import NetworkSceneManager
from test_game.scene.MenuScene import MenuScene
from test_game.scene.TetrisScene import TetrisScene
from test_game.scene.LobbyScene import LobbyScene
class TestGame:
    """デバッグ用のgame"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.DOUBLEBUF)

        self.clock = pygame.time.Clock()
        self.running = True

        # gamelibの初期化
        self.gamelib = Core()

        self.scene_manager = NetworkSceneManager.get_instance()

        # sceneをセットアップする
        self.setup_scenes()

    def setup_scenes(self):
        """gameSceneを登録する"""
        self.scene_manager.add_scene(MenuScene(self.screen))
        self.scene_manager.add_scene(TetrisScene(self.screen))
        self.scene_manager.add_scene(LobbyScene(self.screen)) # serverを立てた後のlobbyscene(Game|Roleとか変えれる)
        self.scene_manager.set_active_scene("MenuScene")
    def run(self):
        """メインループ"""
        while self.running:
            delta_time = self.clock.tick(1000) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.gamelib.handle_event(event)
            self.screen.fill((0,0,0,0))
            self.gamelib.update(delta_time)
            self.gamelib.render(self.screen)
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = TestGame()
    game.run()