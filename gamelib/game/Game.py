from .utility.Global import Global

class Game(Global):
    def __init__(self):
        if Game._instance is not None:
            raise Exception("Game はシングルトンです。`get_instance()` を使用してください")
        super().__init__()
        self.initialize()
    def initialize(self):
        from gamelib.game.GlobalEventManager import GlobalEventManager
        from gamelib.network.NetworkManager import NetworkManager
        from gamelib.network.syncs.NetworkSceneManager import NetworkSceneManager
        from gamelib.game.InputManager import InputManager

        self.global_event_manager = GlobalEventManager.get_instance()
        self.network_manager = NetworkManager.get_instance()
        self.scene_manager = NetworkSceneManager.get_instance()
        self.input_manager = InputManager.get_instance()

        self.network_manager.set_singleton(self.scene_manager,self.global_event_manager)

        self.instances = [self.scene_manager, self.input_manager, self.network_manager, self.global_event_manager]

    def update(self, dt):
        for instance in self.instances:
            if hasattr(instance, "update"):
                instance.update(dt)
    def render(self, screen):
        for instance in self.instances:
            if hasattr(instance , "render"):
                instance.render(screen)
    def handle_event(self, event):
        for instance in self.instances:
            if hasattr(instance, "handle_event"):
                instance.handle_event(event)