import json
import math
import time

FRAGMENT_SIZE = 850  # 断片サイズ

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片のバッファ管理

    def send_message(self, target_id, data):
        """データを送信 (そのまま分割)"""
        json_str = json.dumps(data)  # 直接JSONに変換
        message_bytes = json_str.encode('utf-8')  # UTF-8バイト列に変換

        if len(message_bytes) > FRAGMENT_SIZE:
            self._send_large_message(target_id, message_bytes)
        else:
            message_payload = json.dumps({"type": "full_message", "data": json_str}).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, message_payload)

    def _send_large_message(self, target_id, message_bytes):
        """データを断片化して送信"""
        total_fragments = math.ceil(len(message_bytes) / FRAGMENT_SIZE)
        fragment_id = str(time.time())  # 一意のIDを生成

        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            fragment_data = message_bytes[start:end].decode('utf-8', errors='replace')

            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                "data": fragment_data
            }

            fragment_bytes = json.dumps(fragment).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, fragment_bytes)
    def _handle_incoming_fragment(self, fragment):
        """受信したフラグメントを結合し、完全なメッセージを復元"""
        fragment_id = fragment["fragment_id"]
        index = fragment["fragment_index"]
        total_fragments = fragment["total_fragments"]

        if fragment_id not in self.fragment_buffer:
            self.fragment_buffer[fragment_id] = [None] * total_fragments

        self.fragment_buffer[fragment_id][index] = fragment["data"]

        # すべての断片が揃ったかチェック
        if all(part is not None for part in self.fragment_buffer[fragment_id]):
            complete_json_str = "".join(self.fragment_buffer[fragment_id])  # JSON文字列の結合
            del self.fragment_buffer[fragment_id]

            try:
                return json.loads(complete_json_str)
            except Exception as e:
                print(f"⚠️ Error in fragment decoding: {e}")
                return None

        return None
