from gamelib.game.game_object.GameObject import GameObject

from gamelib.game.component.Sprite import Sprite
from gamelib.game.component.Clickable import Clickable
import math
class TestPlayer(GameObject):
    def __init__(self, name):
        super().__init__(name)
        self.sprite = self.add_component(Sprite, image_path="test_game/game_objects/FbPGCUhaIAAI1q6-topaz-sharpen-lighting-upscale-6x.png", base_size=(100, 100))
        self.click = self.add_component(Clickable)
        self.click.on_left_click = self.click_me
        self.transform.set_local_position((self.transform.local_position.x, self.transform.local_position.y, -10))
        self.count = 0
    def update(self, dt):
        self.count += dt
        self.transform.set_local_position((self.transform.local_position.x, self.transform.local_position.y, 10*math.sin(self.count)))

    def click_me(self):
        print("Clicked!")