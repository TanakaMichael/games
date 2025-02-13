import json
import math
import time

FRAGMENT_SIZE = 1024  # 断片サイズの上限

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片のバッファ管理

    def send_message(self, target_id, data):
        message_bytes = json.dumps(data).encode('utf-8')

        if len(message_bytes) > FRAGMENT_SIZE:
            # 断片化が必要な場合
            self._send_large_message(target_id, message_bytes)
        else:
            self.network_manager.steam.send_p2p_message(target_id, message_bytes)

    def _send_large_message(self, target_id, message_bytes):
        total_fragments = math.ceil(len(message_bytes) / FRAGMENT_SIZE)
        fragment_id = str(time.time())  # 一意のID

        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                "data": message_bytes[start:end].decode('utf-8', errors='ignore')
            }
            self.network_manager.steam.send_p2p_message(target_id, json.dumps(fragment).encode('utf-8'))

    def receive_message(self, raw_bytes):
        try:
            message = json.loads(raw_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            return None

        if message.get("type") == "fragment":
            return self._handle_incoming_fragment(message)
        return message

    def _handle_incoming_fragment(self, fragment):
        fragment_id = fragment["fragment_id"]
        index = fragment["fragment_index"]
        total_fragments = fragment["total_fragments"]

        if fragment_id not in self.fragment_buffer:
            self.fragment_buffer[fragment_id] = [None] * total_fragments

        self.fragment_buffer[fragment_id][index] = fragment["data"]

        # すべての断片が揃った場合
        if all(part is not None for part in self.fragment_buffer[fragment_id]):
            complete_data = ''.join(self.fragment_buffer[fragment_id])
            del self.fragment_buffer[fragment_id]  # バッファのクリア
            return json.loads(complete_data)

        return None  # まだ未完成
