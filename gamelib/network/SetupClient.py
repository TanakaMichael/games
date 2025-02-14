import threading
import time
from ..game.utility.Coroutine import CoroutineManager, WaitForSeconds
class SetupClient:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.coroutine_manager = CoroutineManager()

    def run(self, lobby_id):
        if not self.self.network_manager.running:
            if self.network_manager.steam.join_lobby(lobby_id):
                print("✅ ロビー参加成功")
            server_steam_id = self.network_manager.steam.get_lobby_owner(lobby_id)
            local_steam_id = self.network_manager.steam.steam_id

            self.network_manager.set_network_ids(lobby_id, server_steam_id, local_steam_id, False, True)
            self.network_manager.running = True
            self.network_manager.connected = False
            self.network_manager.thread_running.set()  # スレッド開始のフラグをTrueに

            # スレッド開始
            self.coroutine_manager.start_coroutine(self._ping_handshake)
            self.network_manager.coroutine_manager.start_coroutine(self.network_manager._receive_messages)

            #self.network_manager.start_thread(self._ping_handshake)
            #self.network_manager.start_thread(self.network_manager._receive_messages)
    def update(self, dt):
        self.coroutine_manager.update(dt)


    def _ping_handshake(self, timeout=20):
        """
        Ping応答を待機し、タイムアウトした場合は強制切断
        """
        start_time = time.time()
        initial_ping_rate = self.network_manager.ping_meter.ping_rate

        print("📡 サーバーへの Ping を開始します...")

        while time.time() - start_time < timeout:
            self.network_manager.ping_meter.send_ping_request()
            yield WaitForSeconds(1)

            # ping_rate が初期値から変わった場合は接続成功
            if self.network_manager.ping_meter.ping_rate != initial_ping_rate:
                print("✅ Ping 応答を受信しました。接続確立！")
                self.network_manager.connected = True

                # シーン同期完了を待機
                self.coroutine_manager.start_coroutine(self._await_scene_sync)
                return

        # タイムアウト処理
        print("❌ Ping 応答なし。接続タイムアウト。ロビーを離脱します。")
        self.network_manager.LeaveLobby()

    def _await_scene_sync(self, timeout=20):
        print("⏳ シーン同期中...")
        # シーン同期を要請する
        start_time = time.time()
        self.network_manager.complete_scene_sync = False
        self.network_manager.scene_manager.request_scene_sync(self.network_manager)
        while time.time() - start_time < timeout:
            yield WaitForSeconds(1)
            if self.network_manager.complete_scene_sync:
                self.network_manager.connected = True
                print("🎉 シーン同期完了！接続確立。")
                self.network_manager.global_event_manager.trigger_event("SetupClient")
                return
        
        # タイムアウト処理
        print("❌ scene sync 応答なし。接続タイムアウト。ロビーを離脱します。")
        self.network_manager.LeaveLobby()