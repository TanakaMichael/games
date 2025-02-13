import json
import math
import time
import zlib

FRAGMENT_SIZE = 950  # Steam P2P の制限を考慮した断片サイズ

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片を一時保持する辞書

    def send_message(self, target_id, data):
        """
        data を JSON 化して圧縮し、断片化が必要なら分割して送信する
        """
        # JSON にして圧縮
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
        """
        total_fragments = math.ceil(len(message_bytes) / FRAGMENT_SIZE)
        fragment_id = str(time.time())  # 一意の断片IDとして現在時刻を使用

        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            # FRAGMENT_SIZE ごとに断片を切り出し、文字列に変換（エラーは無視）
            fragment_data = message_bytes[start:end].decode('utf-8', errors='ignore')
            print(f"[_send_large_message] 断片 {index + 1}/{total_fragments}, サイズ: {len(fragment_data)} バイト")

            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                "data": fragment_data
            }
            # 各断片は再度 JSON 化して送信
            fragment_bytes = json.dumps(fragment).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, fragment_bytes)

    def receive_message(self, raw_bytes):
        """
        受信したデータを解凍・JSON 化して返す。
        断片化されたメッセージの場合は、すべての断片が揃うまでバッファに保持し、完成したら返す。
        """
        # まず圧縮されたメッセージとして解凍を試みる
        try:
            decompressed = zlib.decompress(raw_bytes)
            message = json.loads(decompressed.decode('utf-8'))
        except (zlib.error, json.JSONDecodeError, UnicodeDecodeError):
            # 圧縮されていない可能性もあるので、その場合は直接デコード
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
        すべての断片が揃えば、連結して JSON 化したデータを返す。
        """
        fragment_id = fragment["fragment_id"]
        index = fragment["fragment_index"]
        total_fragments = fragment["total_fragments"]

        if fragment_id not in self.fragment_buffer:
            self.fragment_buffer[fragment_id] = [None] * total_fragments

        self.fragment_buffer[fragment_id][index] = fragment["data"]

        # すべての断片が揃ったか確認
        if all(part is not None for part in self.fragment_buffer[fragment_id]):
            complete_data_str = ''.join(self.fragment_buffer[fragment_id])
            del self.fragment_buffer[fragment_id]  # バッファクリア

            try:
                complete_data = json.loads(complete_data_str)
                return complete_data
            except json.JSONDecodeError:
                return None

        return None  # まだ断片が足りない場合
