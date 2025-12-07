# -------- Экран --------
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
FPS = 60

# -------- Размеры блока --------
BLOCK_WIDTH = 63
BLOCK_HEIGHT = 63

# -------- Кран, верёвка, крюк --------
ROPE_LENGTH = 305

ROPE_ORIGIN_X = 252
ROPE_ORIGIN_Y = 118
CRANE_ANCHOR_X = ROPE_ORIGIN_X
CRANE_ANCHOR_Y = ROPE_ORIGIN_Y

# нижняя точка верёвки
ROPE_BOTTOM_Y = ROPE_ORIGIN_Y + ROPE_LENGTH

SAFE_GAP_TO_HOOK = 80  # минимальный зазор от верха башни до низа верёвки
MAX_TOWER_TOP_Y = -9999

HOOK_BOTTOM_OFFSET = 10
HOOK_ATTACH_OFFSET_X = 50
HOOK_ATTACH_OFFSET_Y = 30

# -------- Физика --------
GRAVITY = 0.4
INITIAL_FORCE = -0.001
COLLAPSE_THRESHOLD = 0.5

# -------- Шатание башни --------
WOBBLE_SPEED = 0.5
WOBBLE_LIMIT = 10

# -------- Ограничения --------
MAX_MISSES = 3
MAX_ONSCREEN_BLOCKS = 8

# -------- Цвета --------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# -------- Пути --------
ASSETS_PATH = "assets/"
TOWERS_PATH = ASSETS_PATH + "towers/"
DATA_PATH = "data/"

# -------- Магазин --------
TOWER_PRICES = {
    1: 0,
    2: 100,
    3: 200,
    4: 300,
    5: 400,
    6: 500,
    7: 600,
    8: 700,
}

TOWER_NAMES = {
    1: "Кирпичная",
    2: "Зеленая",
    3: "Неоновая",
    4: "Деревянная",
    5: "Японская",
    6: "Золотая",
    7: "Каменная",
    8: "Греческая",
}

# -------- Скролл большого фона --------
# высота шага опускания фона (2 блока)
BG_SCROLL_STEP = BLOCK_HEIGHT * 2
# уровень, которого должна достичь вершина башни, чтобы дернуть фон
TOWER_BLOCKS_PER_STEP = 8          # при таком размере башни двигаем фон
BASE_ONSCREEN_BLOCKS = 4           # сколько блоков «оставляем» после шага
