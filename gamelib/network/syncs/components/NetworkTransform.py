import time
from .NetworkComponent import NetworkComponent
from ....game.component.Transform import Transform
from pygame import Vector2, Vector3

class NetworkTransform(NetworkComponent):
    def __init__(self, game_object, sync_interval=0.05):
        super().__init__(game_object)
        self.transform = game_object.get_component(Transform)

        # 同期データの初期化
        self._last_synced_position = Vector3(self.transform.get_local_position())
        self._last_synced_scale = Vector2(self.transform.local_scale)
        self._last_synced_rotation = Vector3(self.transform.local_rotation)

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

        # 位置の変更を検出して送信
        if position.x != self._last_synced_position.x:
            sync_data["position_x"] = position.x
            self._last_synced_position.x = position.x

        if position.y != self._last_synced_position.y:
            sync_data["position_y"] = position.y
            self._last_synced_position.y = position.y

        if position.z != self._last_synced_position.z:
            sync_data["position_z"] = position.z
            self._last_synced_position.z = position.z

        # スケールの変更を検出して送信
        if scale.x != self._last_synced_scale.x:
            sync_data["scale_x"] = scale.x
            self._last_synced_scale.x = scale.x

        if scale.y != self._last_synced_scale.y:
            sync_data["scale_y"] = scale.y
            self._last_synced_scale.y = scale.y

        # 回転の変更を検出して送信
        if rotation.x != self._last_synced_rotation.x:
            sync_data["rotation_x"] = rotation.x
            self._last_synced_rotation.x = rotation.x

        if rotation.y != self._last_synced_rotation.y:
            sync_data["rotation_y"] = rotation.y
            self._last_synced_rotation.y = rotation.y

        if rotation.z != self._last_synced_rotation.z:
            sync_data["rotation_z"] = rotation.z
            self._last_synced_rotation.z = rotation.z

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
            "position_x": position.x,
            "position_y": position.y,
            "position_z": position.z,
            "scale_x": scale.x,
            "scale_y": scale.y,
            "rotation_x": rotation.x,
            "rotation_y": rotation.y,
            "rotation_z": rotation.z
        }

        self.game_object.network_manager.broadcast(force_sync_data)

    def receive_message(self, message):
        """
        クライアント側で同期データを受信したときに呼び出される
        """
        if message.get("type") == "sync_transform" and message.get("network_id") == self.game_object.network_id:
            # 位置の更新
            if "position_x" in message:
                self.transform.set_local_position(Vector3(message["position_x"], self.transform.local_position.y, self.transform.local_position.z))

            if "position_y" in message:
                self.transform.set_local_position(Vector3(self.transform.local_position.x, message["position_y"], self.transform.local_position.z))

            if "position_z" in message:
                self.transform.set_local_position(Vector3(self.transform.local_position.x, self.transform.local_position.y, message["position_z"]))

            # スケールの更新
            if "scale_x" in message:
                self.transform.set_local_scale(Vector2(message["scale_x"], self.transform.local_scale.y))

            if "scale_y" in message:
                self.transform.set_local_scale(Vector2(self.transform.local_scale.x, message["scale_y"]))

            # 回転の更新
            if "rotation_x" in message:
                self.transform.set_local_rotation(Vector3(message["rotation_x"], self.transform.local_rotation.y, self.transform.local_rotation.z))

            if "rotation_y" in message:
                self.transform.set_local_rotation(Vector3(self.transform.local_rotation.x, message["rotation_y"], self.transform.local_rotation.z))

            if "rotation_z" in message:
                self.transform.set_local_rotation(Vector3(self.transform.local_rotation.x, self.transform.local_rotation.y, message["rotation_z"]))
