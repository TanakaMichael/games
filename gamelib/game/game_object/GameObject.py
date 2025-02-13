from ..utility.EventManager import EventManager
from ..utility.Coroutine import CoroutineManager
from ..component.Component import Component
from ..component.Transform import Transform
from ..component.Component import Component
class GameObject:
    def __init__(self, name, active=False, parent=None):
        self.name = name
        self.components = {} # コンポーネント辞書(重複不可)
        self.event_manager = EventManager()
        self.coroutine_manager = CoroutineManager()

        self.children = []
        self.scene = None
        self.set_active(active)

        self.layer = 1
        self.needs_sorting = False  # **ソートが必要かどうか**

        # **デフォルトで Transform を追加**
        self.transform = self.add_component(Transform, parent=parent.transform if parent else None)
        # **親子関係をセット**
        self.parent = parent
    def start(self):
        pass
    def end(self):
        pass
    def add_child(self, child_object):
        """子オブジェクトを追加し、ソートをトリガー"""
        if isinstance(child_object, GameObject):
            self.children.append(child_object)
            child_object.parent = self
            child_object.transform.set_parent(self.transform)
            self.needs_sorting = True  # **新しく追加したらソートが必要**
            return child_object
        else:
            raise ValueError("子オブジェクトは GameObject である必要があります")

    def remove_child(self, child_object):
        """子オブジェクトを削除し、ソートをトリガー"""
        if child_object in self.children:
            self.children.remove(child_object)
            self.needs_sorting = True  # **削除したらソートが必要**
    def set_parent(self, parent):
        self.parent = parent
    def add_component(self, component_class, *args, **kwargs) -> Component:
        """コンポーネントを追加"""
        component = component_class(self, *args, **kwargs)
        self.components[component_class.__name__] = component
        return component

    def get_component(self, component_class):
        if component_class.__name__ in self.components:
            return self.components[component_class.__name__]

        # キャッシュされていない場合、基底クラスも含めて探索
        for comp in self.components.values():
            if isinstance(comp, component_class):
                return comp
        return None
    def update(self, delta_time):
        """親の影響を考慮しつつ更新"""
        if not self.active:
            return

        # **自身の Transform を更新**
        self.transform.update_transform()

        # **コンポーネントの更新**
        for component in self.components.values():
            component.update(delta_time)

        # **コルーチンの更新**
        self.coroutine_manager.update(delta_time)

        # **子オブジェクトの更新**
        if self.needs_sorting:
            self.sort_children()  # **必要ならソート**
        for child in self.children:
            child.update(delta_time)

    def handle_event(self, event):
        """イベント処理"""
        for component in self.components.values():
            component.handle_event(event)

        for child in self.children:
            child.handle_event(event)

    def set_scene(self, scene):
        """シーンを設定"""
        self.scene = scene
        for child in self.children:
            child.set_scene(scene)
    def set_active(self, active):
        """有効状態を設定"""
        self.active = active
        self.visible = active
        self.on_active()
        for child in self.children:
            child.set_active(active)
            child.on_active()

    def on_active(self):
        """有効化時のイベント"""
        pass

    def register_event(self, event_name, callback):
        """ローカルイベントを登録"""
        self.event_manager.register_event(event_name, callback)

    def trigger_event(self, event_name, **kwargs):
        """ローカルイベントを発火"""
        self.event_manager.trigger_event(event_name, **kwargs)

    def sort_children(self):
        """子オブジェクトをレイヤーとZ軸でソート"""
        self.children.sort(key=lambda obj: (obj.layer, obj.transform.global_position.z))
        self.needs_sorting = False  # **ソート完了後、フラグをリセット**
    def render(self, surface, camera):
        """GameObjectを描画 (子オブジェクトをZ値 & レイヤーでソート)"""
        if not self.visible:
            return 

        for component in self.components.values():
            component.render(surface, camera)

        # **ソートが必要なら実行**
        if self.needs_sorting:
            self.sort_children()

        # **ソート済みの順番で子オブジェクトを描画**
        for child in self.children:
            child.render(surface, camera)