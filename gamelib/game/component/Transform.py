import pygame
import math
from .Component import Component

class Transform(Component):
    """
    位置、スケール、回転を管理する Transform コンポーネント。
    - position: pygame.Vector2
    - scale: pygame.Vector2
    - rotation: pygame.Vector3 (2Dゲームの場合は rotation.z を回転角に使うことが多い)
    """
    def __init__(self, game_object, local_position=(0, 0, 0), local_scale=(1, 1), local_rotation=(0, 0, 0), parent=None):
        super().__init__(game_object)
        self.parent = parent
        self.local_position = pygame.Vector3(local_position)
        self.local_scale = pygame.Vector2(local_scale)
        self.local_rotation = pygame.Vector3(local_rotation)  # 2Dゲームでは z成分を使用

        self.global_position = pygame.Vector3(0, 0, 0)
        self.global_scale = pygame.Vector2(1,1)
        self.global_rotation = pygame.Vector3(0, 0, 0)

        self.screen_position = pygame.Vector2(0, 0)
    def update_transform(self):
        """現在の位置をlocalからglobalに更新する"""
        if self.parent:
            self.global_scale = pygame.Vector2(self.parent.global_scale.x * self.local_scale.x, self.parent.global_scale.y * self.local_scale.y)
            self.global_rotation = self.parent.global_rotation + self.local_rotation
            rotated_local_position = self._rotate_vector(self.local_position, self.parent.global_rotation)
            self.global_position.x = self.parent.global_position.x + rotated_local_position.x
            self.global_position.y = self.parent.global_position.y + rotated_local_position.y
            self.global_position.z = self.parent.global_position.z
        else:
            self.global_position = self.local_position
            self.global_scale = self.local_scale
            self.global_rotation = self.local_rotation
    def update_screen_transform(self, camera):
        """カメラの描写範囲を基準にスクリーントランスフォームを更新"""
        self.screen_position = camera.world_to_screen(self.global_position)
    def set_local_position(self, new_local_position):
        """親オブジェクト基準のローカル位置を更新"""
        if isinstance(new_local_position, pygame.Vector2):
            self.local_position = pygame.Vector3(new_local_position.x, new_local_position.y, self.local_position.z)
        else:
            self.local_position = pygame.Vector3(new_local_position)
        self.update_transform()
    def set_local_scale(self, new_local_scale):
        """親オブジェクト基準のスケールを更新"""
        self.local_scale = pygame.Vector2(new_local_scale)
        self.update_transform()
    def set_local_rotation(self, new_local_rotation):
        """親オブジェクト基準の回転を更新"""
        self.local_rotation = pygame.Vector3(new_local_rotation)
        self.update_transform()

    def get_local_position(self):
        """ローカル位置を取得"""
        return self.local_position

    def get_global_position(self):
        """グローバル位置を取得"""
        return self.global_position

    def get_global_scale(self):
        """グローバルスケールを取得"""
        return self.global_scale
    def get_global_rotation(self):
        """グローバル回��を取得"""
        return self.global_rotation
    def set_parent(self, parent):
        """ `RectTransform` を設定"""
        self.parent = parent
        self.update_transform()
    def get_render_position(self):
        """描画に使用するスクリーン座標を取得"""
        return self.screen_position

    def get_render_scale(self):
        """描画に使用するスケールを取得"""
        return self.global_scale
    def get_render_rotation(self):
        """描画に使用する回転を取得"""
        return self.global_rotation
    def _rotate_vector(self, vector, angle_deg):
        """ベクトルを指定した角度 (度数法) だけ回転"""
        if isinstance(angle_deg, pygame.Vector3):
            angle_deg = angle_deg.z
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return pygame.Vector2(
            vector.x * cos_a - vector.y * sin_a,
            vector.x * sin_a + vector.y * cos_a
        )
    def clone(self):
        """このオブジェクトの複製を生成"""
        return Transform(
            self.canvas,
            local_position=self.local_position,
            local_scale=self.local_scale,
            local_rotation=self.local_rotation,
            parent=self.parent
        )