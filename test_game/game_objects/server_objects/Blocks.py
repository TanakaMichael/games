from gamelib.network.syncs.game_objects.NetworkGameObject import NetworkGameObject
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
import pygame
class Blocks(NetworkGameObject):
    def __init__(self, name="Block", active=True, parent=None, network_id=None, steam_id=None, size=20):
        super().__init__(name, active, parent, network_id, steam_id)
        self.network_manager = NetworkManager.get_instance()
        self.position = pygame.Vector2(5, 0)
        self.blocks = []
        self.rotate = 1
        self.size = size
        self.layer = 1

        self._size = size
        self._position = self.position.copy()
    
    def rotation(self):
        # 回転行列 -y, x (90)
        for block in self.blocks:
            x = -block.position.y
            y = block.position.x
            block.position.x = x
            block.position.y = y
    def move_left(self):
        """左に一マス移動"""
        self.position.x -= 1
    def move_right(self):
        """右に一マス移動"""
        self.position.x += 1
    def move_down(self):
        """下に一マス移動"""
        self.position.y += 1
    def update(self, dt):
        super().update(dt)
        for block in self.blocks:
            position = pygame.Vector2(self.position.x +block.position.x, self.position.y + block.position.y)
            block.set_transform_position(self.size ,position)
        if self.network_manager.is_server:
            if self._size != self.size:
                self._size = self.size
                self.network_manager.broadcast({"type": "size", "network_id": self.network_id, "value": self.size})
            if self._position.x != self.position.x:
                self._position.x = self.position.x
                self.network_manager.broadcast({"type": "position_x", "network_id": self.network_id, "value": self.position.x})
            if self._position.y != self.position.y:
                self._position.y = self.position.y
                self.network_manager.broadcast({"type": "position_y", "network_id": self.network_id, "value": self.position.y})
    def receive_message(self, message):
        # サイズ変更などに対応
        if message["type"] == "size" and message["network_id"] == self.network_id:
            self.size = message["value"]
        elif message["type"] == "position_x" and message["network_id"] == self.network_id:
            self.position.x = message["value"]
        elif message["type"] == "position_y" and message["network_id"] == self.network_id:
            self.position.y = message["value"]
        super().receive_message(message)

# **ネットワーク同期可能なオブジェクトとして登録**
NetworkObjectFactory.register_class(Blocks)
