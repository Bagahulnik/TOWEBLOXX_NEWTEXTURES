# Разрешение экрана (портрет)
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
FPS = 60

# Размеры блока
BLOCK_WIDTH = 130
BLOCK_HEIGHT = 90

# Точка крепления крюка (из спрайта крана)
ROPE_LENGTH = 305
ROPE_EXTRA_TO_BLOCK = 20
ROPE_ORIGIN_X = 252
ROPE_ORIGIN_Y = 118
CRANE_ANCHOR_X = ROPE_ORIGIN_X
CRANE_ANCHOR_Y = ROPE_ORIGIN_Y
HOOK_BOTTOM_OFFSET = 10# расстояние от якоря до низа крюка
HOOK_ATTACH_OFFSET_X = 50   # центр блока по ширине 
HOOK_ATTACH_OFFSET_Y = 30    # верхняя грань блока


# Физика
GRAVITY = 0.4
INITIAL_FORCE = -0.001
COLLAPSE_THRESHOLD = 0.5

# Шатание башни
WOBBLE_SPEED = 0.5
WOBBLE_LIMIT = 10

# Максимальное количество промахов
MAX_MISSES = 3

# Максимальное количество блоков на экране
MAX_ONSCREEN_BLOCKS = 8

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Пути к ресурсам
ASSETS_PATH = "assets/"
TOWERS_PATH = ASSETS_PATH + "towers/"
DATA_PATH = "data/"

# Цены на башни
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

# Названия башен
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
