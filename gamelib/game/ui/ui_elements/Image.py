from ..UIElement import UIElement
from ..RectTransform import RectTransform
import pygame
class Image(UIElement):
    def __init__(self, canvas, image_path, base_size=None, rect_transform=None, color=(255,255,255,255)):
        if rect_transform is None:
            rect_transform = RectTransform(canvas, pygame.Vector2(0, 0), pygame.Vector2(1, 1))  # **デフォルト位置とサイズ**
        super().__init__(canvas, rect_transform=rect_transform)

        self.image_path = image_path
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.scaled_image = self.original_image.copy()
        self.final_image = self.scaled_image.copy()
        self.color = pygame.Color(color.r, color.g, color.b, color.a)  # **参照渡し防止**

        self.base_size = base_size if base_size else pygame.Vector2(self.original_image.get_size())  # **基準サイズ**
        self.screen_size = pygame.Vector2(self.base_size) # **スクリーンスケール**

        self._scale = None
        self._scale_factor = None

        # **初期スケール適用**
        self.apply_base_size()
        self.apply_color()
    def clone(self):
        return Image(self.cavnas, self.image_path, self.base_size, self.rect_transform.clone())

    def apply_base_size(self):
        """基準サイズ (`base_size`) に基づいて `original_image` をスケーリング"""
        self.original_image = pygame.transform.smoothscale(self.original_image, (int(self.base_size.x), int(self.base_size.y)))
    def set_scale_size(self, size):
        """transform.scaleを操作して目的のサイズにする"""
        scale_x = size.x/self.base_size.x
        scale_y = size.y/self.base_size.y

        self.rect_transform.set_local_scale((scale_x, scale_y))
    def set_image(self, image_path, size=None):
        if image_path == self.image_path:
            return # 同じ画像の場合は処理しない
        self.image_path = image_path
        self.original_image = pygame.image.load(image_path).convert_alpha()
        if size is not None:
            self.base_size = self.canvas._parse_position(size)
            self.original_image = pygame.transform.smoothscale(self.original_image, (int(size.x), int(size.y)))
        else:
            self.original_image = pygame.transform.smoothscale(self.original_image, (int(self.base_size.x), int(self.base_size.y)))
        

    def apply_color(self):
        """現在の `color` を適用"""
        if self.color:
            temp_image = self.original_image.copy()
            temp_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            self.original_image = temp_image
    def update(self):
        scale = self.rect_transform.get_render_scale()
        scale_factor = self.canvas.get_scale_factor()
        if (scale.x != self._scale.x or scale.y != self._scale.y) or (scale_factor.x != self._scale_factor.x or scale_factor.y != self._scale_factor.y):
            self.scaled_image = pygame.transform.smoothscale(self.original_image, (int(self.base_size.x*scale.x*scale_factor.x), int(self.base_size.y*scale.y*scale_factor.y)))
            self._scale = scale
            self._scale_factor = scale_factor
    def set_alpha(self, alpha):
        """画像の透明度を変更"""
        self.color.a = alpha


    def get_screen_size(self):
        return self.screen_size.copy()

    def render(self, screen):
        """画面にレンダリング"""
        pos = self.rect_transform.get_render_position()
        self.final_image = self.scaled_image.copy()
        self.final_image.set_alpha(self.color.a)
        rect = self.final_image.get_rect(center=(int(pos.x), int(pos.y)))
        self.screen_size = pygame.Vector2(self.final_image.get_size())
        screen.blit(self.final_image, rect)