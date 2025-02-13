import time

class PingMeter:
    def __init__(self, network_manager, ema_alpha=0.2):
        """
        :param network_manager: NetworkManager インスタンス
        :param ema_alpha: 平滑化係数 (0～1)。1に近いほど最新値を重視
        """
        self.network_manager = network_manager
        self.ema_alpha = ema_alpha
        self.last_ping_time = time.perf_counter()
        self.ping_rate = 0.0
        self.interval = 1
        self.last_send_time = time.time()

    def process_ping_response(self, ping_response):
        """
        サーバーからの PING_RESPONSE を処理し、RTT と平滑化された ping_rate を計算する。
        ping_response は辞書形式で {"type": "PING_RESPONSE", "time": 送信時刻, ...} のように想定。
        """
        current_time = time.perf_counter()
        sent_time = ping_response.get("time")
        if sent_time is not None:
            rtt = current_time - sent_time
            estimated_ping = rtt / 2.0
            if self.ping_rate == 0:
                self.ping_rate = estimated_ping
            else:
                self.ping_rate = self.ema_alpha * estimated_ping + (1 - self.ema_alpha) * self.ping_rate
            print(f"DEBUG: RTT = {rtt:.3f}s, estimated ping = {estimated_ping:.3f}s, smoothed ping_rate = {self.ping_rate:.3f}s")
            self.last_ping_time = current_time
    def send_ping(self, message):
        data = {
            "type": "ping_response", 
            "time": message.get("time"),
        }
        self.network_manager.send_to_client(int(message.get("sender_id")), data)
    def receive_message(self, message):
        t = message.get("type")
        if t == "ping_request":
            self.send_ping(message)
        elif t == "ping_response":
            self.process_ping_response(message)
    
    



    def send_ping_request(self):
        """
        クライアント側がサーバーに PING_REQUEST を送信するためのデータを作成して送信する。
        """
        if self.network_manager.running and self.last_send_time + self.interval < time.time():
            ping_request = {
               "type": "ping_request",
               "time": time.perf_counter(),
               "sender_id": self.network_manager.local_steam_id
            }
            self.last_send_time = time.time()
            self.network_manager.send_to_server(ping_request)
