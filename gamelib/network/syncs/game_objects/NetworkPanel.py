from ....game.game_object.Panel import Panel
from .NetworkGameObject import NetworkGameObject

class NetworkPanel(NetworkGameObject):
    def __init__(self, name, active=True, parent=None, network_id=None, steam_id=None):
        self.ui_objects = []
        super().__init__(name, active, parent, network_id, steam_id)


    def set_active(self, active):
        super().set_active(active)
        for ui in self.ui_objects:
            ui.set_active(active)
    def add_ui(self, ui):
        self.ui_objects.append(ui)
        self.canvas.add_ui(ui)
        ui.set_active(self.active)
        return ui

