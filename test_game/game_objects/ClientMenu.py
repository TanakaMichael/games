from gamelib.game.game_object.Panel import Panel
from gamelib.game.ui.ui_objects.MeshButtonText import MeshButtonText
from gamelib.game.ui.ui_objects.InputBox import InputBox
from gamelib.game.ui.component.FadeAnimation import FadeAnimation
from gamelib.game.ui.component.MoveAnimation import MoveAnimation
from gamelib.game.ui.ui_objects.MeshList import MeshList
from gamelib.game.ui.ui_objects.MeshText import MeshText

from gamelib.game.GlobalEventManager import GlobalEventManager

from gamelib.network.NetworkManager import NetworkManager
class ClientMenu(Panel):
    def __init__(self, canvas, name, active=False, parent=None):
        super().__init__(canvas, name, active, parent)
        self.global_event_manager = GlobalEventManager.get_instance()
    def start(self):
        super().start()
        self.network_manager = NetworkManager.get_instance()
        data = ["hello", "world", "3", "4nanoka", "残念5でした"]
        self.lobby_list = self.add_ui(MeshList(self.canvas, name="LobbyList", position=("center", "top+300"), on_item_click=self.on_lobby_click, item_data=data, max_visible_items=3))
        self.public_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="Public", position=("center+200", "top+120"), ui_text="Public", font_height=80, font_alignment="center", correction_background_scale=(1.2,1.2), fixed_background_size=(300, 80)))
        self.friend_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="Friend", position=("center-200", "top+120"), ui_text="Friend", font_height=80, font_alignment="center", correction_background_scale=(1.2,1.2), fixed_background_size=(300, 80)))
        
        self.return_btn = self.add_ui(MeshButtonText(canvas=self.canvas, name="return", position=("left+120", "top+120"), ui_text="Return", font_height=30, font_alignment="center", correction_background_scale=(1.2,1.2)))
        
        self.state_text = self.add_ui(MeshText(self.canvas, "State", "KH-Dot-Dougenzaka-12.ttf", position=("right-400", "bottom+120")))
        self.public_btn.on_click = self.on_public_click
        self.friend_btn.on_pressed = self.on_friend_click
        self.return_btn.on_click = self.on_return_click
    def on_lobby_click(self, index, lobby):
        lobby_id = extract_lobby_ids(lobby)
        if lobby_id:
            self.state_text.set_text("アクセス中...")
            self.network_manager.setup_client(int(lobby_id))


    def on_public_click(self):
        public_lobbies = self.network_manager.steam.get_public_lobbies()
        public_lobbies = [f"Public : {lobby_id}" for lobby_id in public_lobbies]  # すべてstrに変換
        self.lobby_list.create_list_items(public_lobbies)

    def on_friend_click(self):
        friend_lobbies = self.network_manager.steam.get_friend_lobbies()

        # 辞書 {SteamID: LobbyID} から "SteamID : LobbyID" の形式に変換
        friend_lobby_list = [f"{self.network_manager.steam.get_steam_name(steam_id)} : {lobby_id}" for steam_id, lobby_id in friend_lobbies.items()]

        # リストに変換したデータをUIへ渡す
        self.lobby_list.create_list_items(friend_lobby_list)
    def on_return_click(self):
        self.scene.get_object("MainMenu").set_active(True)
        self.set_active(False)

# 安全なパーシング
def extract_lobby_ids(friend_lobby):
    lobby_ids = []
    parts = friend_lobby.split(" : ")
    if len(parts) == 2:
        lobby_ids.append(parts[1])
    else:
        print(f"⚠️ 不正なフォーマット: {parts}")
        return None
    return lobby_ids[0]