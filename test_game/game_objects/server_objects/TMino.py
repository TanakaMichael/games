from gamelib.network.syncs.game_objects.NetworkGameObject import NetworkGameObject
from .Blocks import Blocks
from ..Block import Block
from gamelib.game.component.Sprite import Sprite
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
import pygame
class TMino(Blocks):
    def __init__(self, name="Block", active=True, parent=None, network_id=None, steam_id=None, size=40):
        super().__init__(name, active, parent, network_id, steam_id, size)
        self.image_path = "TMino1.png"
        block1 = self.add_network_child(Block("Block1", parent=self, position=(-1, 0), image_path=self.image_path, size=size))
        block2 = self.add_network_child(Block("Block2", parent=self, position=(1, 0), image_path=self.image_path, size=size))
        block3 = self.add_network_child(Block("Block3", parent=self, position=(0, 1), image_path=self.image_path, size=size))
        block4 = self.add_network_child(Block("Block4", parent=self, position=(0, 0), image_path=self.image_path, size=size))
        mino = [block1, block2, block3, block4]
        self.blocks.extend(mino)

        for block in self.blocks:
            sprite = block.get_component(Sprite)
            sprite.load_image(self.image_path)

NetworkObjectFactory.register_class(TMino)
