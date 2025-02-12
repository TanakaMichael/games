class UIElement:
    def __init__(self, canvas, rect_transform=None, layer=0, visible=True):
        self.ui_object = None
        self.canvas = canvas
        self.rect_transform = rect_transform
        self.layer = layer
        self.visible = visible
    def _set_object(self, ui_object):
        self.ui_object = ui_object
    def update(self, delta_time):
        """更新処理（UIComponent も更新）"""
        self.rect_transform.update_transform()
    def render(self, screen):
        """描画処理"""
        pass
    def handle_event(self, event):
        pass