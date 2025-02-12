from ..UIElement import UIElement
from ..RectTransform import RectTransform
from ..UIObject import UIObject

from ..ui_elements.Text import Text
import pygame
class MeshText(UIObject):
    def __init__(self, canvas, name="MeshText", font_path=None, text="", font_height=100, font_color=pygame.Color(255,255,255), position=pygame.Vector2(0,0),
                 rotation=0, visible=True, alignment="center"):
        rect = RectTransform(canvas=canvas, local_position=position, local_rotation=rotation)
        super().__init__(canvas, name, rect, visible)
        local_rect = RectTransform(canvas=canvas, local_position=pygame.Vector2(0,0), local_rotation=rotation)
        self.text = self.add_element(Text(canvas, text, font_path, font_height, font_color, local_rect, alignment))
    def set_text(self, text):
        self.text.set_text(text)
    def get_text(self):
        return self.text.text
    def add_text(self, text):
        self.text.text += text
        self.text.set_text(self.text.text)
    def get_canvas_size(self):
        self.text.get_canvas_text_size()