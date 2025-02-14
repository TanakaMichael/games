import ctypes
import os
import time
import threading
import json
import zlib
import base64
class SteamNetworking:
    def __init__(self, dll_path="SteamNetworkingWrapper.dll"):
        self.dll_path = os.path.abspath(dll_path)
        try:
            self.steam_dll = ctypes.CDLL(self.dll_path)

            # -------------------------------
            # Steam API 関連
            # -------------------------------
            self._initialize_steam = self.steam_dll.InitializeSteam
            self._initialize_steam.restype = ctypes.c_bool

            self._run_steam_callbacks = self.steam_dll.RunSteamCallbacks
            self._run_steam_callbacks.restype = None

            self._get_steam_id = self.steam_dll.GetSteamID
            self._get_steam_id.restype = ctypes.c_uint64

            # -------------------------------
            # ロビー関連
            # -------------------------------
            self._create_lobby = self.steam_dll.CreateLobby
            self._create_lobby.argtypes = [ctypes.c_int, ctypes.c_int]
            self._create_lobby.restype = ctypes.c_uint64

            self._join_lobby = self.steam_dll.JoinLobby
            self._join_lobby.argtypes = [ctypes.c_uint64]
            self._join_lobby.restype = ctypes.c_bool

            self._leave_lobby = self.steam_dll.LeaveLobby
            self._leave_lobby.argtypes = [ctypes.c_uint64]
            self._leave_lobby.restype = None

            self._get_lobby_owner = self.steam_dll.GetLobbyOwner
            self._get_lobby_owner.argtypes = [ctypes.c_uint64]
            self._get_lobby_owner.restype = ctypes.c_uint64

            self._get_num_lobby_members = self.steam_dll.GetNumLobbyMembers
            self._get_num_lobby_members.argtypes = [ctypes.c_uint64]
            self._get_num_lobby_members.restype = ctypes.c_int

            self._get_lobby_member_by_index = self.steam_dll.GetLobbyMemberByIndex
            self._get_lobby_member_by_index.argtypes = [ctypes.c_uint64, ctypes.c_int]
            self._get_lobby_member_by_index.restype = ctypes.c_uint64

            # lobby検索 (公開)
            self._refresh_public_lobbies = self.steam_dll.RefreshPublicLobbies
            self._refresh_public_lobbies.argtypes = []
            self._refresh_public_lobbies.restype = ctypes.c_int

            self._get_public_lobby_id_by_index = self.steam_dll.GetPublicLobbyIDByIndex
            self._get_public_lobby_id_by_index.argtypes = [ctypes.c_int]
            self._get_public_lobby_id_by_index.restype = ctypes.c_uint64

            # lobby検索 (friend)
            self._refresh_friend_lobbies = self.steam_dll.RefreshFriendLobbiesRichPresence
            self._refresh_friend_lobbies.argtypes = []
            self._refresh_friend_lobbies.restype = ctypes.c_int
            # friendのsteamIDを取得
            self._get_friend_steam_id_by_index = self.steam_dll.GetFriendLobbyIDByIndex_RichPresence
            self._get_friend_steam_id_by_index.argtypes = [ctypes.c_int]
            self._get_friend_steam_id_by_index.restype = ctypes.c_uint64

            # friendのsteamIDからLobbyIDを取得
            self._get_friend_lobby_id_by_steam_id = self.steam_dll.GetLobbyIDFromFriendSteamID
            self._get_friend_lobby_id_by_steam_id.argtypes = [ctypes.c_uint64]
            self._get_friend_lobby_id_by_steam_id.restype = ctypes.c_uint64

            # GetSteamNameの定義
            self._get_steam_name = self.steam_dll.GetSteamName
            self._get_steam_name.argtypes = [ctypes.c_uint64, ctypes.c_char_p, ctypes.c_int]
            self._get_steam_name.restype = None
            # -------------------------------
            # P2P 通信関連
            # -------------------------------
            self._accept_p2p_session = self.steam_dll.AcceptP2PSession
            self._accept_p2p_session.argtypes = [ctypes.c_uint64]
            self._accept_p2p_session.restype = ctypes.c_bool

            self._send_p2p_message = self.steam_dll.SendP2PMessage
            self._send_p2p_message.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
            self._send_p2p_message.restype = ctypes.c_bool

            self._receive_p2p_message = self.steam_dll.ReceiveP2PMessage
            self._receive_p2p_message.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)]
            self._receive_p2p_message.restype = ctypes.c_bool

            self._close_all_p2p_sessions = self.steam_dll.CloseAllP2PSessions
            self._close_all_p2p_sessions.restype = None

            # -------------------------------
            # Rich Presence
            # -------------------------------
            self._set_lobby_rich_presence = self.steam_dll.SetLobbyRichPresence
            self._set_lobby_rich_presence.argtypes = [ctypes.c_uint64]
            self._set_lobby_rich_presence.restype = None

            self._clear_rich_presence = self.steam_dll.ClearRichPresence
            self._clear_rich_presence.restype = None

            # ロビー参加・退出検出
            self._check_lobby_join = self.steam_dll.CheckLobbyJoin
            self._check_lobby_join.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
            self._check_lobby_join.restype = ctypes.c_bool

            self._check_lobby_leave = self.steam_dll.CheckLobbyLeave
            self._check_lobby_leave.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
            self._check_lobby_leave.restype = ctypes.c_bool


            # -------------------------------
            # サーバー管理
            # -------------------------------
            self._shutdown_server = self.steam_dll.ShutdownServer
            self._shutdown_server.restype = None

        except Exception as e:
            print("❌ DLL の読み込みに失敗しました:", e)
            exit()

        if self._initialize_steam():
            print("✅ Steam API 初期化成功")
        else:
            print("❌ Steam API 初期化失敗")
            exit()

        self.steam_id = self._get_steam_id()
        print(f"🎮 自分の Steam ID: {self.steam_id}")

    # -------------------------------
    # コールバック処理
    # -------------------------------
    def run_callbacks(self):
        self._run_steam_callbacks()

    def run_callbacks_loop(self, interval=0.01):
        while True:
            self.run_callbacks()
            time.sleep(interval)

    # -------------------------------
    # ロビー操作
    # -------------------------------
    def create_lobby(self, lobby_type, max_players):
        return self._create_lobby(lobby_type, max_players)

    def join_lobby(self, lobby_id):
        return self._join_lobby(lobby_id)

    def leave_lobby(self, lobby_id):
        self._leave_lobby(lobby_id)

    def get_lobby_owner(self, lobby_id):
        return self._get_lobby_owner(lobby_id)

    def get_num_lobby_members(self, lobby_id):
        return self._get_num_lobby_members(lobby_id)

    def get_lobby_member_by_index(self, lobby_id, index):
        return self._get_lobby_member_by_index(lobby_id, index)
    def get_steam_name(self, steam_id):
        """
        指定したSteamIDに対応するフレンドの名前を取得する。

        :param steam_id: SteamID (uint64)
        :return: フレンドの表示名 (str)
        """
        buffer_size = 128  # 名前の最大長 (適宜調整)
        buffer = ctypes.create_string_buffer(buffer_size)
        
        # DLL関数の呼び出し
        self._get_steam_name(steam_id, buffer, buffer_size)
        
        # バイト列からPythonの文字列へ変換
        return buffer.value.decode('utf-8')
    
    # -------------------------------
    # ｌｏｂｂｙ検索
    # -------------------------------
    def get_public_lobbies(self):
        # リフレッシュする
        lobbies_id = []
        num_lobbies = self._refresh_public_lobbies()
        if num_lobbies == 0:
            return lobbies_id
        for i in range(num_lobbies):
            lobbies_id.append(self._get_public_lobby_id_by_index(i))
        return lobbies_id
    def get_friend_lobbies(self):
        # リフレッシュ
        lobbies_id = {}
        num_lobbies = self._refresh_friend_lobbies()
        if num_lobbies == 0:
            return lobbies_id
        for i in range(num_lobbies):
            steam_id = self._get_friend_steam_id_by_index(i)
            lobby_id = self._get_friend_lobby_id_by_steam_id(steam_id)
            lobbies_id[steam_id] = lobby_id
        return lobbies_id




    # -------------------------------
    # P2P 通信
    # -------------------------------
    def accept_p2p_session(self, steam_id):
        return self._accept_p2p_session(steam_id)

    def send_p2p_message(self, steam_id, message):
        if isinstance(message, str):
            message = message.encode('utf-8')  # 文字列の場合はエンコード
        return self._send_p2p_message(steam_id, message)

    # 断片サイズなどの定数は別途定義されているものとする

    def receive_p2p_message(self, buffer_size=1024):
        buffer = ctypes.create_string_buffer(buffer_size)  # 受信用バッファ
        sender_id = ctypes.c_uint64(0)  # 送信者ID格納用

        success = self._receive_p2p_message(buffer, buffer_size, ctypes.byref(sender_id))
        if success:
            # 受信したデータが空でないかチェック
            if buffer.value and buffer.value != b'\x00' * buffer_size:
                try:
                    # まず、受信したバイト列をUTF-8で文字列に変換
                    encoded_str = buffer.value.decode('utf-8', errors='replace').strip('\x00')
                except Exception as e:
                    print(f"📩 Raw Buffer Value: {buffer.value}")

                    print(f"⚠️ Decode error: {e}")
                    return None, sender_id.value

                # ここで、送信時に圧縮とbase64エンコードしているため、復元する
                try:
                    # base64デコードして圧縮済みデータを取り出す
                    compressed_data = base64.b64decode(encoded_str)
                    # zlibで解凍して元のJSON文字列に戻す
                    json_str = zlib.decompress(compressed_data).decode('utf-8')
                    # JSON文字列をオブジェクトにパースする
                    message = json.loads(json_str)
                except Exception as e:
                    print(f"⚠️ Decompression/JSON decode error: {e}")
                    return None, sender_id.value

                # print(f"📩 Received from {sender_id.value}: {message}")
                return message, sender_id.value
            else:
                print(f"⚠️ Received empty message from {sender_id.value}")
        return None, None




    def close_all_p2p_sessions(self):
        self._close_all_p2p_sessions()

    # -------------------------------
    # Rich Presence
    # -------------------------------
    def set_lobby_rich_presence(self, lobby_id):
        self._set_lobby_rich_presence(lobby_id)

    def clear_rich_presence(self):
        self._clear_rich_presence()

    def get_all_lobby_members(self, lobby_id):
        """
        現在ロビーに参加しているすべてのメンバーのSteamIDを取得する。
        :param lobby_id: 対象のロビーID
        :return: SteamIDのリスト
        """
        member_count = self._get_num_lobby_members(lobby_id)
        steam_ids = []

        for index in range(member_count):
            steam_id = self._get_lobby_member_by_index(lobby_id, index)
            if steam_id != 0:
                steam_ids.append(steam_id)

        return steam_ids
    
    # -------------------------------
    # ロビー参加・退出検出
    # -------------------------------
    def check_lobby_join(self):
        joined_steam_id = ctypes.c_uint64(0)
        lobby_id = ctypes.c_uint64(0)
        success = self._check_lobby_join(ctypes.byref(joined_steam_id), ctypes.byref(lobby_id))
        return success, joined_steam_id.value, lobby_id.value

    def check_lobby_leave(self):
        left_steam_id = ctypes.c_uint64(0)
        lobby_id = ctypes.c_uint64(0)
        success = self._check_lobby_leave(ctypes.byref(left_steam_id), ctypes.byref(lobby_id))
        return success, left_steam_id.value, lobby_id.value

    # -------------------------------
    # サーバー管理
    # -------------------------------
    def shutdown_server(self):
        self._shutdown_server()

# テスト用のコード
if __name__ == "__main__":
    steam = SteamNetworking()
    threading.Thread(target=steam.run_callbacks_loop, daemon=True).start()

    lobby_id = steam.create_lobby(1, 4)
    print("Lobby Created:", lobby_id)

    if steam.join_lobby(lobby_id):
        print("Successfully joined the lobby.")

    steam.send_p2p_message(steam.steam_id, "Hello from Python!")

    time.sleep(3)
    steam.shutdown_server()
