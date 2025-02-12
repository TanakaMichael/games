from .GameObject import GameObject
# GameObjectを継承したUIGameObject

class Panel(GameObject):
    def __init__(self, canvas, name, active=False, parent=None):
        self.ui_objects = []
        super().__init__(name, active, parent)
        self.canvas = canvas
    def set_active(self, active):
        super().set_active(active)
        for ui in self.ui_objects:
            ui.set_active(active)
    def add_ui(self, ui):
        self.ui_objects.append(ui)
        self.canvas.add_ui(ui)
        ui.set_active(self.active)
        return ui
    
