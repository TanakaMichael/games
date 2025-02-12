import pygame
from ..LayerObject import LayerObject

class Background(LayerObject):
    """
    タイル化して背景をループ描画する LayerObject。
    tile_x=True / tile_y=True で 水平・垂直 いずれもループ可能。
    """
    def __init__(self, image_path, transform=None, tile_x=True, tile_y=False, visible=True):
        super().__init__(image_path, transform, visible)
        self.tile_x = tile_x
        self.tile_y = tile_y

    def render(self, surface, camera, parallax_factor=1.0):
        if not self.visible:
            return

        # 修正ポイント: カメラ位置に parallax_factor を直接掛ける
        camera_pos = camera.transform.local_position
        offset = camera_pos * parallax_factor

        # 背景の基準位置（カメラオフセットを適用）
        base_world_pos = self.transform.global_position - offset
        screen_pos, _ = camera.world_to_screen(base_world_pos)

        img_w = self.image.get_width()
        img_h = self.image.get_height()
        screen_w, screen_h = surface.get_size()

        # タイル描画の開始位置
        start_x = screen_pos.x
        start_y = screen_pos.y

        # タイルループのために % 演算を適用
        if self.tile_x:
            start_x = (start_x % img_w) - img_w
        if self.tile_y:
            start_y = (start_y % img_h) - img_h

        # タイル描画
        y = start_y
        while y < screen_h:
            x = start_x
            while x < screen_w:
                surface.blit(self.image, (x, y))
                x += img_w
            y += img_h
