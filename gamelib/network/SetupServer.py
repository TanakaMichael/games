import threading

class SetupServer:
    def __init__(self, network_manager):
        self.network_manager = network_manager

    def run(self, distance, max_player):
        lobby_id = self.network_manager.steam.create_lobby(distance, max_player)
        if lobby_id == 0:
            return False

        server_steam_id = self.network_manager.steam.steam_id
        local_steam_id = self.network_manager.steam.steam_id

        self.network_manager.set_network_ids(lobby_id, server_steam_id, local_steam_id, True, False)
        self.network_manager.running = True

        self.network_manager.start_thread(self.network_manager._receive_messages)
        self.network_manager.global_event_manager.trigger_event("SetupServer")
        return True
