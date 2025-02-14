import ctypes
import time
import json
import zlib
import base64
import re
import math

FRAGMENT_SIZE = 850  # 断片サイズなどは適宜定義されているものとする

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片のバッファ管理

    def send_message(self, target_id, data):
        """データを送信する (圧縮・エンコード後にP2P送信)"""
        json_str = json.dumps(data)
        compressed = zlib.compress(json_str.encode('utf-8'))
        encoded = base64.b64encode(compressed).decode('utf-8')  # Base64エンコード
        
        message_bytes = encoded.encode('utf-8')

        if len(message_bytes) > FRAGMENT_SIZE:
            self._send_large_message(target_id, message_bytes)
        else:
            self.network_manager.steam.send_p2p_message(target_id, message_bytes)

    def _send_large_message(self, target_id, message_bytes):
        """データを断片化して送信"""
        total_fragments = math.ceil(len(message_bytes) / FRAGMENT_SIZE)
        fragment_id = str(time.time())

        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            fragment_data = message_bytes[start:end].decode('utf-8', errors='replace')

            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                "data": fragment_data  # そのまま文字列として送信
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
        else:
            return self._decode_message(message)

    def _decode_message(self, message):
        """Base64デコードと圧縮解除"""
        try:
            # 受信データに余計な非ASCII文字が混ざっていないかクリーニング
            clean_message = re.sub(r'[^A-Za-z0-9+/=]', '', message)

            # Base64パディングを補正（=の個数を調整）
            padding = 4 - (len(clean_message) % 4)
            if padding and padding != 4:
                clean_message += "=" * padding

            compressed = base64.b64decode(clean_message)
            json_str = zlib.decompress(compressed).decode('utf-8')

            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️ Error decoding message: {e}")
            return message
