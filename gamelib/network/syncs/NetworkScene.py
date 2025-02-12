from ...game.core.Scene import Scene
from ...network.NetworkManager import NetworkManager
from ..NetworkObjectFactory import NetworkObjectFactory
from .game_objects.NetworkGameObject import NetworkGameObject
class NetworkScene(Scene):
    def __init__(self, name, screen):
        super().__init__(name, screen)
        self.network_manager = NetworkManager.get_instance()
    
    def add_network_object(self, network_object):
        self.objects.append(network_object)
        # 基本はオブジェクトが生成されたとき自動でNetIDが振り分けられる
        if network_object.network_id is None:
            network_object.network_id = self.network_manager.net_id_generator.generate_id()
        if self.network_manager.is_server:
            # もしサーバーならclientにも生成内容を送る
            self.broadcast_add_network_object(network_object)
        return network_object
    def remove_network_object(self, network_object):
        self.objects.remove(network_object)
        if self.network_manager.is_server:
            # serverならclientにも削除を通知する
            self.broadcast_remove_network_object(network_object)

    def get_network_objects(self):
        """すべてのNetworkGameObjectを取得する"""
        return [ obj for obj in self.objects if isinstance(obj, NetworkGameObject) ]
    def clear_network_objects(self):
        """すべてのNetworkGameObjectを削除します"""
        for obj in self.get_network_objects()[:]:
            self.remove_network_object(obj)
    def get_network_object(self, network_id):
        """network_idからobjectを取得します。"""
        for obj in self.objects:
            if isinstance(obj, NetworkGameObject):
                if obj.network_id == network_id:
                    return obj
    



    def receive_message(self, message):
        t = message.get("type")
        if t == "add_object":
            self.receive_add_object(message)
        elif t == "remove_object":
            self.remove_object(message["network_id"])
        else:
            # 無駄な繰り返しを避ける
            for obj in self.get_network_objects():
                obj.receive_message(message)
            
    def receive_add_object(self, message):
        obj = NetworkObjectFactory.create_object(
            message["class_name"],
            message["object_name"],
            message["network_id"],
            message["steam_id"],
        )
        self.add_network_object(obj)




    
    def broadcast_add_network_object(self, network_object):
        """サーバーがclient全員にスポーン通知を送る"""
        data = {
            "type": "add_object",
            "object_name": network_object.name,
            "network_id": network_object.network_id,
            "steam_id": network_object.steam_id,
            "class_name": network_object.__class__.__name__
        }
        self.network_manager.broadcast(data)
    def broadcast_remove_network_object(self, network_object):
        """サーバーがclient全員にリムーブ通知をおくる"""
        data = {
            "type": "remove_object",
            "network_id": network_object.network_id,
        }
        self.network_manager.broadcast(data)