from .Component import Component

# spriteセットが条件
class Clickable(Component):
    def __init__(self, game_object):
        super().__init__(game_object)
        self.is_clicked = False
        if not hasattr(self, "on_left_click"): # クリックされたときのイベント
            self.on_left_click = lambda: None