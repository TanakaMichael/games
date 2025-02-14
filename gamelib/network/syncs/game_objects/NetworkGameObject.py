from ....game.game_object.GameObject import GameObject
from ...NetworkManager import NetworkManager
from ..components.NetworkTransform import NetworkTransform
from ..components.NetworkComponent import NetworkComponent
from ...NetworkObjectFactory import NetworkObjectFactory

class NetworkGameObject(GameObject):
    def __init__(self, name="network_object", active=True, parent=None, network_id=None, steam_id=None):
        self.network_manager = NetworkManager.get_instance()
        
        if network_id is None:
            self.network_id = self.network_manager.net_id_generator.generate_id()
        else:
            self.network_id = network_id
        
        self.steam_id = steam_id
        self.initialized = False  # receive_messageが非同期のため
        super().__init__(name, active, parent)

        self.add_component(NetworkTransform)

        # **状態の変更をトラッキング**
        self._previous_active = self.active
        self._previous_steam_id = self.steam_id
        self._previous_layer = self.layer  # **layer の変更を監視**

    def end(self):
        super().end()
        self.initialized = False

    def start(self):
        super().start()
        self.initialized = True
        self.scene = self.network_manager.scene_manager.current_scene

    def get_network_components(self):
        """NetworkComponent を継承したコンポーネントのみ取得"""
        network_components = [comp for comp in self.components.values() if isinstance(comp, NetworkComponent)]
        return network_components


    def receive_message(self, message):
        """ネットワークメッセージを受信"""
        t = message.get("type")

        # **コンポーネントの同期処理**
        for component in self.get_network_components():
            component.receive_message(message)
        for child in self.children:
            if hasattr(child, "receive_message"):
                child.receive_message(message)

        # **オブジェクトの状態を同期**
        if t == "sync_network_object" and message.get("network_id") == self.network_id:
            self.active = message.get("active", self.active)
            self.steam_id = message.get("steam_id", self.steam_id)
            self.layer = message.get("layer", self.layer)  # **layer を同期**
            self.parent = self.network_manager.scene_manager.current_scene.get_network_object(message.get("parent_id"))

        # **強制同期メッセージを受信**
        if t == "force_sync_network_game_objects_components":
            self.force_sync()

        # **子オブジェクトの追加を受信**
        if t == "add_network_child" and message.get("parent_id") == self.network_id:
            self.handle_add_network_child(message)
        if t == "remove_network_child" and message.get("parent_id") == self.network_id:
            self.remove_network_child(message["network_id"])
        

    def force_sync(self):
        """強制的に全ネットワークコンポーネントを同期"""
        self.sync_state()  # **自身の同期情報も送信**
        for component in self.get_network_components():
            component.force_sync()
    
    def sync_state(self):
        """オブジェクトの状態を同期する"""
        parent_id = self.parent.network_id if self.parent else None
        sync_data = {
            "type": "sync_network_object",
            "network_id": self.network_id,
            "active": self.active,
            "steam_id": self.steam_id,
            "layer": self.layer,  # **layer を同期**
            "parent_id": parent_id
        }
        if self.network_manager.is_server:
            self.network_manager.broadcast(sync_data)

    def add_network_child(self, child, layer=None):
        """このオブジェクトに子オブジェクトを追加し、ネットワークに通知"""
        if not layer:
            layer = child.layer
        self.add_child(child, layer)
        self.sync_state()  # **親子関係が変わるため同期**
        data = {
            "type": "add_network_child",
            "parent_id": self.network_id,
            "child_id": child.network_id,
            "child_class": child.__class__.__name__,
            "child_name": child.name,
            "steam_id": child.steam_id,
            "layer":  layer # **子オブジェクトの layer も同期**
        }
        
        if self.network_manager.is_server:
            self.network_manager.broadcast(data)
        return child

    def remove_network_child(self, child):
        if isinstance(child, int):
            child = self.get_network_child(child)
        if child in self.children:
            self.children.remove(child)

            self.sync_state()  # **親子関係が変わるため同期**
            data = {
                "type": "remove_network_child",
                "network_id": child.network_id,
                "parent_id": self.network_id
            }
            if self.network_manager.is_server:
                self.network_manager.broadcast(data)
    def get_network_child(self, network_id):
        for child in self.children:
            if isinstance(child, NetworkGameObject):
                if child.network_id == network_id:
                    return child
    
    def handle_add_network_child(self, message):
        """ネットワーク経由で子オブジェクトを追加"""
        parent_id = message.get("parent_id")
        child_id = message.get("child_id")
        child_class_name = message.get("child_class")
        child_name = message.get("child_name")
        steam_id = message.get("steam_id")
        layer = message.get("layer")

        # **`NetworkObjectFactory` を使って子オブジェクトを生成**
        child_obj = NetworkObjectFactory.create_object(child_class_name, child_name, child_id, steam_id)

        if not child_obj:
            print(f"⚠️ Failed to create object {child_name} of type {child_class_name}")
            return

        # **親オブジェクトに子オブジェクトを追加**
        child_obj.layer = layer  # **layer を同期**
        self.add_child(child_obj)

        print(f"✅ Added child {child_name} ({child_id}) to parent {parent_id}")

    def update(self, dt):
        """毎フレーム実行: 状態の変化を監視し、必要なら同期"""
        super().update(dt)

        # **状態の変化を検知**
        if (
            self.active != self._previous_active or 
            self.steam_id != self._previous_steam_id or 
            self.layer != self._previous_layer  # **layer の変更をチェック**
        ):
            self.sync_state()  # **変更があったら同期**
            self._previous_active = self.active
            self._previous_steam_id = self.steam_id
            self._previous_layer = self.layer  # **layer の変更を記録**
