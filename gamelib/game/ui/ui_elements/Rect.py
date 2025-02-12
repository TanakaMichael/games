from ..UIElement import UIElement
from ..RectTransform import RectTransform
import pygame
import copy

class Rect(UIElement):
    def __init__(self, canvas, base_size=None, rect_transform=None, color=(255,255,255,255)):
        if rect_transform is None:
            rect_transform = RectTransform(canvas, pygame.Vector2(0, 0), pygame.Vector2(1, 1))  # **デフォルトの位置とサイズ**
        super().__init__(canvas, rect_transform=rect_transform)
        self.base_size = canvas._parse_position(base_size) if base_size else pygame.Vector2(100, 50)  # **デフォルトサイズ**
        self.scaled_size = self.base_size.copy()
        self.color = pygame.Color(color)
        
        rotated_rect = pygame.Surface((self.base_size.x, self.base_size.y), pygame.SRCALPHA)
        rotated_rect.fill(self.color)
        self.transformed_surface = pygame.transform.rotate(rotated_rect, -self.rect_transform.global_rotation)
        self._current_rotation = None
        self._final_width = None
        self._final_height = None
        self._color_a = copy.copy(self.color.a)
    def clone(self):
        return Rect(self.canvas, self.base_size, self.rect_transform.clone(), self.color)

    def update(self, dt):
        current_rotation=self.rect_transform.global_rotation
        current_scale=self.rect_transform.global_scale
        scale_factor = self.canvas.get_scale_factor()

        final_width = max(1, int(self.base_size.x * current_scale.x * scale_factor.x))
        final_height = max(1, int(self.base_size.y * current_scale.y * scale_factor.y))
        if current_rotation!=self._current_rotation or final_width!=self._final_width or final_height!=self._final_height or self.color.a != self._color_a:
            # **回転後の矩形サイズを取得**
            angle = -current_rotation  # pygame の座標系は時計回り
            rotated_rect = pygame.Surface((final_width, final_height), pygame.SRCALPHA)
            rotated_rect.fill(self.color)
            self.transformed_surface = pygame.transform.rotate(rotated_rect, angle)
            self.transformed_surface.set_alpha(self.color.a)
            self._current_rotation = current_rotation
            self._final_width = final_width
            self._final_height = final_height
            self._color_a = copy.copy(self.color.a)
    def set_alpha(self, alpha):
        self.color.a = alpha
    def set_scale_size(self, size):
        """transform.scaleを操作して目的のサイズにする"""
        size = pygame.Vector2(size)
        scale_x = size.x/self.base_size.x
        scale_y = size.y/self.base_size.y

        self.rect_transform.set_local_scale((scale_x, scale_y))

    def render(self, screen):
        pos = self.rect_transform.get_render_position()
        rect = self.transformed_surface.get_rect(center=(int(pos.x), int(pos.y)))
        screen.blit(self.transformed_surface, rect)
