from ..RectTransform import RectTransform
from ..UIObject import UIObject
from ..ui_elements.Rect import Rect
from ..ui_elements.Text import Text
from ..ui_elements.Image import Image
from .MeshButtonText import MeshButtonText
from ....game.InputManager import InputManager
import pygame
import copy
import time
class MeshList(UIObject):
    """クリック可能なリストUI"""
    def __init__(self, canvas, name="UIList", position = (0,0), rotation=0, item_data=None, item_size=(600, 50), max_visible_items=8
                 ,spacing=1, scroll_enabled=True, on_item_click=None, font_path=None, font_height=80, font_color=pygame.Color(255,255,255), ui_background=pygame.Color(30,30,30), 
                 alignment="center", correction_background_scale=pygame.Vector2(1.2,1.5), ui_button_background=pygame.Color(20,20,20)):
        rect = RectTransform(canvas, local_position=position, local_rotation=rotation)
        super().__init__(canvas=canvas, name=name, rect_transform=rect.clone())

        self.item_data = item_data if item_data else []
        if item_size:
            self.item_size = canvas._parse_position(item_size)
        else:
            self.item_size = (font_height * 5, font_height)
        
        self.max_visible_items = max_visible_items
        self.spacing = spacing
        self.scroll_enabled = scroll_enabled
        self.scroll_offset = 0
        self.scroll_cooldown_time = 0.1
        self.correction_background_scale = correction_background_scale

        self.alignment = alignment
        self.font_path = font_path
        self.font_height = font_height
        self.font_color = font_color
        self.on_item_click = on_item_click

        self.input_manager = InputManager.get_instance()
        self.scroll_up_action = self.input_manager.get_action("ScrollUp")
        self.scroll_down_action = self.input_manager.get_action("ScrollDown")

        self.item_buttons = []
        self.ui_button_background = ui_button_background
        self.init_ui(ui_background)
        self.create_list_items(self.item_data)
        self.rect_color = None


    def init_ui(self, ui_background):
        scale_x = self.item_size.x * self.correction_background_scale.x
        scale_y = (self.item_size.y * self.max_visible_items + self.max_visible_items * self.spacing) * self.correction_background_scale.y
        rect = RectTransform(canvas=self.canvas, local_position=(0,scale_y/2 - self.item_size.y/2 - self.spacing))
        if isinstance(ui_background, pygame.Color):
            self.rect_color = copy.copy(ui_background)
            self.ui_background = self.add_element(Rect(self.canvas, base_size=(scale_x, scale_y), rect_transform=rect.clone(), color=self.rect_color), -2)
        elif isinstance(ui_background, str):
            self.ui_background = self.add_element(Image(self.canvas, image_path=ui_background, base_size=(scale_x, scale_y), rect_transform=rect.clone()), -2)
        rect = RectTransform(canvas=self.canvas)
        if isinstance(self.ui_button_background, pygame.Color):
            self.ui_button_background = self.add_element(Rect(self.canvas, base_size=(self.item_size.x, self.item_size.y), rect_transform=rect.clone(), color=ui_background), -1)
        elif isinstance(self.ui_button_background, str):
            self.ui_button_background = self.add_element(Image(self.canvas, self.ui_button_background, base_size=(self.item_size.x, self.item_size.y), rect_transform=rect.clone()), -1)

    def create_list_items(self, item_data):
        """アイテムを生成する"""
        self.item_buttons.clear()
        self.clear_objects()

        for i, item in enumerate(item_data):
            # ** Textの検出
            if isinstance(item, Text):
                ui_text = item.clone()
            elif isinstance(item, str):
                rect = RectTransform(self.canvas, (0,0))
                ui_text = Text(self.canvas, item, self.font_path, self.font_height, self.font_color, rect.clone(), "right")
            # クリック時に on_item_click を呼び出す
            def create_on_click(index=i, value=ui_text.value):
                return lambda: self.handle_item_click(index, value)
            
            btn = MeshButtonText(
                canvas=self.canvas, 
                name=f"{self.name}_{i}",
                position=pygame.Vector2(0, 0),
                ui_text=ui_text,    
                ui_image=self.ui_button_background.clone(),
                fixed_background_size=self.item_size,
                font_alignment=self.alignment
            )
            btn.on_click = create_on_click()

            if i == 0:
                btn_spacing = 0
            else:
                prev_btn=self.item_buttons[-1]
                btn_spacing = (prev_btn.get_canvas_button_size().y / 2 + btn.get_canvas_button_size().y / 2) + self.spacing

            # **ボタンの位置を調整する
            btn.rect_transform.set_local_position(pygame.Vector2(0, btn_spacing * i))
            self.item_buttons.append(btn)
            self.add_object(btn)
        self.update_item_positions()
    def handle_item_click(self, index, item_text):
        """アイテムがクリックされたときに呼び出される"""
        if callable(self.on_item_click):
            self.on_item_click(index, item_text)
    def update_item_positions(self):
        """現在の `scroll_offset` に基づいて UI アイテムの位置を更新"""
        self.scroll_up(1)
        self.scroll_down(1)
        start_index = self.scroll_offset
        end_index = min(len(self.item_buttons), start_index + self.max_visible_items)

        y_offset = 0  # **Y座標のオフセットをリセット**

        for i, btn in enumerate(self.item_buttons):
            if start_index <= i < end_index:
                btn.visible = True
                btn.rect_transform.set_local_position(pygame.Vector2(0, y_offset))
                y_offset += btn.get_canvas_button_size().y + self.spacing
            else:
                btn.visible = False
    def update(self, delta_time):
        """リストの UI を更新"""
        super().update(delta_time)
        self.update_item_positions()

    def can_scroll(self):
        """スクロールできるか判定 (クールダウン考慮)"""
        current_time = time.time()
        if current_time - self.last_scroll_time >= self.scroll_cooldown_time:
            self.last_scroll_time = current_time
            return True
        return False
    def scroll_up(self, delta):
        """スクロールアップ"""
        if self.scroll_up_action.get_on_press():
            if self.scroll_enabled and self.scroll_offset > 0 and self.can_scroll():
                self.scroll_offset = max(0, self.scroll_offset - int(delta))
                self.update_item_positions()

    def scroll_down(self, delta):
        """スクロールダウン"""
        if self.scroll_down_action.get_on_press():
            if self.scroll_enabled and self.scroll_offset < len(self.item_buttons) - self.max_visible_items and self.can_scroll():
                self.scroll_offset = min(len(self.item_buttons) - self.max_visible_items, self.scroll_offset + int(abs(delta)))
                self.update_item_positions()

    def set_items(self, new_data):
        """リストのアイテムを更新"""
        self.item_data = new_data
        self.create_list_items(self.item_data)