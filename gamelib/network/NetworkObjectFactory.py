class NetworkObjectFactory:
    _registry = {}  # クラスの登録用辞書

    @classmethod
    def register_class(cls, target_class):
        """オブジェクトクラスを登録する"""
        NetworkObjectFactory._registry[target_class.__name__] = target_class


    @classmethod
    def create_object(cls, class_name, object_name, network_id=None, steam_id=None, **kwargs):
        """クラス名からオブジェクトを生成"""
        if class_name not in cls._registry:
            print(f"⚠️ クラス '{class_name}' が登録されていません。")
            return None

        # 登録されたクラスからインスタンスを生成
        obj_class = cls._registry[class_name]
        obj = obj_class(name=object_name, network_id=network_id, steam_id=steam_id, **kwargs)

        return obj
