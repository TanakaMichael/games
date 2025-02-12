import time
from .NetworkComponent import NetworkComponent
from ....game.component.Transform import Transform
from pygame import Vector2, Vector3

class NetworkTransform(NetworkComponent):
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object)
        self.transform = game_object.get_component(Transform)

        # 同期データの初期化
        self.last_synced_position = Vector3(self.transform.get_local_position())
        self.last_synced_scale = Vector2(self.transform.local_scale)
        self.last_synced_rotation = Vector3(self.transform.local_rotation)

        self.sync_interval = sync_interval  # 同期間隔 (秒)
        self.last_sync_time = time.time()

    def update(self, delta_time):
        current_time = time.time()

        if self.game_object.network_manager.is_server:
            if current_time - self.last_sync_time >= self.sync_interval:
                self.sync_if_needed()
                self.last_sync_time = current_time

    def sync_if_needed(self):
        # 現在の Transform 状態を取得
        position = self.transform.get_local_position()
        scale = self.transform.local_scale
        rotation = self.transform.local_rotation

        # 同期データの差分検出
        sync_data = {"type": "sync_transform", "network_id": self.game_object.network_id}

        if position != self.last_synced_position:
            sync_data["position"] = [position.x, position.y, position.z]
            self.last_synced_position = position

        if scale != self.last_synced_scale:
            sync_data["scale"] = [scale.x, scale.y]
            self.last_synced_scale = scale

        if rotation != self.last_synced_rotation:
            sync_data["rotation"] = [rotation.x, rotation.y, rotation.z]
            self.last_synced_rotation = rotation

        # 変更があればクライアントに送信
        if len(sync_data) > 2:  # "type" と "network_id" 以外のデータが含まれている場合
            self.game_object.network_manager.broadcast(sync_data)
    def force_sync(self):
        position = self.transform.get_local_position()
        scale = self.transform.local_scale
        rotation = self.transform.local_rotation

        force_sync_data = {
            "type": "sync_transform",
            "network_id": self.game_object.network_id,
            "position": [position.x, position.y, position.z],
            "scale": [scale.x, scale.y],
            "rotation": [rotation.x, rotation.y, rotation.z]
        }

        self.game_object.network_manager.broadcast(force_sync_data)

    def receive_network_data(self, message):
        """
        クライアント側で同期データを受信したときに呼び出される
        """
        if message.get("type") == "sync_transform" and message.get("network_id") == self.game_object.network_id:
            # 位置の更新
            if "position" in message:
                pos = message["position"]
                self.transform.set_local_position(Vector3(*pos))

            # スケールの更新
            if "scale" in message:
                scale = message["scale"]
                self.transform.set_local_scale(Vector2(*scale))

            # 回転の更新
            if "rotation" in message:
                rotation = message["rotation"]
                self.transform.set_local_rotation(Vector3(*rotation))

