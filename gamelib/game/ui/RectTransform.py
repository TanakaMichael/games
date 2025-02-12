import pygame
import math

class RectTransform:
    """キャンバス内の UI のローカル & グローバル座標変換を管理 (スケール & 回転継承)"""
    def __init__(self, canvas, local_position=(0, 0), local_scale=(1, 1), local_rotation=0, parent=None):
        """
        :param canvas: 管理対象のキャンバス
        :param local_position: 親オブジェクト基準の相対座標 (数値または ('center', 'top') 形式のタプル)
        :param local_scale: 親基準のスケール
        :param local_rotation: 親基準の回転角度（度数法）
        :param parent: 親 `RectTransform`（オプション）
        """
        self.canvas = canvas
        self.parent = parent  # **親オブジェクト**
        self.local_position = self.canvas._parse_position(local_position)  # **親基準のローカル位置**
        self.local_scale = pygame.Vector2(local_scale)  # **親基準のスケール**
        self.local_rotation = local_rotation  # **親基準の回転角度**

        self.global_position = pygame.Vector2(0, 0)  # **キャンバス基準のグローバル座標**
        self.global_scale = pygame.Vector2(1, 1)  # **キャンバス基準のグローバルスケール**
        self.global_rotation = 0  # **キャンバス基準のグローバル回転**

        self.screen_position = pygame.Vector2(0, 0)  # **スクリーン描画用座標**
        
        self.update_transform()  # **初期化時に変換を適用**


    def update_transform(self):
        """グローバル座標, スケール, 回転を更新 (親の影響を受ける)"""
        if self.parent:
            # **親のスケールを継承**
            self.global_scale = pygame.Vector2(
                self.parent.global_scale.x * self.local_scale.x,
                self.parent.global_scale.y * self.local_scale.y
            )

            # **親の回転を継承**
            self.global_rotation = self.parent.global_rotation + self.local_rotation

            # **親の回転を考慮した位置補正**
            rotated_local_position = self._rotate_vector(self.local_position, self.parent.global_rotation)

            # **最終的なグローバル座標**
            self.global_position = self.parent.global_position + rotated_local_position
        else:
            self.global_position = self.local_position
            self.global_scale = self.local_scale
            self.global_rotation = self.local_rotation

        self.update_screen_transform()

    def update_screen_transform(self):
        """キャンバスのサイズに応じて `screen_position` を計算"""
        canvas_size = self.canvas.get_canvas_size()
        self.screen_position.x = (self.global_position.x / canvas_size[0]) * pygame.display.get_surface().get_width()
        self.screen_position.y = (self.global_position.y / canvas_size[1]) * pygame.display.get_surface().get_height()

    def set_local_position(self, new_local_position):
        """親オブジェクト基準のローカル位置を更新"""
        self.local_position = self.canvas._parse_position(new_local_position)
        self.update_transform()

    def set_global_position(self, new_global_position):
        """キャンバス内のグローバル位置を設定（親なしのオブジェクト向け）"""
        self.global_position = new_global_position
        self.local_position = new_global_position - (self.parent.global_position if self.parent else pygame.Vector2(0, 0))
        self.update_screen_transform()

    def set_parent(self, parent):
        """ `RectTransform` を設定"""
        self.parent = parent
        self.update_transform()

    def set_local_scale(self, new_local_scale):
        """親オブジェクト基準のスケールを更新"""
        self.local_scale = pygame.Vector2(new_local_scale)
        self.update_transform()

    def set_local_rotation(self, new_local_rotation):
        """親オブジェクト基準の回転を更新"""
        self.local_rotation = new_local_rotation
        self.update_transform()
    def get_global_position(self):
        """キャンバス内のグローバル位置を取得"""
        return self.global_position

    def get_render_position(self):
        """描画に使用するスクリーン座標を取得"""
        return self.screen_position

    def get_render_scale(self):
        """描画に使用するスケールを取得"""
        return self.global_scale

    def get_canvas_position(self):
        """キャンバス内でのグローバル位置を取得"""
        return self.global_position

    def get_render_rotation(self):
        """描画に使用する回転を取得"""
        return self.global_rotation

    def _rotate_vector(self, vector, angle_deg):
        """ベクトルを指定した角度 (度数法) だけ回転"""
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return pygame.Vector2(
            vector.x * cos_a - vector.y * sin_a,
            vector.x * sin_a + vector.y * cos_a
        )
    def clone(self):
        """このオブジェクトの複製を生成"""
        return RectTransform(
            self.canvas,
            local_position=self.local_position,
            local_scale=self.local_scale,
            local_rotation=self.local_rotation,
            parent=self.parent
        )
    
    