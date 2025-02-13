from ....game.game_object.GameObject import GameObject
from ...NetworkManager import NetworkManager
from ..components.NetworkTransform import NetworkTransform
from ..components.NetworkComponent import NetworkComponent

class NetworkGameObject(GameObject):
    def __init__(self, name="network_object", active=True, parent=None, network_id=None, steam_id=None):
        self.network_manager = NetworkManager.get_instance()
        
        if network_id is None:
            self.network_id = self.network_manager.net_id_generator.generate_id()
        else:
            self.network_id = network_id
        
        self.steam_id = steam_id
        # receive_messageが非同期のため、
        self.initialized = False
        name = name + f"_{self.network_id}"
        super().__init__(name, active, parent)

        self.add_component(NetworkTransform)

        # **状態の変更をトラッキングするための変数**
        self._previous_active = self.active
        self._previous_steam_id = self.steam_id
    def end(self):
        super().end()
        self.initialized = False
    def start(self):
        super().end()
        self.initialized = True

    def get_network_components(self):
        return [component for component in self.components if isinstance(component, NetworkComponent)]

    def receive_message(self, message):
        """ネットワークメッセージを受信"""
        t = message.get("type")

        # **コンポーネントの同期処理**
        for component in self.get_network_components():
            component.receive_message(message)

        # **強制同期メッセージを受信**
        if t == "force_sync_network_game_objects_components":
            self.force_sync()

    def force_sync(self):
        """強制的に全ネットワークコンポーネントを同期"""
        self.sync_state()  # **自身の同期情報も送信**
        for component in self.get_network_components():
            component.force_sync()
    
    def sync_state(self):
        """オブジェクトの状態 (active, steam_id) を同期する"""
        parent_id = None
        if self.parent:
            parent_id = self.parent.network_id
        sync_data = {
            "type": "sync_network_object",
            "network_id": self.network_id,
            "active": self.active,
            "steam_id": self.steam_id,
            "parent_id": parent_id
        }
        self.network_manager.broadcast(sync_data)  # **全クライアントに同期を送信**

    def update(self, dt):
        """毎フレーム実行: 状態の変化を監視し、必要なら同期"""
        super().update(dt)

        # **状態の変化を検知**
        if self.active != self._previous_active or self.steam_id != self._previous_steam_id:
            self.sync_state()  # **変更があったら同期**
            self._previous_active = self.active
            self._previous_steam_id = self.steam_id
