class UIComponent:
    """UI に追加できるコンポーネントの基底クラス"""
    def __init__(self, ui_object):
        self.ui_object = ui_object
        self.active = True  # **有効フラグ**
    
    def update(self, delta_time):
        """毎フレーム更新処理（オーバーライド可能）"""
        pass
    def render(self, screen):
        """描画処理 (オーバー��イド用)"""
        pass

    def enable(self):
        """コンポーネントを有効化"""
        self.active = True

    def disable(self):
        """コンポーネントを無効化"""
        self.active = False
    def handle_event(self, event):
        """イベントを処理"""
        pass