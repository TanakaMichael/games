class Layer:
    def __init__(self, name, parallax_factor=1.0, visible=True):
        self.name = name
        self.parallax_factor = parallax_factor
        self.visible = visible
        self.objects = []  # LayerObject や他のオブジェクトを格納

    def add_object(self, layer_object):
        self.objects.append(layer_object)

    def remove_object(self, layer_object):
        if layer_object in self.objects:
            self.objects.remove(layer_object)

    def update(self, delta_time):
        for obj in self.objects:
            if hasattr(obj, "update"):
                obj.update(delta_time)

    def render(self, surface, camera):
        if not self.visible:
            return

        for obj in self.objects:
            # LayerObject の render に parallax_factor を渡す
            obj.render(surface, camera, parallax_factor=self.parallax_factor)
