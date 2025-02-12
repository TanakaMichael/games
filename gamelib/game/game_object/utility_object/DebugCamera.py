# デバッグ用のカメラ
from ...core.Camera import Camera
from ...InputManager import InputManager

class DebugCamera(Camera):
    def __init__(self, canvas, zoom = 1):
        super().__init__(canvas, zoom=zoom)
        self.input_manager = InputManager.get_instance()

        self.up = self.input_manager.get_action("MoveUp")
        self.down = self.input_manager.get_action("MoveDown")
        self.left = self.input_manager.get_action("MoveLeft")
        self.right = self.input_manager.get_action("MoveRight")

        self.move_speed = 100.0  # 移動速度 [m/s]

    def update(self, dt):
        super().update(dt)

        if self.up.get_on_hold():
            self.transform.local_position.y -= self.move_speed * dt
        if self.down.get_on_hold():
            self.transform.local_position.y += self.move_speed * dt
        if self.left.get_on_hold():
            self.transform.local_position.x -= self.move_speed * dt
        if self.right.get_on_hold():
            self.transform.local_position.x += self.move_speed * dt
        