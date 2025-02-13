from gamelib.network.syncs.game_objects.NetworkGameObject import NetworkGameObject
from .Blocks import Blocks
from ..Block import Block
from gamelib.game.component.Sprite import Sprite
import pygame
class TMino(Blocks):
    def __init__(self, name="Block", active=True, parent=None, network_id=None, steam_id=None):
        super().__init__(name, active, parent, network_id, steam_id)
        self.image_path = "TMino1.png"
        block1 = self.add_child(Block("Block1", parent=self, position=(-1, 0), image_path=self.image_path))
        block2 = self.add_child(Block("Block2", parent=self, position=(1, 0), image_path=self.image_path))
        block3 = self.add_child(Block("Block3", parent=self, position=(0, 1), image_path=self.image_path))
        mino = [block1, block2, block3]
        self.blocks.extend(mino)

        for block in self.blocks:
            sprite = block.get_component(Sprite)
            sprite.load_image(self.image_path)

