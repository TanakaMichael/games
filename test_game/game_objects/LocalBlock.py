from gamelib.network.syncs.game_objects.NetworkGameObject import NetworkGameObject, GameObject
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
from gamelib.game.component.Sprite import Sprite
from gamelib.network.syncs.components.NetworkSprite import NetworkSprite
import pygame
class LocalBlock(GameObject):
    def __init__(self, name="Block", active=True, parent=None, network_id=None, steam_id=None, position=None, image_path=None, is_wall=False, size=40):
        super().__init__(name, active, parent)
        self.sprite = self.add_component(Sprite, image_path=image_path, base_size=size)
        if position is not None:
            self.position = pygame.Vector2(position)
        self.is_wall = is_wall
        # 壁ではない => プレイヤーか、背景
        if not is_wall:
            self.layer = -1
        self._size = 0
    def set_transform_position(self, size, final_position):
        self.transform.set_local_position(pygame.Vector3(final_position.x * size, final_position.y * size, 0))
        if size != self._size:
            self._size = size
            self.sprite.apply_base_size((size, size))

