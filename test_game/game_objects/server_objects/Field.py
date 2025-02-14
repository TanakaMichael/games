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
from ..LocalBlock import LocalBlock
import pygame
# フィールドを親に、ブロックが設置される
class Field(NetworkGameObject):
    def __init__(self, name="Field", active=True, parent=None, network_id=None, steam_id=None, number=None, position=None):
        super().__init__(name, active, parent, network_id, steam_id)
        self.network_manager = NetworkManager.get_instance()
        self.input_manager = InputManager.get_instance()

        # 操作のためのactionを取得する
        self.move_right_action = self.input_manager.get_action("MoveRight")
        self.move_left_action = self.input_manager.get_action("MoveLeft")
        self.move_rotate_action = self.input_manager.get_action("Rotate")
        self.move_down_action = self.input_manager.get_action("MoveDown")
        self.canvas = self.network_manager.scene_manager.current_scene.canvas
        members = self.network_manager.steam.get_all_lobby_members(self.network_manager.lobby_id)

        self.is_local_player = False
        if self.network_manager.is_server:
            if len(members) >= 2:
                self.steam_id = members[number]
            else:
                # おそらくデバッグまたはオフライン起動(ユーザーは0番目のフィールドを使用する)
                if number == 0:
                    self.steam_id = self.network_manager.local_steam_id
        self.field_number = number
        self.width = 10
        self.height = 20

        self.mino_size = 40
        if position is None:
            if number == 0:
                self.transform.set_local_position(pygame.Vector2(-500 - (self.width * self.mino_size) + self.mino_size, -300))
            elif number == 1:
                self.transform.set_local_position(pygame.Vector2(500, -300))


    def start(self):
        # initialize処理
        super().start()
        if self.network_manager.is_server:
            self.game_started = False
            self.is_alive = True # ゲームの終了条件の一つとして使用するbool
            self.running = False
            self.active_mino = None
            self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

            # 生成回数
            self.generate_time = 1
            self.minos = [TMino]
            self.fall_speed = 0.5
        # 背景ブロック
        self.back_mino_image = "BackMino1.png"
        for y in range(self.height):
            for x in range(self.width):
                back = self.add_child(LocalBlock(parent=self, image_path=self.back_mino_image, is_wall=False, position=(y, x)))
                back.set_transform_position(self.mino_size, pygame.Vector2(x, y))

    def generate_block(self):
        """server側でブロックの生成patternを作成する"""
        index = self.generate_time * self.scene.seed % len(self.minos)
        self.active_mino = self.add_network_child(self.minos[index](parent=self, size=self.mino_size))
        self.generate_time += 1


    def update(self, dt):
        super().update(dt)
        if self.initialized and self.steam_id == self.network_manager.local_steam_id:
            if self.move_left_action.get_on_press():
                self.network_manager.send_to_server({"type": "move_left_mino", "sender_id": self.network_manager.local_steam_id}, True)
            if self.move_right_action.get_on_press():
                self.network_manager.send_to_server({"type": "move_right_mino", "sender_id": self.network_manager.local_steam_id}, True)
            if self.move_down_action.get_on_press():
                self.network_manager.send_to_server({"type": "move_down_mino", "sender_id": self.network_manager.local_steam_id}, True)
            if self.move_rotate_action.get_on_press():
                self.network_manager.send_to_server({"type": "rotation", "sender_id": self.network_manager.local_steam_id, }, True)

    def on_fall_active_mino(self):
        """fall関数を定期的に呼び出すコルーチン"""
        while self.running:
            yield WaitForSeconds(self.fall_speed)
            self.fall()
    def fall(self):
        """ミノを落とすか設置するか決める"""
        if self.check_put():
            self.fix_active_mino()
        else:
            self.fall_active_mino()
    def fix_active_mino(self):
        """アクティブなミノをフィールドに固定し、コピーしたブロックを配置"""
        if self.active_mino:
            new_blocks = []  # 新しくコピーするブロックリスト
            for block in self.active_mino.blocks:
                x = int(block.position.x + self.active_mino.position.x)
                y = int(block.position.y + self.active_mino.position.y)

                # **ブロックを新しく作成し、ネットワークオブジェクトとして登録**
                new_block = self.add_network_child(Block(name="FixedBlock", 
                                                                parent=self,  
                                                                position=(x, y),
                                                                image_path=self.active_mino.image_path,
                                                                is_wall=True
                                                                ))
                new_blocks.append(new_block)
                new_block.set_transform_position(self.mino_size, pygame.Vector2(x, y))
                self.grid[y][x] = new_block
                # **ゲームオーバー判定**
                if self.check_game_over(x, y):
                    self.trigger_game_over()
                    return
            # **active_mino を削除**
            self.remove_network_child(self.active_mino)
            self.clear_complete_lines()
            self.generate_block()

            # **固定されたブロックは親子関係を持たず独立して存在**
            print(f"🧱 固定されたブロック: {len(new_blocks)} 個が配置されました。")
    def check_game_over(self, x, y):
        """ゲームオーバー判定"""
        game_over_height = 2  # **ゲームオーバーとする高さ（要調整）**
        return (x == self.width // 2 and y < game_over_height) or self.grid[0][x] is not None
    def trigger_game_over(self):
        """ゲームオーバー処理を実行"""
        print("💀 ゲームオーバー！")
        self.network_manager.broadcast({"type": "game_over", "loser": self.steam_id, "field_number": self.field_number}, True)
        self.coroutine_manager.clear()
        self.is_alive = False
        self.running = False


    def clear_complete_lines(self):
        """ラインが完成しているかをチェックし、削除 & シフト処理"""
        full_lines = [y for y in range(self.height) if all(self.grid[y][x] is not None for x in range(self.width))]

        if not full_lines:
            return  # 消えるラインなし

        shift_map = get_shift_map(full_lines)  # {start_y: length} の辞書を取得
        print(f"🔥 消去対象のライン: {shift_map}")

        # **ライン消去**
        for y in full_lines:
            for x in range(self.width):
                block = self.grid[y][x]
                if block:
                    self.remove_network_child(block)  # ネットワークオブジェクト削除
                self.grid[y][x] = None  # グリッドの参照も削除

        # **上にあるブロックをシフト**
        for start_y, length in shift_map.items():
            for y in reversed(range(start_y)):  # start_y の上のブロックを移動
                for x in range(self.width):
                    block = self.grid[y][x]
                    if block:
                        new_y = y + length  # 落下後のY位置
                        if new_y < self.height:
                            self.grid[new_y][x] = block
                            self.grid[y][x] = None  # 元の位置をクリア

                            # **ブロックの座標を更新**
                            block.position.y = new_y
                            block.set_transform_position(self.mino_size, pygame.Vector2(x, new_y))

                            print(f"⬇ ブロック {block.name} を {y} → {new_y} に移動")


    def fall_active_mino(self):
        self.active_mino.move_down()
    def check_put(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = int(self.active_mino.position.x + block.position.x)
                y = int(self.active_mino.position.y + block.position.y)
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
                self.running = True
                self.generate_block()
                self.coroutine_manager.start_coroutine(self.on_fall_active_mino)
        if self.network_manager.is_client or not self.running:
            return
        # 個々より先はgameが開始していることが条件の操作
        elif message.get("type") == "move_left_mino" and message["sender_id"] == self.steam_id:
            self.move_left()
        elif message.get("type") == "move_right_mino" and message["sender_id"] == self.steam_id:
            self.move_right()
        elif message.get("type") == "rotation" and message["sender_id"] == self.steam_id:
            self.rotation()
        elif message.get("type") == "move_down_mino" and message["sender_id"] == self.steam_id:
            self.fall()
        elif message.get("type") == "game_over" and message["field_number"] == self.field_number:
            # self.on_game_over(message)
            self.coroutine_manager.clear()
            self.running = False
            print(f"敗北者 : {message['loser']}" )
    def move_right(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = int(self.active_mino.position.x + block.position.x)
                y = int(self.active_mino.position.y + block.position.y)
                if x+1 >= self.width or self.grid[y][x+1] is not None:
                    return False
            self.active_mino.move_right()
    def move_left(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = int(self.active_mino.position.x + block.position.x)
                y = int(self.active_mino.position.y + block.position.y)
                if x-1 <=-1 or self.grid[y][x-1] is not None:
                    return False
            self.active_mino.move_left()
    def rotation(self):
        if self.active_mino:
            for block in self.active_mino.blocks:
                x = int(-block.position.y + self.active_mino.position.x)
                y = int(block.position.x + self.active_mino.position.y)
                if (x < 0 or x >= self.width) or (y < 0 or y >= self.height) :
                    return False
                if self.grid[y][x] is not None:
                    return False
            self.active_mino.rotation()



        
def get_shift_map(full_lines):
    """消えたラインを {開始Y: 長さ} の辞書に変換"""
    if not full_lines:
        return {}

    full_lines.sort(reverse=True)  # 上から消えていくので降順ソート
    shift_map = {}  # `{start_y: length}` の辞書
    start_y = full_lines[0]
    length = 1

    for i in range(1, len(full_lines)):
        if full_lines[i] == full_lines[i - 1] - 1:  # 連続している
            length += 1
        else:
            shift_map[start_y] = length  # 連続ブロック登録
            start_y = full_lines[i]  # 新しいスタート地点
            length = 1  # 長さリセット

    shift_map[start_y] = length  # 最後のグループを登録

    return shift_map

NetworkObjectFactory.register_class(Field)