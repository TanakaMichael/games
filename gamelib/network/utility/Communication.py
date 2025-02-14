import json
import math
import time
import zlib
import base64

FRAGMENT_SIZE = 950  # Steam P2Pのパケットサイズ制限を考慮

class Communication:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.fragment_buffer = {}  # 断片を一時保持する辞書 {fragment_id: [断片1, 断片2, ...]}

    def send_message(self, target_id, data):
        # JSONに変換して圧縮
        raw = json.dumps(data).encode('utf-8')
        compressed = zlib.compress(raw)
        
        if len(compressed) > FRAGMENT_SIZE:
            self._send_large_message(target_id, compressed)
        else:
            self.network_manager.steam.send_p2p_message(target_id, compressed)
    
    def _send_large_message(self, target_id, message_bytes):
        total_fragments = math.ceil(len(message_bytes) / FRAGMENT_SIZE)
        # 一意のIDとして現在時刻を文字列に変換
        fragment_id = str(time.time())
        
        for index in range(total_fragments):
            start = index * FRAGMENT_SIZE
            end = start + FRAGMENT_SIZE
            fragment_data = message_bytes[start:end]
            
            # デバッグ: 各断片のサイズを出力
            print(f"Sending fragment {index + 1}/{total_fragments}, size: {len(fragment_data)}")
            
            fragment = {
                "type": "fragment",
                "fragment_id": fragment_id,
                "fragment_index": index,
                "total_fragments": total_fragments,
                # 断片データは base64 エンコードせず、文字列に変換（エンコード時 errors='replace'）
                "data": fragment_data.decode('latin1', errors='replace')  
                # ※ latin1 を使うことで1:1変換が可能。復元時に同じ方式でエンコードする
            }
            fragment_json = json.dumps(fragment).encode('utf-8')
            self.network_manager.steam.send_p2p_message(target_id, fragment_json)
    
    def receive_message(self, raw_bytes):
        try:
            message = json.loads(raw_bytes.decode('utf-8', errors='replace'))
        except json.JSONDecodeError:
            print("⚠️ JSONDecodeError in receive_message")
            return None

        if message.get("type") == "fragment":
            return self._handle_incoming_fragment(message)
        else:
            # 通常のメッセージは圧縮されているので解凍して返す
            try:
                decompressed = zlib.decompress(raw_bytes)
                return json.loads(decompressed.decode('utf-8')), None
            except Exception as e:
                print(f"⚠️ Decompression error: {e}")
                return None

    def _handle_incoming_fragment(self, fragment):
        fragment_id = fragment["fragment_id"]
        index = fragment["fragment_index"]
        total_fragments = fragment["total_fragments"]
        
        # 断片データはlatin1でエンコードされているので元のバイト列に戻す
        fragment_bytes = fragment["data"].encode('latin1')
        
        if fragment_id not in self.fragment_buffer:
            self.fragment_buffer[fragment_id] = [None] * total_fragments
        
        self.fragment_buffer[fragment_id][index] = fragment_bytes
        
        # すべての断片が揃った場合
        if all(part is not None for part in self.fragment_buffer[fragment_id]):
            complete_data = b"".join(self.fragment_buffer[fragment_id])
            del self.fragment_buffer[fragment_id]
            try:
                decompressed = zlib.decompress(complete_data)
                return json.loads(decompressed.decode('utf-8'))
            except Exception as e:
                print(f"⚠️ Error decompressing or decoding complete data: {e}")
                return None
        
        return None  # まだ断片が不足している