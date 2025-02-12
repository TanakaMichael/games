class Global:
    """すべてのシングルトンが継承する基底クラス"""
    _instance = None

    @classmethod
    def get_instance(cls):
        """シングルトンインスタンスを取得し、Game に登録"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
