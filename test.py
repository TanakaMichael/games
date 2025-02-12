import pygame, sys, math

# --- グローバル設定 ---
TILE_SIZE = 32
MAP_WIDTH = 20
MAP_HEIGHT = 15
LIGHT_RADIUS = 6            # 光の影響半径（タイル単位）
LIGHT_INTENSITY = 1.0       # 光の強度（1.0 が最大）
LIGHT_COLOR = (255, 240, 200)  # 光の色（暖色系）

# 各タイルの透過率（0: 完全遮蔽, 1: 完全透過）
# 例: 床は光をそのまま通す（1.0）、壁は 20% しか光を通さない（0.2）
TILE_TRANSMISSION = {
    0: 1.0,  # 床
    1: 0.2   # 壁
}

# --- シンプルなグリッドマップ ---
# 0: 床, 1: 壁
grid = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
# 例として、中央付近の 7 行目に 5～14 列で壁を配置
for x in range(5, 15):
    grid[7][x] = 1

# --- Bresenham の直線アルゴリズム ---
def bresenham_line(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            yield x, y
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
        yield x, y
    else:
        err = dy / 2.0
        while y != y1:
            yield x, y
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
        yield x, y

# --- 視線透過率を計算する関数 ---
def compute_visibility(light_x, light_y, tile_x, tile_y, grid):
    """
    光源（light_x, light_y）から目的タイル（tile_x, tile_y）までの
    直線上で、各タイルの透過率を乗算して最終的な光の伝達率（0～1）を返す。
    始点と終点は除外します。
    """
    transmission = 1.0
    for (x, y) in bresenham_line(light_x, light_y, tile_x, tile_y):
        if (x, y) == (light_x, light_y) or (x, y) == (tile_x, tile_y):
            continue
        # grid[y][x] が 0 や 1 の数値の場合、透過率は TILE_TRANSMISSION 辞書から取得
        tile_type = grid[y][x]
        transmission *= TILE_TRANSMISSION.get(tile_type, 1.0)
        # 途中で transmission が極端に低くなったら早期終了
        if transmission < 0.01:
            return 0.0
    return transmission

# --- プレイヤー（光源）の初期位置と移動速度 ---
player_x = 10.0  # グリッド座標（浮動小数点）
player_y = 10.0
player_speed = 5.0  # タイル/秒

# --- Pygame 初期化 ---
pygame.init()
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))
pygame.display.set_caption("Grid Lighting Demo with Adjustable Light and Wall Transparency (WASD Move)")
clock = pygame.time.Clock()

while True:
    dt = clock.tick(60) / 1000.0  # delta_time（秒）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- プレイヤー移動 (WASD) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_y -= player_speed * dt
    if keys[pygame.K_s]:
        player_y += player_speed * dt
    if keys[pygame.K_a]:
        player_x -= player_speed * dt
    if keys[pygame.K_d]:
        player_x += player_speed * dt

    # マップ外に出ないようクランプ
    player_x = max(0, min(MAP_WIDTH - 1, player_x))
    player_y = max(0, min(MAP_HEIGHT - 1, player_y))

    # --- ライティング計算 ---
    # 各タイルの光の強さ（0～1）を格納する 2 次元リストを作成
    light_intensity = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    # プレイヤーのグリッド座標（整数）
    p_x = int(player_x)
    p_y = int(player_y)
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            # タイル中心座標（グリッド単位）
            tile_center_x = j + 0.5
            tile_center_y = i + 0.5
            dx = tile_center_x - player_x
            dy = tile_center_y - player_y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance <= LIGHT_RADIUS:
                # 基本の光減衰（線形減衰）
                intensity = 1.0 - (distance / LIGHT_RADIUS)
                # 透過率を計算（プレイヤー位置とタイル位置は整数に丸める）
                vis = compute_visibility(p_x, p_y, j, i, grid)
                # 最終的な照度は、光源強度 × 基本減衰 × 透過率
                final_intensity = LIGHT_INTENSITY * intensity * vis
                # クランプ
                light_intensity[i][j] = max(0, min(final_intensity, 1))
            else:
                light_intensity[i][j] = 0

    # --- 描画 ---
    screen.fill((0, 0, 0))
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            # タイルの基本色（床と壁で異なる色）
            if grid[i][j] == 0:
                base_color = (0, 0, 0)  # 床
            else:
                base_color = (50, 50, 50)     # 壁
            # 照度に応じて、ライトの色で補正する
            intensity = light_intensity[i][j]
            # シンプルなブレンド：最終色 = 基本色*(1-intensity) + LIGHT_COLOR*(intensity)
            r = int(base_color[0] * (1 - intensity) + LIGHT_COLOR[0] * intensity)
            g = int(base_color[1] * (1 - intensity) + LIGHT_COLOR[1] * intensity)
            b = int(base_color[2] * (1 - intensity) + LIGHT_COLOR[2] * intensity)
            color = (r, g, b)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)  # タイルの枠線

    # --- プレイヤー描画 ---
    player_pixel_x = int(player_x * TILE_SIZE + TILE_SIZE / 2)
    player_pixel_y = int(player_y * TILE_SIZE + TILE_SIZE / 2)
    pygame.draw.circle(screen, (255, 255, 0), (player_pixel_x, player_pixel_y), TILE_SIZE // 3)

    pygame.display.flip()
