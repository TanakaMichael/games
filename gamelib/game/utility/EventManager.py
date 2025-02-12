class EventManager:
    """イベント登録・通知の基底クラス"""
    def __init__(self):
        self.events = {}

    def register_event(self, event_name, callback):
        """イベントを登録"""
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    def trigger_event(self, event_name, **kwargs):
        """イベントを発火 (登録されたすべてのコールバックを実行)"""
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(**kwargs)
    def unregister_event(self, event_name, callback):
        """イベントの登録解除"""
        if event_name in self.events:
            self.events[event_name].remove(callback)
    def clear_events(self):
        """すべてのイベントを解除"""
        self.events.clear()