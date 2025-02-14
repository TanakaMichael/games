import time
from .NetworkComponent import NetworkComponent
from ....game.component.Sprite import Sprite

class NetworkSprite(NetworkComponent):
    def __init__(self, game_object, sync_interval=0.1):
        super().__init__(game_object)
        self.sprite = game_object.get_component(Sprite)

        # 同期データの初期化
        self.last_synced_image_path = self.sprite.image_path
        self.last_synced_base_size = self.sprite.base_size
        self.last_synced_alpha = 255  # デフォルトは不透明

        self.sync_interval = sync_interval  # 同期間隔 (秒)
        self.last_sync_time = time.time()

    def update(self, delta_time):
        current_time = time.time()

        if self.game_object.network_manager.is_server:
            if current_time - self.last_sync_time >= self.sync_interval:
                self.sync_if_needed()
                self.last_sync_time = current_time

    def sync_if_needed(self):
        sync_data = {
            "type": "sync_sprite",
            "network_id": self.game_object.network_id
        }

        # 画像パスの同期
        if self.sprite.image_path != self.last_synced_image_path:
            sync_data["image_path"] = self.sprite.image_path
            self.last_synced_image_path = self.sprite.image_path

        # 基準サイズの同期
        if self.sprite.base_size != self.last_synced_base_size:
            sync_data["base_size"] = [self.sprite.base_size.x, self.sprite.base_size.y]
            self.last_synced_base_size = self.sprite.base_size

        # 透明度の同期（オプション）
        current_alpha = self.sprite.transformed_image.get_alpha() if self.sprite.transformed_image else 255
        if current_alpha != self.last_synced_alpha:
            sync_data["alpha"] = current_alpha
            self.last_synced_alpha = current_alpha

        # 差分がある場合のみ送信
        if len(sync_data) > 2:
            self.game_object.network_manager.broadcast(sync_data)
    def force_sync(self):
        """
        強制的にすべての同期データを送信
        """
        force_sync_data = {
            "type": "sync_sprite",
            "network_id": self.game_object.network_id,
            "image_path": self.sprite.image_path,
            "base_size": [self.sprite.base_size.x, self.sprite.base_size.y],
            "alpha": self.sprite.transformed_image.get_alpha() if self.sprite.transformed_image else 255
        }

        self.game_object.network_manager.broadcast(force_sync_data)

    def receive_message(self, message):
        """
        クライアント側で同期データを受信したときに呼び出される
        """
        if message.get("type") == "sync_sprite" and message.get("network_id") == self.game_object.network_id:
            # 画像パスの更新
            if "image_path" in message:
                self.sprite.load_image(message["image_path"])

            # 基準サイズの更新
            if "base_size" in message:
                self.sprite.apply_base_size(message["base_size"])

            # 透明度の更新
            if "alpha" in message:
                if self.sprite.transformed_image:
                    self.sprite.transformed_image.set_alpha(message["alpha"])
