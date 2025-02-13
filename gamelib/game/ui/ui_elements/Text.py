import pygame
import math
from ..UIElement import UIElement
from ..RectTransform import RectTransform

class Text(UIElement):
    def __init__(self, canvas, text, font_path, font_height, color=(255, 255, 255),
                 rect_transform=None, alignment="center"):
        if rect_transform is None:
            rect_transform = RectTransform(canvas, pygame.Vector2(0, 0), pygame.Vector2(1, 1))
        super().__init__(canvas, rect_transform=rect_transform)
        
        self.text = text
        self.font_path = font_path
        self.font_height = font_height
        self.font_color = pygame.Color(color)
        self.alignment = alignment.lower()

        self.font = None
        self.rendered_text = None
        self.rotated_text = None
        self.char_colors = {}  # 文字ごとの色を保存する辞書 {index: color}
        self.canvas_text_size = pygame.Vector2(0, 0)
        self.color = color
        self.create_font()
        self.set_text(self.text)
        self.set_color(color)

    def clone(self):
        return Text(self.canvas, self.text, self.font_path, self.font_height, self.color, self.rect_transform.clone(), self.alignment)

    def create_font(self):
        """キャンバスとウィンドウのスケールに基づいてフォントを作成"""
        canvas_height = self.canvas.get_canvas_size()[1]
        window_height = pygame.display.get_surface().get_height()
        scale_factor = window_height / canvas_height

        try:
            scaled_font_height = int(self.font_height * scale_factor)
            self.font = pygame.font.Font(self.font_path, scaled_font_height)
        except FileNotFoundError:
            print(f"Font file '{self.font_path}' は見つかりません。デフォルトフォントを使用します。")
            self.font = pygame.font.SysFont(None, self.font_height)

    def set_text(self, text):
        """テキストを更新する"""
        self.value = text
        self.char_colors = {}  # テキストが変更された場合、色設定をリセット

        # 描画用のテキスト Surface
        self.rendered_text = self.font.render(self.value, True, self.font_color)
        angle = -self.rect_transform.global_rotation
        self.rotated_text = pygame.transform.rotate(self.rendered_text, angle)

        # **テキストサイズの取得**
        size = self.get_text_size()

        # **キャンバススケール計算**
        canvas_size = self.canvas.get_canvas_size()
        screen_size = pygame.display.get_surface().get_size()
        scale_x = canvas_size[0] / screen_size[0]
        scale_y = canvas_size[1] / screen_size[1]

        # **キャンバス上のサイズを設定**
        self.canvas_text_size = pygame.Vector2(size.x * scale_x, size.y * scale_y)

        # **テキストの配置を調整**
        if self.alignment == "right":
            self.rect_transform.set_local_position((size.x / 2, 0))
        elif self.alignment == "left":
            self.rect_transform.set_local_position((-size.x / 2, 0))
        else:
            self.rect_transform.set_local_position((0, 0))

    def set_alpha(self, alpha):
        self.font_color.a = alpha
        self.set_text(self.value)

    def set_color(self, color, start=None, length=None):
        """テキストの部分ごとに色を設定できる"""
        if start is None or length is None:
            self.font_color = pygame.Color(color)
            self.set_text(self.value)
        else:
            for i in range(start, min(start + length, len(self.value))):
                self.char_colors[i] = pygame.Color(color)

    def get_text_size(self):
        """テキスト全体のサイズを取得"""
        if self.font:
            text_width, text_height = self.font.size(self.value)
            return pygame.Vector2(text_width, text_height)
        return pygame.Vector2(0, 0)

    def get_canvas_text_size(self):
        """キャンバス基準のテキストサイズを取得"""
        return self.canvas_text_size

    def render(self, screen):
        if self.visible and self.font:
            pos = self.rect_transform.get_render_position()
            total_width, total_height = self.font.size(self.value)

            # alignment に応じた開始位置の調整（中心の場合）
            if self.alignment == "center":
                start_x = pos.x - total_width / 2
            elif self.alignment == "right":
                start_x = pos.x - total_width / 2
            else:  # "left"
                start_x = pos.x + total_width / 2

            # ピボットとしてテキストの中心位置を設定（ここでは pos を使用）
            pivot = pygame.Vector2(pos.x, pos.y)

            current_x = start_x
            for i, char in enumerate(self.value):
                color = self.char_colors.get(i, self.font_color)
                char_surface = self.font.render(char, True, color)
                # 回転角度（degree）
                angle = -self.rect_transform.global_rotation
                rotated_char = pygame.transform.rotate(char_surface, -angle/2)

                char_width = char_surface.get_width()
                char_height = char_surface.get_height()

                # 各文字の元の位置（文字を垂直方向中央揃え）
                original_x = current_x
                original_y = pos.y - char_height / 2

                # ピボットを基準にした相対座標を求める
                rel_x = original_x - pivot.x
                rel_y = original_y - pivot.y

                # 回転行列で相対座標を回転させる
                rotated_rel_x, rotated_rel_y = rotate_point(rel_x, rel_y, angle/2)

                # 最終的なスクリーン上の位置
                final_x = pivot.x + rotated_rel_x
                final_y = pivot.y + rotated_rel_y

                char_rect = rotated_char.get_rect()
                char_rect.topleft = (final_x, final_y)
                screen.blit(rotated_char, char_rect)

                current_x += char_width


    def handle_event(self, event):
        """ウィンドウサイズ変更時にテキストサイズを調整"""
        if event.type == pygame.VIDEORESIZE:
            self.set_text(self.value)
def rotate_point(x, y, angle):
    """原点 (0,0) を基準に (x, y) を `angle` 度回転させた座標を返す"""
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    return new_x, new_y