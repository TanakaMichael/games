from ..ui.Canvas import Canvas
from ..utility.Coroutine import CoroutineManager
class Scene:
    def __init__(self, name, screen):
        self.name = name
        self.screen = screen
        self.coroutine_manager = CoroutineManager()

        self.canvas = Canvas(screen)
        self.objects = []
        self.cameras = []
        self.active = False

    def add_object(self, obj):
        self.objects.append(obj)
        obj.set_scene(self)
        return obj
    def remove_object(self, obj):
        self.objects.remove(obj)
    def add_camera(self, camera):
        self.cameras.append(camera)
        camera.set_scene(self)
        return camera
    def remove_camera(self, camera):
        self.cameras.remove(camera)
    def get_object(self, name):
        for obj in self.objects:
            if obj.name == name:
                return obj
    def update(self, dt):
        if not self.active:
            return
        self.coroutine_manager.update(dt)
        for obj in self.objects:
            obj.update(dt)
        for camera in self.cameras:
            if hasattr(camera, "update"):
                camera.update(dt)
                camera.clicked_sprite(self.objects)
        self.canvas.update(dt)

    def render(self, screen):
        if not self.active:
            return
        for camera in self.cameras:
            camera.render_back_layers(screen)
            camera.render_objects(screen, self.objects)
            camera.render_front_layers(screen)
        self.canvas.render(screen)
    def handle_event(self, event):
        if not self.active:
            return
        for camera in self.cameras:
            if hasattr(camera, "handle_event"):
                camera.handle_event(event)
        for obj in self.objects:
            if hasattr(obj, "handle_event"):
                obj.handle_event(event)

        self.canvas.handle_event(event)


    def start(self, **kwargs):
        """sceneが開始した時に呼び出される"""
        # sceneに渡したい変数があればkwargsに入力する
        self.active = True
        for camera in self.cameras:
            if hasattr(camera, "start"):
                camera.start()
        for objects in self.objects:
            if hasattr(objects, "start"):
                objects.start()
    def end(self):
        self.active = False
        for camera in self.cameras:
            if hasattr(camera, "end"):
                camera.end()
        for objects in self.objects:
            if hasattr(objects, "end"):
                objects.end()