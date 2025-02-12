from ..utility.Coroutine import CoroutineManager, WaitForSeconds
from .UIComponent import UIComponent
class UIAnimation(UIComponent):
    """UI アニメーションの基底クラス（コルーチンを利用）"""
    def __init__(self, ui_element):
        super().__init__(ui_element)
        self.coroutine_manager = CoroutineManager()
        self.running_coroutines = []

    def start_animation(self, animation_func, *args):
        """アニメーションを開始"""
        coroutine = self.coroutine_manager.start_coroutine(animation_func, *args)
        self.running_coroutines.append(coroutine)

    def stop_animation(self):
        """すべてのアニメーションを停止"""
        for coroutine in self.running_coroutines:
            self.coroutine_manager.stop_coroutine(coroutine)
        self.running_coroutines.clear()

    def update(self, delta_time):
        """アニメーションの更新処理"""
        super().update(delta_time)
        self.coroutine_manager.update(delta_time)
