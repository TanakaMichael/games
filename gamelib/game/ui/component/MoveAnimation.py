import pygame
from ..UIAnimation import UIAnimation
from ...utility.Coroutine import WaitForSeconds
import math

# **イージング関数**
def ease_out_quad(t):
    return 1 - (1 - t) ** 2  # **ゆっくり開始、速く移動**

def ease_in_out_sine(t):
    return 0.5 * (1 - math.cos(math.pi * t))  # **シンプルなイージング**

class MoveAnimation(UIAnimation):
    """UIObject を移動させるアニメーション"""
    def __init__(self, ui_object, target_position=pygame.Vector2(0,0), duration=1.0, ease_function=None, finish_animation=None):
        """
        :param ui_object: 移動対象の `UIObject`
        :param target_position: 目標位置 (キャンバス内のローカル座標)
        :param duration: 移動時間 (秒)
        :param ease_function: イージング関数 (デフォルトなし)
        """
        super().__init__(ui_object)
        self.target_position = ui_object.canvas._parse_position(target_position)
        self.duration = duration
        self.ease_function = ease_function or (lambda t: t)  # **デフォルトは線形補間 (t: 0 ~ 1)**

        self.finish_animation = finish_animation

        self.delta_position = pygame.Vector2(0, 0)
        self.original_position = self.ui_object.rect_transform.local_position.copy()

    def start_to_target_animation(self, target_position, duration=1.0, ease_function=None):
        """目標位置へ移動"""
        self.target_position = self.ui_object.canvas._parse_position(target_position)
        self.duration = duration
        self.ease_function = ease_function or ease_in_out_sine
        self.original_position = self.ui_object.rect_transform.local_position.copy()
        self.start(True)  

    def start_to_current_animation(self, start_position, duration=1.0, ease_function=None):
        """目標位置から現在位置へのアニメーション"""
        self.target_position = self.ui_object.rect_transform.local_position.copy()
        self.ui_object.rect_transform.set_local_position(start_position)
        self.original_position = self.ui_object.rect_transform.local_position.copy()
        self.start_to_target_animation(self.target_position, duration, ease_function)

    def start_to_delta_animation(self, delta_position, duration=1.0, ease_function=None):
        """現在の位置からデルタ値移動 (一時的な座標変更)"""
        self.delta_position += self.ui_object.canvas._parse_position(delta_position)
        self.target_position = self.original_position + self.delta_position
        self.duration = duration
        self.ease_function = ease_function or ease_in_out_sine
        self.start()

    def return_to_delta_animation(self, duration=1.0, ease_function=None):
        """デルタ値の影響をリセット"""
        self.target_position = self.original_position
        self.duration = duration
        self.ease_function = ease_function or ease_in_out_sine
        self.start()
        self.delta_position = pygame.Vector2(0, 0)  

    def move_animation(self, save_original=False):
        """アニメーションのコルーチン"""
        start_pos = self.ui_object.rect_transform.local_position.copy()  
        elapsed = 0

        while elapsed < self.duration:
            elapsed += yield WaitForSeconds(0.01)  
            t = min(elapsed / self.duration, 1.0)  
            eased_t = self.ease_function(t)  

            # **線形補間 (Lerp) を適用**
            self.ui_object.rect_transform.set_local_position(start_pos.lerp(self.target_position, eased_t))

        if save_original:
            self.original_position = self.target_position.copy()
        if self.finish_animation:
            self.finish_animation()

    def start(self, save_original=False):
        """アニメーションを開始"""
        self.start_animation(self.move_animation, save_original)
