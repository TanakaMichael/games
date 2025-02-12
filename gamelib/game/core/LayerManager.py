class LayerManager:
    """Camera が保持するレイヤー管理クラス。複数の Layer を管理する。"""
    def __init__(self):
        self.layers = []

    def add_layer(self, layer):
        """Layer を追加"""
        self.layers.append(layer)
        return layer

    def remove_layer(self, layer):
        """Layer を削除"""
        if layer in self.layers:
            self.layers.remove(layer)

    def get_layer(self, name):
        """レイヤー名で探して返す。見つからなければ None"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None

    def update(self, delta_time):
        """すべてのレイヤーを更新"""
        for layer in self.layers:
            layer.update(delta_time)

    def render_back_layers(self, screen, camera):
        """parallax_factor が 1.0 以下のレイヤーをソートして描画"""
        for layer in sorted(self.layers, key=lambda l: l.parallax_factor):
            if layer.parallax_factor <= 1.0:
                layer.render(screen, camera)

    def render_front_layers(self, screen, camera):
        """parallax_factor が 1.0 超のレイヤーをソートして描画"""
        for layer in sorted(self.layers, key=lambda l: l.parallax_factor):
            if layer.parallax_factor > 1.0:
                layer.render(screen, camera)
