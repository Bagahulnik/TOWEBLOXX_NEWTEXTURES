# -------- Экран --------
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
FPS = 60

# -------- Размеры блока --------
BLOCK_WIDTH = 96
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
HOOK_ATTACH_OFFSET_X = 60
HOOK_ATTACH_OFFSET_Y = 30

# -------- Физика --------
GRAVITY = 0.4
INITIAL_FORCE = -0.0015
FORCE_ACCELERATION = 1.015  # +1.5% за блок (можно 1.01-1.03)
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
MUSIC_PATH  = ASSETS_PATH + "music/"
DATA_PATH   = "data/"

UI_PATH     = ASSETS_PATH + "ui/"
SFX_PATH    = ASSETS_PATH + "sfx/"
CRANE_PATH  = ASSETS_PATH + "crane/"



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
BG_SCROLL_STEP = BLOCK_HEIGHT * 2      # шаг = 2 блока  
TOWER_BLOCKS_PER_STEP = 6              # смена на 6 блоках (в 2 раза раньше)
BASE_ONSCREEN_BLOCKS = 4               # оставляем 4 блока
BG_SCROLL_DURATION = 20                # анимация 20 кадров (~0.33 сек при 60 FPS)

