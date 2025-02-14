import json
import math
import time
import zlib
import base64

# 断片サイズはSteamの制限に合わせる
FRAGMENT_SIZE = 950

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片のバッファ管理

    def send_message(self, target_id, data):
        """
        data を JSON 化して圧縮し、断片化が必要なら分割して送信する。
        断片化する際は、バイナリデータをBase64エンコードして文字列に変換する。
        """
        # JSONにして圧縮
        message_bytes = zlib.compress(json.dumps(data).encode('utf-8'))
        print(f"[send_message] 全体サイズ: {len(message_bytes)} バイト")
        
        if len(message_bytes) > FRAGMENT_SIZE:
            self._send_large_message(target_id, message_bytes)
        else:
            self.network_manager.steam.send_p2p_message(target_id, message_bytes)

    def _send_large_message(self, target_id, message_bytes):
        """
        メッセージが大きい場合は、断片に分割して送信する。
        各断片は FRAGMENT_SIZE 以下になるようにする。
        バイナリデータをBase64エンコードしてからJSON化する。
        """
        total_fragments = math.ceil(len(message_bytes) / FRAGMENT_SIZE)
        fragment_id = str(time.time())  # 一意の断片IDとして現在時刻を使用

        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            # バイナリデータをBase64エンコードして文字列に変換
            fragment_data = base64.b64encode(message_bytes[start:end]).decode('utf-8')
            print(f"[_send_large_message] 断片 {index + 1}/{total_fragments}, サイズ: {len(fragment_data)} 文字")

            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                "data": fragment_data
            }
            fragment_bytes = json.dumps(fragment).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, fragment_bytes)

    def receive_message(self, raw_bytes):
        """
        受信したデータを解凍・JSON 化して返す。
        断片化されたメッセージの場合は、すべての断片が揃うまでバッファに保持し、
        完成したらBase64デコードしてからJSON化する。
        """
        try:
            decompressed = zlib.decompress(raw_bytes)
            message = json.loads(decompressed.decode('utf-8'))
        except (zlib.error, json.JSONDecodeError, UnicodeDecodeError):
            try:
                message = json.loads(raw_bytes.decode('utf-8'))
            except Exception:
                return None

        if message.get("type") == "fragment":
            return self._handle_incoming_fragment(message)
        return message

    def _handle_incoming_fragment(self, fragment):
        """
        断片メッセージを受信した場合の処理。
        すべての断片が揃えば、連結してBase64デコード後にJSON化したデータを返す。
        """
        fragment_id = fragment["fragment_id"]
        index = fragment["fragment_index"]
        total_fragments = fragment["total_fragments"]

        if fragment_id not in self.fragment_buffer:
            self.fragment_buffer[fragment_id] = [None] * total_fragments

        self.fragment_buffer[fragment_id][index] = fragment["data"]

        if all(part is not None for part in self.fragment_buffer[fragment_id]):
            complete_data_str = ''.join(self.fragment_buffer[fragment_id])
            del self.fragment_buffer[fragment_id]
            try:
                # Base64デコードしてから解凍・JSON化する
                complete_data_bytes = base64.b64decode(complete_data_str.encode('utf-8'))
                decompressed = zlib.decompress(complete_data_bytes)
                complete_data = json.loads(decompressed.decode('utf-8'))
                return complete_data
            except Exception as e:
                print(f"❌ 断片データの復元に失敗: {e}")
                return None

        return None  # まだ断片が足りない場合
