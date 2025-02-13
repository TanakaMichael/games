from .Component import Component
from .Transform import Transform
import pygame
class Sprite(Component):
    image_cache = {}
    def __init__(self, game_object, image_path=None, base_size=None):
        super().__init__(game_object)
        self.image_path = None
        self.base_size = pygame.Vector2(base_size) if base_size else None
        self.transform = game_object.get_component(Transform)

        self.original_image = None
        self.transformed_image = None

        self._last_scale = None
        self._last_rotation = None
        self._last_position = None

        self._final_width = None
        self._final_height = None
        if image_path:
            self.load_image(image_path)

    def load_image(self, path):
        """画像のロードとキャッシュ"""
        if path == self.image_path:
            return
        self.image_path = path
        if self.image_path not in Sprite.image_cache:
            Sprite.image_cache[self.image_path] = pygame.image.load(self.image_path).convert_alpha()
        self.original_image = Sprite.image_cache[self.image_path]
        if self.base_size:
            self.apply_base_size(self.base_size)
        else:
            # 画像の元サイズを基準にする
            self.base_size = pygame.Vector2(self.original_image.get_size())
        self.update_transform(force=True)
    def apply_base_size(self, base_size):
        """基準サイズを適用する"""
        self.base_size = pygame.Vector2(base_size)
        self.original_image = pygame.transform.scale(self.original_image, (int(self.base_size.x), int(self.base_size.y)))

    def update_transform(self, force=False):
        """Transform 情報に基づき、スケーリング・回転変換を更新（キャッシュ利用）"""
        current_scale = self.transform.get_global_scale()
        current_rotation = self.transform.get_global_rotation().z
        current_position = self.transform.get_global_position()
        if not force and (current_scale == self._last_scale and current_rotation == self._last_rotation and current_position == self._last_position):
            return

        self._last_scale = current_scale
        self._last_rotation = current_rotation
        self._last_position = current_position

        # 画像のスケーリング（base_size に対して global_scale を掛ける）
        scaled_width = int(self.base_size.x * current_scale.x)
        scaled_height = int(self.base_size.y * current_scale.y)
        scaled_image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
        # 回転（時計回りに反転）
        self.transformed_image = pygame.transform.rotate(scaled_image, -current_rotation)

    def render(self, surface, camera):
        """スプライトをレンダリング"""
        if not self.transformed_image:
            return
        self.update_transform()
        pos = self.transform.get_global_position()

        # 追加のスケーリングを行う
        lb_rect, lb_scale = camera.get_letterbox_rect_cached()
        final_position, final_scale = camera.world_to_screen(pos)
        final_width = int(self.transformed_image.get_width() * lb_scale.x * final_scale)
        final_height = int(self.transformed_image.get_height() * lb_scale.y * final_scale)
        if final_width != self._final_width or final_height != self._final_height:
            self.image_to_draw = pygame.transform.smoothscale(self.transformed_image, (final_width, final_height))
            self._final_width = final_width
            self._final_height = final_height
        rect = self.image_to_draw.get_rect(center=(int(final_position.x), int(final_position.y)))
        self.render_rect = rect  # クリック判定用に保持
        surface.blit(self.image_to_draw, rect)
        