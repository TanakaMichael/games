class Component:
    """GameObjectに付与できるコンポーネントの基底クラス"""
    def __init__(self, game_object):
        self.game_object = game_object  # このコンポーネントを持つGameObject
        self.enabled = True  # コンポーネントが有効かどうか

    def start(self):
        """初期化処理 (オーバーライド用)"""
        pass

    def update(self, delta_time):
        """毎フレーム更新処理 (オーバーライド用)"""
        if not self.enabled:
            return False
    def render(self, surface, camera):
        """描画処理 (オーバーライド用)"""
        if not self.enabled:
            return False
    def handle_event(self, event):
        """イベントを処理 (オーバーライド用)"""
        pass
