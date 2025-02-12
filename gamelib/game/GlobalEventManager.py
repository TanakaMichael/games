from .utility.EventManager import EventManager
from .utility.Global import Global

class GlobalEventManager(EventManager, Global):
    """グローバル環境でのイベントを登録/発動する"""
    def __init__(self):
        if GlobalEventManager._instance is not None:
            raise Exception("エラー : グローバルイベントはsingletonです")
        super().__init__()