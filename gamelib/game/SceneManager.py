from .utility.Global import Global

class SceneManager(Global):
    def __init__(self):
        if SceneManager._instance is not None:
            raise Exception("SceneManager is a singleton!")
        super().__init__()

        self.scenes = {}
        self.current_scene = None

    def add_scene(self, scene):
        """sceneを追加する"""
        if scene.name in self.scenes:
            raise Exception(f"Scene '{scene.name}' already exists!")
        self.scenes[scene.name] = scene

    def get_current_scene(self):
        """現在のシーンを返す"""
        return self.current_scene
    def get_scene(self, scene_name):
        return self.scenes[scene_name]

    def set_active_scene(self, name, **kwargs):
        """シーンをアクティブにする"""
        if name not in self.scenes:
            raise Exception(f"Scene '{name}' does not exist!")
        if self.current_scene is not None:
            self.current_scene.end()
        self.current_scene = self.scenes[name]
        self.start_scene(**kwargs)
        return self.current_scene
    
    def start_scene(self, **kwargs):
        """sceneにスタートを伝える"""
        self.current_scene.start(**kwargs)
    def start_objects(self):
        for camera in self.current_scene.cameras:
            if hasattr(camera, "start"):
                camera.start()
        for objects in self.current_scene.objects:
            if hasattr(objects, "start"):
                objects.start()
    def update(self, dt):
        """シーンの更新"""
        if self.current_scene is not None:
            self.current_scene.update(dt)
    def render(self, screen):
        """シーンのレンダリング"""
        if self.current_scene is not None:
            self.current_scene.render(screen)
    def handle_event(self, event):
        """シーンにイベントを処理させる"""
        if self.current_scene is not None:
            self.current_scene.handle_event(event)