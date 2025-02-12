import pygame
from ..game_object.GameObject import GameObject
from .LayerManager import LayerManager
from ..InputManager import InputManager
from ..component.Sprite import Sprite
from ..component.Clickable import Clickable

class Camera(GameObject):
    def __init__(self, canvas, camera_view_size=100, canvas_view_rect=None, zoom=1, name="camera"):
        super().__init__(name, True)
        self.canvas = canvas
        self.camera_view_size = camera_view_size
        self.zoom = zoom
        self.layer_manager = LayerManager()
        self.input_manager = InputManager.get_instance()

        self.mouse_left_action = self.input_manager.get_action("MouseLeft")

        self.depth_constant = 0.1

        if canvas_view_rect is None:
            self.canvas_rect = pygame.Rect((0, 0), self.canvas.get_window_size())
        else:
            self.canvas_rect = canvas_view_rect

        self._cached_letterbox_rect = None
        self._cached_letterbox_scale = None
        self._cached_canvas_rect = None

    # --- レターボックス関数 ---
    def get_letterbox_rect(self):
        target_aspect = self.canvas.get_window_size().x / self.canvas.get_window_size().y
        canvas_aspect = self.canvas_rect.width / self.canvas_rect.height

        if abs(target_aspect - canvas_aspect) < 1e-5:
            return self.canvas_rect.copy()
        elif target_aspect > canvas_aspect:
            new_width = self.canvas_rect.width
            new_height = int(new_width / target_aspect)
            offset_y = (self.canvas_rect.height - new_height) // 2
            return pygame.Rect(self.canvas_rect.x, self.canvas_rect.y + offset_y, new_width, new_height)
        else:
            new_height = self.canvas_rect.height
            new_width = int(new_height * target_aspect)
            offset_x = (self.canvas_rect.width - new_width) // 2
            return pygame.Rect(self.canvas_rect.x + offset_x, self.canvas_rect.y, new_width, new_height)

    def get_letterbox_scale(self):
        lb_rect = self.get_letterbox_rect()
        scale_x = lb_rect.width / self.canvas.get_window_size().x
        scale_y = lb_rect.height / self.canvas.get_window_size().y
        return pygame.Vector2(scale_x, scale_y)

    def get_letterbox_rect_cached(self):
        if self._cached_canvas_rect != self.canvas_rect:
            self._cached_letterbox_rect = self.get_letterbox_rect()
            self._cached_letterbox_scale = self.get_letterbox_scale()
            self._cached_canvas_rect = self.canvas_rect.copy()
        return self._cached_letterbox_rect, self._cached_letterbox_scale

    # --- 主要な座標変換 ---
    def world_to_screen(self, world_position):
        """
        カメラの transform（中心）を基準として、ワールド座標をスクリーン座標に変換。
        """
        center = self.transform.get_local_position()
        rel = pygame.Vector2(world_position.x - center.x, world_position.y - center.y)
        lb_scale = self.get_letterbox_scale()

        # 深度（z）の取得とスケール計算
        z = world_position.z if hasattr(world_position, 'z') else 0
        depth_scale = 1 / (1 + self.depth_constant * z) if z >= 0 else 1 + (self.depth_constant * abs(z))

        # 座標変換（ズーム・スケール適用）
        screen_x = rel.x * self.zoom * lb_scale.x * depth_scale
        screen_y = rel.y * self.zoom * lb_scale.y * depth_scale

        # 深度オフセット
        screen_y += z * 5  

        # レターボックス補正
        lb_rect = self.get_letterbox_rect()
        screen_x += lb_rect.centerx
        screen_y += lb_rect.centery

        return pygame.Vector2(int(screen_x), int(screen_y)), depth_scale

    def screen_to_world(self, screen_position):
        """
        スクリーン座標からワールド座標に変換。
        """
        lb_scale = self.get_letterbox_scale()
        lb_rect = self.get_letterbox_rect()
        center = self.transform.get_local_position()

        rel_x = (screen_position.x - lb_rect.centerx) / (self.zoom * lb_scale.x)
        rel_y = (screen_position.y - lb_rect.centery) / (self.zoom * lb_scale.y)

        return pygame.Vector2(rel_x + center.x, rel_y + center.y)
    def clicked_sprite(self, game_objects):
        mouse_pos = self.canvas.to_canvas_position(*pygame.mouse.get_pos())
        if self.mouse_left_action.get_on_press():
            clicked_sprites = []
            sprites = [go.get_component(Sprite) for go in game_objects if go.get_component(Sprite) and go.get_component(Clickable)]
            for sprite in sprites:
                # ここでは、各スプライトが render() 内で self.render_rect を設定していると仮定
                if hasattr(sprite, 'render_rect') and sprite.render_rect.collidepoint(mouse_pos):
                    clicked_sprites.append(sprite)

                if not clicked_sprites:
                    return None

                # 複数ある場合、transform.global_position.z が最も低いもの（手前にあるもの）を選択する
                # ※ ※プロジェクトによって「手前」の定義は異なりますが、ここでは z 値が低いほど手前と仮定
                clicked_sprites.sort(key=lambda spr: spr.transform.global_position.z)
                clickable = sprite.game_object.get_component(Clickable)
                clickable.on_left_click()

    # --- カメラの拡大縮小 ---
    def get_camera_scale(self):
        scale_x = (self.canvas_rect.width * self.zoom) / self.canvas.get_window_size().x
        scale_y = (self.canvas_rect.height * self.zoom) / self.canvas.get_window_size().y
        return pygame.Vector2(scale_x, scale_y)

    def set_zoom(self, new_zoom):
        self.zoom = max(0.1, new_zoom)

    # --- レイヤーの描画 ---
    def render_back_layers(self, screen):
        self.layer_manager.render_back_layers(screen, self)

    def render_front_layers(self, screen):
        self.layer_manager.render_front_layers(screen, self)

    def render_objects(self, screen, objects):
        # オブジェクトの z 座標、次いでレイヤー順にソート
        sorted_objects = sorted(
            objects,
            key=lambda obj: (obj.transform.global_position.z, getattr(obj, 'layer', 0))
        )
        for obj in sorted_objects:
            obj.render(screen, self)
