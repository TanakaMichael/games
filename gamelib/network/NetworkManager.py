import ctypes
import time
import threading
from .SteamNetworking import SteamNetworking
from ..game.utility.Global import Global
from .utility.Communication import Communication
from .utility.MissingObject import MissingObjectManager
from .utility.NetIDGenerator import NetIDGenerator
from .utility.PingMeter import PingMeter

from .SetupServer import SetupServer
from .SetupClient import SetupClient
class NetworkManager(Global):
    
    def __init__(self):
        if NetworkManager._instance is not None:
            raise Exception("NetworkManager is a singleton!")
        self.steam = SteamNetworking()
        super().__init__()
        # 何かしらのサーバーに接続されている
        self.connected = False
        self.running = False
        self.complete_scene_sync = False

        self.lobby_id = 0
        # サーバー主のID
        self.server_steam_id = 0
        # 自身のID
        self.local_steam_id = self.steam.steam_id
        self.is_server = None
        self.is_client = None

        self.thread_running = threading.Event()  # イベントでスレッド制御
        self.threads = []  # スレッド管理リスト

        self.lobby_members = {}

        # singleton(循環防止)
        self.lock = threading.Lock()
        # 各機能クラスの初期化
        self.communication = Communication(self)
        # 各拡張機能(component)を初期化
        self.ping_meter = PingMeter(self)
        self.net_id_generator = NetIDGenerator(self)
        self.missing_object_manager = MissingObjectManager(self)

        self.components = [self.ping_meter, self.net_id_generator, self.missing_object_manager]

        # セットアップ用のクラス
        self.server_setup = SetupServer(self)
        self.client_setup = SetupClient(self)
    def set_singleton(self, scene_manager, global_event_manager):
        self.global_event_manager = global_event_manager
        self.scene_manager = scene_manager

    def setup_server(self, dis, max_p):
        # 生成ミスがあった場合Falseを返す
        return self.server_setup.run(dis, max_p)
    def setup_client(self, lobby_id):
        self.client_setup.run(lobby_id)

    # ------------------------
    # メッセージ送受信
    # ------------------------
    def send_to_client(self, client_id, message):
        if self.is_server:
            self.steam.accept_p2p_session(client_id)
            self.communication.send_message(client_id, message)

    def send_to_server(self, message):
        if self.is_client:
            self.steam.accept_p2p_session(self.server_steam_id)
            self.communication.send_message(self.server_steam_id, message)

    def broadcast(self, message):
        for client_id in self.lobby_members.keys():
            if client_id != self.server_steam_id:
                self.send_to_client(client_id, message)

    def process_received_message(self, message):
        for component in self.components:
            if hasattr(component, "receive_message"):
                component.receive_message(message)

        self.scene_manager.receive_message(self, message)
        

    def _receive_messages(self):
        while self.running:
            raw_data, sender_id = self.steam.receive_p2p_message()

            if raw_data:
                message = self.communication.receive_message(raw_data.encode('utf-8'))
                if message:
                    with self.lock:
                        self.process_received_message(message, sender_id)

            time.sleep(0.01)
    def start_thread(self, target):
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        self.threads.append(thread)

    def stop_all_threads(self):
        print("🛑 すべてのスレッドを停止します...")
        self.running.clear()

        current_thread = threading.current_thread()  # 🔹 現在実行中のスレッドを取得

        for thread in self.threads:
            if thread.is_alive() and thread is not current_thread:
                thread.join(timeout=1)  # 🔹 自分自身は join() しない

        self.threads.clear()


    def LeaveLobby(self):
        """
        サーバーまたはクライアントを強制終了する
        """
        print("⚠️ ロビーから切断します...")
        self.connected = False
        self.running = False
        self.stop_all_threads()
        self.steam.leave_lobby(self.lobby_id)
        self.steam.close_all_p2p_sessions()

        self.global_event_manager.trigger_event("SelfLobbyLeave")

        # NetworkManager のリセット
        NetworkManager._instance = None
        print("✅ ネットワーク状態をリセットしました。")


    # ------------------------
    # ロビーの参加・退出の管理
    # ------------------------
    def update(self, dt):
        # **ロビー参加のチェック**
        success, steam_id, lobby_id = self.steam.check_lobby_join()
        if success:
            player_name = self.steam.get_steam_name(steam_id)
            print(f"✅ {player_name} (SteamID: {steam_id}) が ロビー {lobby_id} に参加しました！")

            # 🔹 参加者リストに追加
            self.lobby_members[steam_id] = player_name

            self.global_event_manager.trigger_event("LobbyJoin", steam_id=steam_id, player_name=player_name, lobby_id=lobby_id)


        # **ロビー退出のチェック**
        left, steam_id, lobby_id = self.steam.check_lobby_leave()
        if left:
            player_name = self.lobby_members.get(steam_id, "Unknown Player")
            print(f"❌ {player_name} (SteamID: {steam_id}) が ロビー {lobby_id} を退出しました。")

            # 🔹 参加者リストから削除
            if steam_id in self.lobby_members:
                del self.lobby_members[steam_id]

            self.global_event_manager.trigger_event("LobbyLeave", steam_id=steam_id, player_name=player_name, lobby_id=lobby_id)

    # 🔹 現在の参加者一覧を取得
    def get_lobby_members(self):
        return self.lobby_members






    def set_network_ids(self, lobby_id, server_steam_id, local_steam_id, is_server, is_client):
        self.lobby_id = lobby_id
        self.server_steam_id = server_steam_id
        self.local_steam_id = local_steam_id
        self.is_server = is_server
        self.is_client = is_client



