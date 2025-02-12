import pygame
import json
import os
from .utility.Global import Global

SPECIAL_NAME = {
    "SPACE": "SPACE",
    "RETURN": "RETURN",
    "ENTER": "RETURN",
    "ESCAPE": "ESCAPE",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "UP": "UP",
    "DOWN": "DOWN",
    "BUTTON_LEFT": "BUTTON_LEFT",
    "BUTTON_RIGHT": "BUTTON_RIGHT",
    "SCROLL_UP": "SCROLL_UP",
    "SCROLL_DOWN": "SCROLL_DOWN"
}


class Action:
    """特定の入力アクションを管理するクラス"""
    def __init__(self, name):
        self.name = name
        self.is_pressed = False      # 現在押されているか
        self.was_pressed = False     # 押された瞬間
        self.was_released = False    # 離された瞬間

        # イベントリスナー
        self.listeners = {"on_press": [], "on_hold": [], "on_release": []}

    def update(self, is_pressed):
        """アクションの状態を更新"""
        self.was_pressed = not self.is_pressed and is_pressed
        self.was_released = self.is_pressed and not is_pressed
        self.is_pressed = is_pressed

        # 状態に応じてイベント発火
        if self.was_pressed:
            self.trigger_event("on_press")
        if self.is_pressed:
            self.trigger_event("on_hold")
        if self.was_released:
            self.trigger_event("on_release")

    def trigger_event(self, event_type):
        """登録されたイベントリスナーを呼び出す"""
        for callback in self.listeners.get(event_type, []):
            callback(self.name)

    def register_event(self, event_type, callback):
        """イベントリスナーを登録"""
        if event_type in self.listeners:
            self.listeners[event_type].append(callback)

    def unregister_event(self, event_type, callback):
        """イベントリスナーを解除"""
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)

    # 状態確認メソッド
    def get_on_press(self):
        return self.was_pressed

    def get_on_hold(self):
        return self.is_pressed

    def get_on_release(self):
        return self.was_released


class InputManager(Global):
    """イベント駆動型 singleton"""

    # Action名 : 対応Input pygame.event.K_{}
    DEFAULT_BINDINGS = {
        "MoveUp": "w",
        "MoveDown": "s",
        "MoveLeft": "a",
        "MoveRight": "d",
        "MouseLeft": "BUTTON_LEFT",
        "MouseRight": "BUTTON_RIGHT",
        "ScrollUp": "SCROLL_UP",
        "ScrollDown": "SCROLL_DOWN"
    }

    def __init__(self):
        if InputManager._instance is not None:
            raise Exception("InputManager is a singleton!")
        super().__init__()

        self.config_path = "gamelib/config/input_bindings.txt"
        self.bindings = self.load_bindings()
        self.actions = {name: Action(name) for name in self.bindings}  # アクション管理
        self.held_keys = set()  # 現在押されているキーのセット

    def load_bindings(self):
        """キーバインドをロード (無ければデフォルト)"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return self.DEFAULT_BINDINGS.copy()

    def save_bindings(self, action_name, key):
        """キーバインドを保存"""
        self.bindings[action_name] = key
        with open(self.config_path, "w") as f:
            json.dump(self.bindings, f, indent=4)
    def get_action_key(self, action):
        """アクション名から対応する pygame キーコードを取得"""
        key_name = self.bindings.get(action, "")

        if key_name.upper() in SPECIAL_NAME:
            key_name = SPECIAL_NAME[key_name.upper()]  # **特殊キーを大文字に変換**
            if key_name.startswith("BUTTON_"):
                return getattr(pygame, key_name, None)
        else:
            key_name = key_name.lower()  # **通常のキー（A-Z）は小文字に変換**

        return getattr(pygame, f"K_{key_name}", None) if key_name else None

    def get_action(self, action_name):
        """Action インスタンスを取得"""
        return self.actions.get(action_name, None)

    def handle_event(self, event):
        """入力の監視 & アクションの更新"""
        for action_name, key in self.bindings.items():
            mapped_key = self.get_action_key(action_name)

            if event.type == pygame.KEYDOWN and event.key == mapped_key:
                self.held_keys.add(action_name)
                self.actions[action_name].update(True)

            elif event.type == pygame.KEYUP and event.key == mapped_key:
                self.held_keys.discard(action_name)
                self.actions[action_name].update(False)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == mapped_key:
                self.held_keys.add(action_name)
                self.actions[action_name].update(True)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == mapped_key:
                self.held_keys.discard(action_name)
                self.actions[action_name].update(False)

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.actions["ScrollUp"].update(True)
                elif event.y < 0:
                    self.actions["ScrollDown"].update(True)

    def update(self, dt):
        """フレームごとにアクションの状態を更新"""
        for action in self.actions.values():
            action.update(action.name in self.held_keys)
