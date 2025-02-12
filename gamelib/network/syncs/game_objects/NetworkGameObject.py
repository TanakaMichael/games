from ....game.game_object.GameObject import GameObject
from ...NetworkManager import NetworkManager
from ..components.NetworkTransform import NetworkTransform
from ..components.NetworkComponent import NetworkComponent
class NetworkGameObject(GameObject):
    def __init__(self, name="network_object", active=True, parent=None):
        self.network_manager = NetworkManager.get_instance()
        self.network_id = self.network_manager.net_id_generator.generate_id()
        self.steam_id = None
        name = name + f"_{self.network_id}"
        super().__init__(name, active, parent)

        self.add_component(NetworkTransform, )
    def get_network_components(self):
        [component for component in self.components if isinstance(component, NetworkComponent)]
    def receive_message(self, message):
        # コンポーネント更新
        t = message.get("type")
        for component in self.get_network_components():
            component.receive_message(message)
        if t == "force_sync_network_game_objects_components":
             for component in self.get_network_components():
                component.force_sync(message)