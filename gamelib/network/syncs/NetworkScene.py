from ...game.core.Scene import Scene
from ...network.NetworkManager import NetworkManager
from ..NetworkObjectFactory import NetworkObjectFactory
from .game_objects.NetworkGameObject import NetworkGameObject

class NetworkScene(Scene):
    def __init__(self, name, screen):
        super().__init__(name, screen)
        self.network_manager = NetworkManager.get_instance()
    
    def add_network_object(self, network_object):
        """オブジェクトを追加し、サーバーならクライアントに通知"""
        self.objects.append(network_object)
        network_object.set_scene(self)

        if network_object.network_id is None:
            network_object.network_id = self.network_manager.net_id_generator.generate_id()

        if self.network_manager.is_server:
            self.broadcast_add_network_object(network_object)
        return network_object

    def remove_network_object(self, network_object):
        """オブジェクトを削除し、サーバーならクライアントにも通知"""
        if network_object in self.objects:
            # **子オブジェクトも削除する**
            children_to_remove = network_object.children[:]
            for child in children_to_remove:
                self.remove_network_object(child)  # **再帰的に削除**
            
            # **親の削除**
            self.objects.remove(network_object)
            
            if self.network_manager.is_server:
                self.broadcast_remove_network_object(network_object)


    def get_network_objects(self):
        """すべての `NetworkGameObject` を取得"""
        return [obj for obj in self.objects if isinstance(obj, NetworkGameObject)]

    def clear_network_objects(self):
        """すべての `NetworkGameObject` を削除"""
        for obj in self.get_network_objects()[:]:  # コピーを作成してループ
            self.remove_network_object(obj)

    def get_network_object(self, network_id):
        """`network_id` からオブジェクトを取得 (子オブジェクトも含めて再帰検索)"""
        if not network_id:
            return None

        # **ルートオブジェクトを検索**
        for obj in self.objects:
            if isinstance(obj, NetworkGameObject) and obj.network_id == network_id:
                return obj

            # **子オブジェクトも再帰的に検索**
            found = self._find_network_object_recursive(obj, network_id)
            if found:
                return found

        return None

    def _find_network_object_recursive(self, obj, network_id):
        """再帰的に `network_id` を持つオブジェクトを探す"""
        for child in obj.children:
            if isinstance(child, NetworkGameObject) and child.network_id == network_id:
                return child

            # **さらに深い子を探索**
            found = self._find_network_object_recursive(child, network_id)
            if found:
                return found

        return None


    def receive_message(self, message):
        """受信したメッセージを処理"""
        t = message.get("type")
        if t == "add_object":
            self.receive_add_object(message)
        elif t == "remove_object":
            self.remove_network_object(self.get_network_object(message["network_id"]))
        else:
            # **無駄なループを避ける**
            for obj in self.get_network_objects():
                obj.receive_message(message)
            
    def receive_add_object(self, message):
        """クライアント側: サーバーから受け取ったオブジェクトを追加"""
        obj = NetworkObjectFactory.create_object(
            message["class_name"],
            message["object_name"],
            message["network_id"],
            message["steam_id"],
        )

        if obj:
            parent_obj = self.get_network_object(message.get("parent_id"))
            if parent_obj:
                parent_obj.add_child(obj)  # **親子関係を適用**
                obj.set_parent(parent_obj)

            self.add_network_object(obj)

    def broadcast_add_network_object(self, network_object):
        """サーバーが全クライアントにオブジェクト追加を通知"""
        parent_id = network_object.parent.network_id if network_object.parent else None

        data = {
            "type": "add_object",
            "object_name": network_object.name,
            "network_id": network_object.network_id,
            "steam_id": network_object.steam_id,
            "class_name": network_object.__class__.__name__,
            "parent_id": parent_id,  # **親オブジェクトがある場合、その `network_id` を送信**
        }
        self.network_manager.broadcast(data)

    def broadcast_remove_network_object(self, network_object):
        """サーバーが全クライアントにオブジェクト削除を通知"""
        data = {
            "type": "remove_object",
            "network_id": network_object.network_id,
        }
        self.network_manager.broadcast(data)
