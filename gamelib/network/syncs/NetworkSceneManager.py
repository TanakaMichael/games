from ...game.SceneManager import SceneManager
from ...network.syncs.NetworkScene import NetworkScene
from ..NetworkObjectFactory import NetworkObjectFactory
import json

class NetworkSceneManager(SceneManager):
    def __init__(self):
        super().__init__()

    def set_active_network_scene(self, scene_name):
        """シーン変更と自動同期"""
        scene = super().set_active_scene(scene_name)
        if scene and isinstance(scene, NetworkScene):
            lobby_members = scene.network_manager.get_lobby_members()
            for members in lobby_members.keys():
                if members != scene.network_manager.server_steam_id:
                    self.send_network_scene_sync(scene.network_manager, members)

    def receive_network_scene_sync(self, nm, scene_data):
        """クライアント側でシーンを構築"""
        self.set_active_scene(scene_data["scene_name"])
        self.current_scene.clear_network_objects()

        object_dict = {}  # `network_id` → `オブジェクト`
        parent_map = {}   # `network_id` → `parent_id`

        # **オブジェクトを先に生成し、辞書に登録**
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
        self._apply_parent_relationships(object_dict, parent_map)

        # **親を持たない（=最も浅い）オブジェクトのみシーンに追加**
        for obj_id, obj in object_dict.items():
            if parent_map[obj_id] is None:  # **親がいないオブジェクトだけ追加**
                self.current_scene.add_network_object(obj)

        # シーン開始
        self.start_objects()
        nm.complete_scene_sync = True
        nm.send_to_server({"type": "force_sync_network_game_objects_components"})

    def _apply_parent_relationships(self, object_dict, parent_map):
        """親子関係を適用"""
        for child_id, parent_id in parent_map.items():
            if parent_id and parent_id in object_dict:
                parent_obj = object_dict[parent_id]
                child_obj = object_dict[child_id]
                parent_obj.add_child(child_obj)
                child_obj.set_parent(parent_obj)

    def send_network_scene_sync(self, network_manager, target_client_id):
        """現在のシーンのデータを送信する (サーバー専用)"""
        if not isinstance(self.current_scene, NetworkScene):
            print("エラー: ネットワーク対応のシーンのみ送信可能")
            return False

        # **シリアライズ用のオブジェクトリスト**
        network_objects = self.current_scene.get_network_objects()
        serialized_objects = []

        for obj in network_objects:
            serialized_objects.extend(self._serialize_object_tree(obj))

        scene_data = {
            "type": "scene_sync",
            "scene_name": self.current_scene.name,
            "scene_data": {
                "objects": serialized_objects
            }
        }
        network_manager.send_to_client(target_client_id, scene_data)

    def _serialize_object_tree(self, obj):
        """オブジェクトとすべての子オブジェクトを再帰的にシリアライズ"""
        serialized_objects = []
        self._serialize_recursive(obj, serialized_objects, None)
        return serialized_objects

    def _serialize_recursive(self, obj, serialized_list, parent_id):
        """再帰的にオブジェクトをシリアライズ"""
        serialized_list.append({
            "class_name": obj.__class__.__name__,
            "object_name": obj.name,
            "network_id": obj.network_id,
            "steam_id": obj.steam_id,
            "parent_id": parent_id
        })
        for child in obj.children:
            self._serialize_recursive(child, serialized_list, obj.network_id)

    def request_scene_sync(self, network_manager):
        """シーン同期の要請をClient -> Serverでする"""
        network_manager.send_to_server({
            "type": "request_scene_sync",
            "sender_id": network_manager.local_steam_id
        })

    def receive_message(self, network_manager, message):
        """受信メッセージの処理"""
        t = message.get("type")
        if t == "scene_sync":
            self.receive_network_scene_sync(network_manager, message)
        elif t == "request_scene_sync":
            self.send_network_scene_sync(network_manager, message["sender_id"])
        elif t == "force_sync_network_game_objects_components":
            self.force_sync_objects(network_manager)

        else:
            if hasattr(self.current_scene, "receive_message"):
                self.current_scene.receive_message(message)

    def force_sync_objects(self, network_manager):
        """サーバーの NetworkGameObject と同期"""
        existing_ids = {obj.network_id for obj in self.current_scene.get_network_objects()}
        new_ids = set()

        for obj in self.current_scene.get_network_objects():
            new_ids.add(obj.network_id)
            obj.sync_state()

        # **クライアント側の不要なオブジェクトを削除**
        for extra_id in existing_ids - new_ids:
            obj = self.current_scene.get_network_object(extra_id)
            if obj:
                self.current_scene.remove_network_object(obj)
