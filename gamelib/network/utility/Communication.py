import ctypes
import time
import json
import base64
import re
import math

FRAGMENT_SIZE = 850  # 断片サイズ (適宜変更)

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片のバッファ管理

    def send_message(self, target_id, data):
        """データを送信 (Base64エンコードして分割)"""
        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')  # Base64エンコード
        
        message_bytes = encoded.encode('utf-8')

        if len(message_bytes) > FRAGMENT_SIZE:
            self._send_large_message(target_id, encoded)
        else:
            message_payload = json.dumps({"type": "full_message", "data": encoded}).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, message_payload)

    def _send_large_message(self, target_id, encoded_data):
        """データを断片化して送信"""
        total_fragments = math.ceil(len(encoded_data) / FRAGMENT_SIZE)
        fragment_id = str(time.time())

        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            fragment_data = encoded_data[start:end]

            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                "data": fragment_data  # Base64文字列の一部
            }

            fragment_bytes = json.dumps(fragment).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, fragment_bytes)
    def receive_message(self, raw_bytes):
        """受信データを解析する"""
        try:
            decoded_str = raw_bytes.decode('utf-8', errors='replace').strip('\x00')
            message = json.loads(decoded_str)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error: {e}")
            return None

        if message.get("type") == "fragment":
            return self._handle_incoming_fragment(message)
        elif message.get("type") == "full_message":
            return self._decode_message(message["data"])
        else:
            return None

    def _decode_message(self, base64_str):
        """Base64デコード"""
        try:
            # Base64のパディングを補正
            clean_message = re.sub(r'[^A-Za-z0-9+/=]', '', base64_str)
            padding = 4 - (len(clean_message) % 4)
            if padding and padding != 4:
                clean_message += "=" * padding

            json_str = base64.b64decode(clean_message).decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️ Error decoding message: {e}")
            return None
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
            complete_encoded = "".join(self.fragment_buffer[fragment_id])  # Base64文字列の結合
            del self.fragment_buffer[fragment_id]

            return self._decode_message(complete_encoded)

        return None
