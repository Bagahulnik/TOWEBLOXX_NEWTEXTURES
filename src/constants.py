# Константы игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 120

# Физика
GRAVITY = 0.5
ROPE_LENGTH = 120
INITIAL_FORCE = -0.001
FORCE_MULTIPLIER = 1.02

# Параметры башни
BLOCK_WIDTH = 96
BLOCK_HEIGHT = 48
MAX_ONSCREEN_BLOCKS = 3
SCROLL_THRESHOLD = 5
WOBBLE_SPEED = 0.4
WOBBLE_LIMIT = 20

# Игровая логика
MAX_MISSES = 3  # Максимальное количество промахов
COLLAPSE_THRESHOLD = 0.5  # 50% смещения для обрушения (0.5 = 50%)

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)

# Пути к ресурсам
ASSETS_PATH = "assets/"
TOWERS_PATH = "assets/towers/"
UI_PATH = "assets/ui/"
DATA_PATH = "data/"

# Настройки магазина
TOWER_PRICES = {
    1: 0,
    2: 100,
    3: 200,
    4: 300,
    5: 400,
    6: 500,
    7: 600,
    8: 700
}

TOWER_NAMES = {
    1: "Стандартная",
    2: "Кирпичная",
    3: "Каменная",
    4: "Деревянная",
    5: "Стеклянная",
    6: "Золотая",
    7: "Неоновая",
    8: "Космическая"
}
