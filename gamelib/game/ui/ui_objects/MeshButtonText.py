import pygame
import math
from ..UIObject import UIObject
from ..RectTransform import RectTransform
from ..ui_elements.Text import Text
from ..ui_elements.Rect import Rect
from ...InputManager import InputManager

class MeshButtonText(UIObject):
    def __init__(self, canvas, name, position, ui_text, ui_image=pygame.Color(30,30,30), rotation=0, 
                 correction_background_scale=pygame.Vector2(1.2,1.5), fixed_background_size=None, 
                 on_click=None, font_path=None, font_height=100, font_alignment="center"):
        
        rect = RectTransform(canvas=canvas, local_position=position, local_rotation=rotation)
        super().__init__(canvas, name, rect.clone())
        
        self.background_scale = canvas._parse_position(correction_background_scale)
        self.fixed_background_size = canvas._parse_position(fixed_background_size) if fixed_background_size else None
        self.font_path = font_path
        self.font_height = font_height
        self.on_click = on_click
        self.is_hovered = False
        self.is_pressed = False

        self.alignment = font_alignment
        self.init_ui_elements(canvas, ui_text, ui_image)
        self.inputManager = InputManager.get_instance()

        self.click_action = self.inputManager.get_action("MouseLeft")

        # コールバックの初期化（すでにメソッドが定義されている場合は上書きしない）
        if not hasattr(self, "on_pressed"):
            self.on_pressed = lambda: None
        if not hasattr(self, "on_pressed_hold"):
            self.on_pressed_hold = lambda: None
        if not hasattr(self, "on_released"):
            self.on_released = lambda: None
        if not hasattr(self, "on_hovered"):
            self.on_hovered = lambda: None
        if not hasattr(self, "on_normal"):
            self.on_normal = lambda: None

    def init_ui_elements(self, canvas, ui_text, ui_image):
        if isinstance(ui_image, pygame.Color):
            self.ui_image = self.add_element(Rect(canvas=canvas, color=ui_image), -1)
        else:
            self.ui_image = self.add_element(ui_image, -1)

        if isinstance(ui_text, str):
            rect = RectTransform(canvas, parent=self.rect_transform)
            if self.fixed_background_size:
                #固定の場合はtextの原点を固定して考える
                alignment = "right"
            else:
                alignment = "center"
            ui_text = Text(canvas, font_path=self.font_path or "KH-Dot-Dougenzaka-12.ttf", 
                               text=ui_text, rect_transform=rect.clone(), 
                               font_height=self.font_height, alignment=alignment)
        self.ui_text = self.add_element(ui_text)
    def get_canvas_button_size(self):
        """ボタンの最終的なキャンバス上のサイズ"""
        if self.fixed_background_size:
            return pygame.Vector2(self.fixed_background_size.x * self.background_scale.x, self.fixed_background_size.y * self.background_scale.y)

        # **Textのサイズを取得する
        text_canvas_size = self.ui_text.get_canvas_text_size()
        width = text_canvas_size.x * self.background_scale.x
        height = text_canvas_size.y * self.background_scale.y

        return pygame.Vector2(width,height)

    def update_background_size(self):
        if self.ui_image:
            # 背景サイズの決定
            size = self.get_canvas_button_size()

            self.ui_image.set_scale_size((size.x, size.y))

            # 背景位置の調整
            if self.fixed_background_size is None:
                # 自動調整の場合は、背景もテキストも常に親の重心（center）に合わせる

                self.ui_image.rect_transform.set_local_position(
                    self.ui_text.rect_transform.local_position
                )
            else:
                # 固定サイズの場合は、テキストのサイズを元に背景の位置をずらす
                # ui_text は常に親（self.rect_transform）の中心に配置されているので、
                # 背景をずらすことで、背景内でのテキストの見かけ上の位置を調整する
                text_width = self.ui_text.get_canvas_text_size().x
                if self.alignment == "center":
                    offset_x = 0
                elif self.alignment == "right":
                    # 「right」の場合、背景の実質的なアンカーが親に対して左側（＝背景を左にずらす）
                    # ずらす量はテキスト幅の半分
                    offset_x = self.fixed_background_size.x / 2 + -text_width / 2
                elif self.alignment == "left":
                    # 「left」の場合は背景を右にずらす
                    offset_x = -self.fixed_background_size.x / 2 + text_width / 2
                else:
                    offset_x = 0  # 万が一のときは center と同じ扱い

                self.ui_text.rect_transform.set_local_position(pygame.Vector2(offset_x, 0))



    def update(self, dt):
        super().update(dt)
        self.update_background_size()

        # **現在のマウス座標（キャンバス基準）**
        mouse_pos = self.canvas.to_canvas_position(*pygame.mouse.get_pos())

        # **ボタンの中心座標 & サイズ**
        button_size = self.get_canvas_button_size()
        button_pos = self.rect_transform.get_canvas_position()

        # **pygame.Rect を作成**
        button_rect = pygame.Rect(
            button_pos.x - button_size.x / 2,  # 左上X座標
            button_pos.y - button_size.y / 2,  # 左上Y座標
            button_size.x,  # 幅
            button_size.y   # 高さ
        )

        # **マウスがボタンの矩形内にあるか判定**
        was_hovered = self.is_hovered
        self.is_hovered = button_rect.collidepoint(mouse_pos.x, mouse_pos.y)

        # **ホバー状態の切り替え時にコールバック**
        if was_hovered and not self.is_hovered:
            self.on_normal()
            self.ui_image.set_alpha(255)
        elif self.is_hovered and not was_hovered:
            self.on_hovered()
            self.ui_image.set_alpha(128)

        # **押下時/長押し時のコールバック**
        if self.is_pressed:
            if self.click_action.get_on_hold():
                self.on_pressed_hold()

        self.input()


    def input(self):
        if self.click_action.get_on_press() and self.is_hovered:
            self.is_pressed = True
            self.on_pressed()

        if self.click_action.get_on_hold() and self.is_pressed and self.is_hovered:
            self.on_pressed_hold()

        if self.click_action.get_on_release():
            if self.is_pressed and self.is_hovered:
                if callable(self.on_click):
                    self.on_click()
                self.on_released()
            else:
                self.on_normal()
            self.is_pressed = False

    def render(self, screen):
        super().render(screen)
