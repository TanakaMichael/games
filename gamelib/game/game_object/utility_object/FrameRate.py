from ..Panel import Panel
from ...ui.ui_objects.MeshText import MeshText

class FrameRate(Panel):
    def __init__(self, canvas, name="FrameRate", active = True):
        super().__init__(canvas, name, active)
        self.frame_rate = MeshText(canvas, "frome_rate", font_height=50,position=("right-175", "top+100"))
        self.canvas.add_ui(self.frame_rate)
        self.alpha = 0.01  # 移動平均の重み (1 に近いほど最新値を重視)
        self.fps_smooth = 0.0  # 移動平均の fps

    def update(self, dt):
        super().update(dt)
        if dt > 0:
            instant_fps = 1.0 / dt
            self.fps_smooth = (self.alpha * instant_fps) + ((1 - self.alpha) * self.fps_smooth)
            self.frame_rate.set_text(f"{self.fps_smooth:.1f}f/s")