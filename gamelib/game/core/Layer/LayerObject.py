import pygame
from ...component.Transform import Transform  # パスは環境に合わせて変えてください

class LayerObject:
    """
    レイヤー上に配置する基本的なオブジェクト。
    - 画像を1枚だけ描画する想定。タイル化しない。
    - Transform を持ち、カメラやパララックスに応じた描画を行う。
    """
    def __init__(self, image_path, transform=None, visible=True):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.visible = visible

        if transform is None:
            # 自前で Transform を作る（game_object なしの場合など）
            # あるいはダミーGameObjectでもよい
            self.transform = Transform(game_object=None)
        else:
            self.transform = transform

    def set_size(self, size):
        """画像を拡大・縮小する"""
        self.image = pygame.transform.scale(self.image, (int(size[0]), int(size[1])))

    def update(self, delta_time):
        """必要に応じてアニメーションや移動など"""
        # ここでは何もしない
        pass

    def render(self, surface, camera, parallax_factor=1.0):
        """画像を1枚描画する"""
        if not self.visible:
            return

        # カメラの移動量に parallax_factor を反映
        # カメラの中心（local_position）を取得し、オフセットを計算
        camera_pos = camera.transform.local_position
        offset = camera_pos * (1 - parallax_factor)
        # 実際に描画したいワールド位置
        base_world_pos = self.transform.global_position - offset

        # ワールド→スクリーン座標変換
        # あなたの Camera 実装が (screen_pos, scale) のタプルを返すならそれに合わせる
        screen_pos, _ = camera.world_to_screen(base_world_pos)

        # 画像を描画
        # （回転が必要ならさらに Transform の rotation を加味して回転 transform する）
        rect = self.image.get_rect(center=(screen_pos.x, screen_pos.y))
        surface.blit(self.image, rect)
