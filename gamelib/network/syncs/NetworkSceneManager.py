from ...game.SceneManager import SceneManager
from ...network.syncs.NetworkScene import NetworkScene
from ..NetworkObjectFactory import NetworkObjectFactory
import json
from .NetworkScene import NetworkScene
class NetworkSceneManager(SceneManager):
    def __init__(self):
        super().__init__()
    def set_active_network_scene(self, scene_name):
        """scene変更と自動同期を図る"""
        # 変更先のsceneがNetworkSceneであることが条件

        scene = super().set_active_scene(scene_name)
        if scene and isinstance(scene, NetworkScene):
            # 条件を満たしている
            lobby_members = scene.network_manager.get_lobby_members()
            for members in lobby_members.keys():
                if members != scene.network_manager.server_steam_id:
                    self.send_network_scene_sync(scene.network_manager, members)

    def receive_network_scene_sync(self, nm, scene_data):
        """クライアント側でシーンを構築する"""
        self.set_active_scene(scene_data["scene_name"])
        self.current_scene.clear_network_objects()

        # **オブジェクト作成前に親子関係を辞書で紐付け**
        object_dict = {}  # `network_id` → `オブジェクト`
        parent_map = {}   # `network_id` → `parent_id`

        # **オブジェクトを先に生成して辞書に登録**
        for obj_data in scene_data["scene_data"]["objects"]:
            new_obj = NetworkObjectFactory.create_object(
                obj_data["class_name"],
                obj_data["object_name"],
                obj_data["network_id"],
                obj_data["steam_id"]
            )
            if new_obj:
                object_dict[obj_data["network_id"]] = new_obj
                parent_map[obj_data["network_id"]] = obj_data.get("parent_id")

        # **親子関係を適用**
        for child_id, parent_id in parent_map.items():
            if parent_id and parent_id in object_dict:
                parent_obj = object_dict[parent_id]
                child_obj = object_dict[child_id]
                parent_obj.add_child(child_obj)
                child_obj.set_parent(parent_obj)

        # **すべてのオブジェクトをシーンに追加**
        for obj in object_dict.values():
            self.current_scene.add_network_object(obj)

        # シーン開始
        self.start_scene()
        nm.complete_scene_sync = True  # 同期完了！
        nm.send_to_server({"type": "force_sync_network_game_objects_components"})

    # Serverオンリー
    def send_network_scene_sync(self, network_manager, target_client_id):
        """現在のシーンのデータを送信する (サーバー専用)"""
        if not isinstance(self.current_scene, NetworkScene):
            print("エラー: ネットワーク対応のシーンのみ送信可能")
            return False

        network_objects = self.current_scene.get_network_objects()

        scene_data = {
            "type": "scene_sync",
            "scene_name": self.current_scene.name,
            "scene_data": {
                "objects": [
                    {
                        "class_name": obj.__class__.__name__,
                        "object_name": obj.name,
                        "network_id": obj.network_id,
                        "steam_id": obj.steam_id,
                        "parent_id": obj.parent.network_id if obj.parent else None  # **親のネットワークIDを記録**
                    }
                    for obj in network_objects
                ]
            }
        }
        network_manager.send_to_client(target_client_id, scene_data)
        
    def request_scene_sync(self, network_manager):
        """シーン同期の要請をClient -> Serverでする"""
        network_manager.send_to_server({
                "type": "request_scene_sync", 
                "sender_id": network_manager.local_steam_id
            })

    def receive_message(self, network_manager, message):
        t = message.get("type")
        if t == "scene_sync":
            self.receive_network_scene_sync(network_manager, message)
        elif t == "request_scene_sync":
            self.send_network_scene_sync(network_manager, message["sender_id"])
        #sceneからは、循環が発生しないのでnetwork_managerを送信する
        if isinstance(self.current_scene, NetworkScene):
            self.current_scene.receive_message(message)
        
