import time
import json

class MissingObjectManager:
    def __init__(self, network_manager, request_timeout=5):
        """
        :param network_manager: NetworkManager インスタンス
        :param request_timeout: 再送信タイムアウト (秒)
        """
        self.network_manager = network_manager
        self.request_timeout = request_timeout
        # キー: network_id, 値: {"last_request": タイムスタンプ, "attempts": 試行回数}
        self.missing_object_requests = {}

    def request_missing_object(self, network_id):
        """
        欠損オブジェクトの情報をサーバーに要求する。
        :param network_id: 欠損オブジェクトのネットワークID
        """
        current_time = time.time()
        req = self.missing_object_requests.get(network_id)
        if req is None:
            self.missing_object_requests[network_id] = {"last_request": current_time, "attempts": 1}
            self._send_missing_object_request(network_id)
        else:
            if current_time - req["last_request"] >= self.request_timeout:
                req["last_request"] = current_time
                req["attempts"] += 1
                print(f"📡 Missing object (network_id: {network_id}) re-request, attempt: {req['attempts']}")
                self._send_missing_object_request(network_id)

    def _send_missing_object_request(self, network_id):
        request_data = {
            "type": "request_missing_object",
            "network_id": network_id,
            "sender_id": self.network_manager.local_steam_id
        }
        self.network_manager.send_to_server(request_data)

    def check_missing_requests(self):
        """
        定期的に欠損オブジェクトのリクエストをチェックし、タイムアウトしているものを再送信する。
        この関数は別スレッドで呼び出すことを想定。
        """
        while self.network_manager.running:
            current_time = time.time()
            for network_id, req in list(self.missing_object_requests.items()):
                if current_time - req["last_request"] >= self.request_timeout:
                    req["last_request"] = current_time
                    req["attempts"] += 1
                    print(f"📡 Re-requesting missing object {network_id}, attempt {req['attempts']}")
                    self._send_missing_object_request(network_id)
            time.sleep(1)
