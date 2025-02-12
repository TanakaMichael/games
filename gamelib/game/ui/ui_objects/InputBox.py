import pygame
from .MeshButtonText import MeshButtonText
from ..ui_elements.Text import Text

class InputBox(MeshButtonText):
    def __init__(self, canvas, name, position, default_text="", font_path=None, font_height=100,
                 input_color=(128, 128, 128), confirmed_color=(255, 255, 255),
                 placeholder_color=(128, 128, 128), max_chars=None, background_size=None, **kwargs):
        """
        :param max_chars: 入力可能な最大文字数（None の場合は制限なし）
        """
        super().__init__(canvas, name, position, ui_text="",
                         font_path=font_path, font_height=font_height,
                         fixed_background_size=background_size, font_alignment="right", **kwargs)

        # 入力バッファとプレースホルダーの設定
        self.buffer = ""         # 確定済みの文字列
        self.composition = ""    # 未確定（編集中）の文字列
        self.default_text = default_text
        self.is_selected = False

        # カラー設定
        self.input_color = pygame.Color(*input_color)         # 未確定文字の色（全角入力中）
        self.placeholder_color = pygame.Color(*placeholder_color)
        self.confirmed_color = pygame.Color(*confirmed_color)   # 確定済み文字の色
        self.max_chars = max_chars  # None の場合は文字数制限なし

        # 初期状態：プレースホルダー表示
        self.text_obj = self.ui_text
        self.text_obj.set_text(self.default_text)
        self.text_obj.set_color(self.placeholder_color)
    
    def _update_text_obj(self):
        """
        buffer と composition を連結して ui_text に設定し、  
        confirmed_color で buffer 部分、input_color で composition 部分の色を適用する。
        ※ set_color(color, start, length) が使用可能な前提
        """
        full_text = self.buffer + self.composition
        self.text_obj.set_text(full_text)
        # 確定部分の色を設定
        self.text_obj.set_color(self.confirmed_color, 0, len(self.buffer))
        # 未確定部分があれば input_color を適用
        if self.composition:
            self.text_obj.set_color(self.input_color, len(self.buffer), len(self.composition))
    
    def on_pressed(self):
        """クリック時に呼ばれる（選択状態にしてテキスト入力を開始）"""
        self.is_selected = True
        # IME 対応のため TEXTINPUT/TEXTEDITING イベントを有効化
        pygame.key.start_text_input()
        # 編集開始時、buffer が空ならプレースホルダーをクリア
        if self.buffer == "":
            self.text_obj.set_text("")
    
    def on_unselected(self):
        """選択解除時の処理（入力確定後の表示処理）"""
        self.is_selected = False
        pygame.key.stop_text_input()
        # 確定処理：composition が残っていたら buffer に追加
        if self.composition:
            addition = self.composition
            if self.max_chars is not None:
                allowed = self.max_chars - len(self.buffer)
                addition = addition[:allowed]
            self.buffer += addition
        self.composition = ""
        
        if self.buffer == "":
            # 入力がなければプレースホルダー表示
            self.text_obj.set_text(self.default_text)
            self.text_obj.set_color(self.placeholder_color)
        else:
            # buffer の内容を確定色で表示
            self.text_obj.set_text(self.buffer)
            self.text_obj.set_color(self.confirmed_color)
    
    def handle_event(self, event):
        """イベント処理（キーボード・マウスなど）"""
        super().handle_event(event)
        if self.is_selected:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Enter キーで確定
                    if self.composition:
                        # 未確定部分をまず buffer に反映（max_chars を考慮）
                        addition = self.composition
                        if self.max_chars is not None:
                            allowed = self.max_chars - len(self.buffer)
                            addition = addition[:allowed]
                        self.buffer += addition
                        self.composition = ""
                    print(f"入力確定: {self.buffer}")
                    self.on_unselected()
                elif event.key == pygame.K_BACKSPACE:
                    if self.composition:
                        self.composition = self.composition[:-1]
                    else:
                        self.buffer = self.buffer[:-1]
                    self._update_text_obj()
            elif event.type == pygame.TEXTEDITING:
                # 未確定の文字列（IME入力中）の更新
                comp_text = event.text
                if self.max_chars is not None:
                    allowed = self.max_chars - len(self.buffer)
                    comp_text = comp_text[:allowed]
                self.composition = comp_text
                self._update_text_obj()
            elif event.type == pygame.TEXTINPUT:
                # TEXTINPUT は確定入力（IMEで確定時または半角入力）として扱う
                addition = event.text
                if self.max_chars is None or len(self.buffer) + len(addition) <= self.max_chars:
                    self.buffer += addition
                else:
                    if self.max_chars is not None:
                        allowed = self.max_chars - len(self.buffer)
                        self.buffer += addition[:allowed]
                self.composition = ""
                self._update_text_obj()
        
        # マウスクリックがウィジェット外の場合は選択解除（入力確定）する
        if event.type == pygame.MOUSEBUTTONDOWN and not self.is_hovered:
            self.on_unselected()
        elif event.type == pygame.VIDEORESIZE:
            if self.buffer or self.composition:
                self._update_text_obj()
            else:
                self.text_obj.set_text(self.default_text)
    
    def update(self, dt):
        """
        更新処理。
        MeshButtonText により背景はテキストサイズに合わせて更新されるため、
        update 内でカーソル表示などは行いません。
        """
        super().update(dt)
    
    def get_value(self):
        """現在の入力値（確定済みの buffer）を取得"""
        return self.buffer
