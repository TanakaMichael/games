import pygame
from ..UIAnimation import UIAnimation
from ...utility.Coroutine import WaitForSeconds
import math
from .MoveAnimation import ease_in_out_sine, ease_out_quad
class FadeAnimation(UIAnimation):
    """UIObject の透明度を変化させるアニメーション"""
    def __init__(self, ui_object, start_alpha=255, target_alpha=0, duration=1.0, ease_function=None):
        super().__init__(ui_object)
        self.start_alpha = start_alpha
        self.target_alpha = target_alpha
        self.duration = duration
        self.ease_function = ease_function or (lambda t: t)  # 線形補間がデフォルト

    def fade_in(self, duration=1.0, ease_function=None):
        self.start_alpha = 0
        self.target_alpha = 255
        self.duration = duration
        self.ease_function = ease_function or ease_out_quad
        self.start()

    def fade_out(self, duration=1.0, ease_function=None):
        self.start_alpha = 255
        self.target_alpha = 0
        self.duration = duration
        self.ease_function = ease_function or ease_out_quad
        self.start()

    def fade_animation(self):
        elapsed = 0
        while elapsed < self.duration:
            elapsed += yield WaitForSeconds(0.01)
            t = min(elapsed / self.duration, 1.0)
            eased_t = self.ease_function(t)
            alpha = int(self.start_alpha + (self.target_alpha - self.start_alpha) * eased_t)

            # **アルファ値の適用**
            if hasattr(self.ui_object, "set_alpha"):
                self.ui_object.set_alpha(alpha)

    def start(self):
        self.start_animation(self.fade_animation)
