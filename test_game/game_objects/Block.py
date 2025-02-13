from gamelib.network.syncs.game_objects.NetworkGameObject import NetworkGameObject
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
from gamelib.game.component.Sprite import Sprite
from gamelib.network.syncs.components.NetworkSprite import NetworkSprite
import pygame
class Block(NetworkGameObject):
    def __init__(self, name="Block", active=True, parent=None, network_id=None, steam_id=None, position=None, image_path=None):
        super().__init__(name, active, parent, network_id, steam_id)
        self.add_component(Sprite, image_path=image_path)
        self.add_component(NetworkSprite)
        self.network_manager = NetworkManager.get_instance()
        self.position = pygame.Vector2(position)
    def set_transform_position(self, size, final_position):
        self.transform.set_local_position(final_position.x * size, final_position.y * size)

    

# **ネットワーク同期可能なオブジェクトとして登録**
NetworkObjectFactory.register_class(Block)
