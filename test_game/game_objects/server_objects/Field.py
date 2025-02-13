from gamelib.network.syncs.game_objects.NetworkGameObject import NetworkGameObject
from gamelib.game.ui.ui_objects.MeshText import MeshText
from gamelib.game.ui.ui_objects.MeshButtonText import MeshButtonText
from gamelib.network.syncs.components.NetworkScript import NetworkScript
from gamelib.game.InputManager import InputManager
from gamelib.network.NetworkManager import NetworkManager
from gamelib.network.NetworkObjectFactory import NetworkObjectFactory
from gamelib.game.utility.Coroutine import WaitForSeconds
from .TMino import TMino
from ..Block import Block
import pygame
# フィールドを親に、ブロックが設置される
class Field(NetworkGameObject):
    def __init__(self, name="Field", active=True, parent=None, network_id=None, steam_id=None, number=None):
        super().__init__(name, active, parent, network_id, steam_id)
        self.network_manager = NetworkManager.get_instance()
        self.input_manager = InputManager.get_instance()

        # 操作のためのactionを取得する
        self.move_right_action = self.input_manager.get_action("MoveRight")
        self.move_left_action = self.input_manager.get_action("MoveLeft")
        self.canvas = self.network_manager.scene_manager.current_scene.canvas
        members = self.network_manager.steam.get_all_lobby_members(self.network_manager.lobby_id)
        self.is_local_player = False
        if self.network_manager.is_server:
            if len(members) >= 2:
                self.steam_id = members[number]
        self.game_started = False
        # 生成回数
        self.generate_time = 1
        self.minos = [TMino]
        self.width = 10
        self.height = 20
        self.fall_speed = 0.5
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

        self.active_mino = None

            

    def start(self):
        # initialize処理
        super().start()

    def generate_block(self):
        """server側でブロックの生成patternを作成する"""
        index = self.generate_time * self.scene.seed % len(self.minos)
        self.active_mino = self.scene.add_network_object(self.minos[index](parent=self))
        self.active_mino.set_transform_position()
        self.generate_time += 1


    def update(self, dt):
        super().update(dt)
        if self.initialized and self.steam_id == self.network_manager.local_steam_id:
            if self.move_left_action.get_on_press():
                self.network_manager.send_to_server({"type": "move","x": -1, "sender_id": self.network_manager.local_steam_id})
            if self.move_right_action.get_on_press():
                self.network_manager.send_to_server({"type": "move","x": 1, "sender_id": self.network_manager.local_steam_id})
            if self.move_rotate_action.get_on_press():
                self.network_manager.send_to_server({"type": "rotation", "sender_id": self.network_manager.local_steam_id})

    def on_fall_active_mino(self):
        WaitForSeconds(self.fall_speed)
        if self.check_put():
            self.fix_active_mino()
        else:
            self.fall_active_mino()
    def fix_active_mino(self):
        """アクティブなミノをフィールドに固定し、コピーしたブロックを配置"""
        if self.active_mino:
            new_blocks = []  # 新しくコピーするブロックリスト
            for block in self.active_mino.blocks:
                x = block.position.x + self.active_mino.position.x
                y = block.position.y + self.active_mino.position.y

                # **ブロックを新しく作成し、ネットワークオブジェクトとして登録**
                new_block = self.scene.add_network_object(Block(name="FixedBlock", 
                                                                parent=self,  
                                                                position=(x, y),
                                                                image_path=self.active_mino.image_path
                                                                ))
                new_blocks.append(new_block)
                new_block.set_transform_position(pygame.Vector2(x, y))
                self.grid[y][x] = new_block
                # **ゲームオーバー判定**
                if self.check_game_over(x, y):
                    self.trigger_game_over()
                    return

            # **active_mino を削除**
            self.scene.remove_network_object(self.active_mino)

            # **固定されたブロックは親子関係を持たず独立して存在**
            print(f"🧱 固定されたブロック: {len(new_blocks)} 個が配置されました。")
    def check_game_over(self, x, y):
        """ゲームオーバー判定"""
        game_over_height = 2  # **ゲームオーバーとする高さ（要調整）**
        return (x == self.width // 2 and y < game_over_height) or self.grid[0][x] is not None
    def trigger_game_over(self):
        """ゲームオーバー処理を実行"""
        print("💀 ゲームオーバー！")
        self.network_manager.broadcast({"type": "game_over", "loser": self.steam_id}, True)
        self.coroutine_manager.clear()


    def clear_complete_lines(self):
        """ラインが完成しているかをチェックし、削除 & シフト処理"""
        full_lines = []

        # **完成したラインを探す**
        for y in range(self.height):
            if all(self.grid[y][x] is not None for x in range(self.width)):  
                full_lines.append(y)

        if not full_lines:
            return  # 消えるラインなし

        print(f"🔥 消去対象のライン: {full_lines}")

        # **ライン消去**
        for y in full_lines:
            for x in range(self.width):
                block = self.grid[y][x]
                if block:
                    self.scene.remove_network_object(block)  # ネットワークオブジェクト削除
                self.grid[y][x] = None  # グリッドの参照も削除

        # **上にあるブロックをシフト**
        for y in reversed(range(self.height)):  # 上から下へ確認
            if y in full_lines:  # 消えたラインなら無視
                continue

            for x in range(self.width):
                block = self.grid[y][x]
                if block:
                    new_y = y + len([line for line in full_lines if line > y])  # いくつ下に落ちるか
                    if new_y < self.height:
                        self.grid[new_y][x] = block
                        self.grid[y][x] = None  # 元の位置をクリア

                        # **ブロックの座標を更新**
                        block.position.y = new_y
                        block.set_transform_position(pygame.Vector2(x, new_y))

                        print(f"⬇ ブロック {block.name} を {y} → {new_y} に移動")


    def fall_active_mino(self):
        self.active_mino.move_down()
    def check_put(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = self.active_mino.position.x + block.x
                y = self.active_mino.position.y + block.y
                # 設置可能
                if y+1 >= self.height or self.grid[y+1][x] is not None:
                    return True
        # 設置不可
        return False
    def receive_message(self, message):
        super().receive_message(message)
        if message.get("type") == "start_game":
            self.game_started = True
            if self.network_manager.is_server:
                # テトリスのメインの処理はserverのみが行う
                self.generate_block()
                self.coroutine_manager.start_coroutine(self.on_fall_active_mino)
        elif message.get("type") == "move" and message["x"] == -1 and message["sender_id"] == self.steam_id:
            self.move_left()
        elif message.get("type") == "move" and message["x"] == 1 and message["sender_id"] == self.steam_id:
            self.move_right()
        elif message.get("type") == "rotation" and message["sender_id"] == self.steam_id:
            self.rotation()
        elif message.get("type") == "game_over":
            # self.on_game_over(message)
            self.coroutine_manager.clear()
            print(f"敗北者 : {message['sender_id']}" )
    def move_right(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = self.active_mino.position.x + block.x
                y = self.active_mino.position.y + block.y
                if x+1 >= self.wdith or self.grid[y][x+1] is not None:
                    return False
            self.active_mino.move_right()
    def move_left(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = self.active_mino.position.x + block.x
                y = self.active_mino.position.y + block.y
                if x-1 <= 0 or self.grid[y][x-1] is not None:
                    return False
            self.active_mino.move_left()
    def rotation(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = -block.y
                y = block.x
                if (x < 0 or x >= self.width) or (y < 0 or y >= self.height) :
                    if self.grid[y][x] is not None:
                        return False
            self.active_mino.rotation()



        

NetworkObjectFactory.register_class(Field)