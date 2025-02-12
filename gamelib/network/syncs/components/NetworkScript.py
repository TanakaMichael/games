from .NetworkComponent import NetworkComponent
class NetworkScript(NetworkComponent):
    def __init__(self, game_object):
        self.game_object = game_object
        self.network_manager = game_object.network_manager

        if self.network_manager.is_server:
            self.on_server_start()
        elif self.network_manager.is_client:
            self.on_client_start()

    def update(self, delta_time):
        """フレームごとの更新処理"""
        if self.network_manager.is_server:
            self.on_server_update(delta_time)
        elif self.network_manager.is_client:
            self.on_client_update(delta_time)

    # -------------------------------
    # サーバー専用メソッド
    # -------------------------------
    def on_server_start(self):
        """サーバーでのみ実行される初期化処理"""
        pass

    def on_server_update(self, delta_time):
        """サーバーでのみ実行される更新処理"""
        pass

    def send_to_client(self, client_id, command, data):
        """クライアントにデータを送信"""
        message = {
            "type": "NETWORK_SCRIPT",
            "network_id": self.game_object.network_id,
            "command": command,
            "data": data
        }
        self.network_manager.send_to_client(client_id, message)

    # -------------------------------
    # クライアント専用メソッド
    # -------------------------------
    def on_client_start(self):
        """クライアントでのみ実行される初期化処理"""
        pass

    def on_client_update(self, delta_time):
        """クライアントでのみ実行される更新処理"""
        pass

    def send_to_server(self, command, data):
        """サーバーにデータを送信"""
        message = {
            "type": "NETWORK_SCRIPT",
            "network_id": self.game_object.network_id,
            "command": command, # 実行するメソッド
            "data": data
        }
        self.network_manager.send_to_server(message)

    # -------------------------------
    # ネットワークデータ受信処理
    # -------------------------------
    def receive_network_data(self, message):
        if message.get("type") == "NETWORK_SCRIPT" and message.get("network_id") == self.game_object.network_id:
            command = message.get("command")
            data = message.get("data")

            # コマンドハンドリング
            self.handle_command(command, data)

    def handle_command(self, command, data):
        """クライアント/サーバーで共通のコマンド処理"""
        handler_name = f"on_{command}"
        if hasattr(self, handler_name):
            getattr(self, handler_name)(data)
        else:
            print(f"⚠️ 未対応のコマンド: {command}")
