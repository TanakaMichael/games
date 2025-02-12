import pygame
import re
class Canvas:
    def __init__(self, screen):
        self.ui_objects = []
        self.screen = screen
        self.canvas_size = pygame.Vector2(1920, 1080)
        self.current_window_size = pygame.Vector2(self.screen.get_size())

        self.scale_factor = pygame.Vector2(
            self.current_window_size.x / self.canvas_size.x,
            self.current_window_size.y / self.canvas_size.y
        )
    def add_ui(self, ui):
        self.ui_objects.append(ui)
        self.ui_objects.sort(key=lambda e: e.layer)  # レイヤー順にソート
        return ui

    def remove_ui(self, ui):
        self.ui_objects.remove(ui)
    def update(self, dt):
        for object in self.ui_objects:
            if object.active:
                object.update(dt)
    def render(self, screen):
        for object in self.ui_objects:
            if object.visible:
                object.render(screen)
    def handle_event(self, event):
        """UI 要素にイベントを処理"""
        if event.type == pygame.VIDEORESIZE:
            self.on_resize(event.w, event.h)
        for object in self.ui_objects:
            object.handle_event(event)
    def on_resize(self, new_width, new_height):
        """ウィンドウサイズ変更時にキャンバスサイズを更新"""
        self.current_window_size = pygame.Vector2(new_width, new_height)

        # **スケール係数の更新**
        self.scale_factor.x = self.current_window_size.x / self.canvas_size.x
        self.scale_factor.y = self.current_window_size.y / self.canvas_size.y

    # ヘルパーメソッド
    def get_canvas_size(self):
        return self.canvas_size.copy()
    def get_window_size(self):
        """ウィンドウサイズ (width, height) を取得"""
        return pygame.Vector2(self.screen.get_size())
    
    def get_scale_factor(self):
        """Canvas座標からScreen座標にするスケールファクター"""
        return self.scale_factor.copy()
    
    def clear(self):
        """UI 要素をすべて削除"""
        for object in self.ui_objects:
            if hasattr(object, "end"):
                object.end()  # **オブジェクトが `end()` を持っている場合のみ呼び出す**
        self.ui_objects.clear()
        # 以前はEvent式のInputのために使っていたがおそらく必要ない
    def _parse_position(self, position):
        """入力の local_position を適切な `pygame.Vector2` に変換"""
        if isinstance(position, tuple) and len(position) == 2:
            canvas_size = self.get_canvas_size()
            parsed_x = self._parse_axis(position[0], canvas_size[0])
            parsed_y = self._parse_axis(position[1], canvas_size[1])
            return pygame.Vector2(parsed_x, parsed_y)
        return pygame.Vector2(position)  # 数値の場合そのまま適用

    def _parse_axis(self, value, canvas_size):
        """'center+100', 'right-50', 'top*0.5' などの座標演算を処理"""
        if isinstance(value, str):
            base_value = 0

            # **基準値を決定**
            if "center" in value:
                base_value = canvas_size / 2
            elif "top" in value:
                base_value = 0
            elif "bottom" in value:
                base_value = canvas_size
            elif "left" in value:
                base_value = 0
            elif "right" in value:
                base_value = canvas_size

            # **演算が含まれる場合、計算を実行**
            match = re.search(r"([+\-*/]\d+(\.\d+)?)", value)
            if match:
                operation = match.group(0)  # 例: "+100", "-50", "*0.5"
                try:
                    # **文字列の式を安全に評価**
                    base_value = eval(f"{base_value}{operation}")
                except Exception as e:
                    raise ValueError(f"無効な座標演算: {value} ({e})")

            return base_value  # **計算結果を返す**

        return value  # **数値ならそのまま使用**
    def to_canvas_position(self, screen_x, screen_y):
        """
        **スクリーン座標 → キャンバス座標 に変換**
        :param screen_x: スクリーン上の X 座標
        :param screen_y: スクリーン上の Y 座標
        :return: `pygame.Vector2` (キャンバス内の座標)
        """
        # **スケール係数を適用**
        canvas_x = screen_x / self.scale_factor.x
        canvas_y = screen_y / self.scale_factor.y

        return pygame.Vector2(canvas_x, canvas_y)