class NetIDGenerator:
    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.reset_net_id()

    def reset_net_id(self):
        self.last_network_id = 0
        self.last_scene_network_id = 0
    def generate_id(self):
        self.last_network_id += 1
        return self.last_network_id