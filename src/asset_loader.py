import pygame
from src.constants import ASSETS_PATH, TOWERS_PATH


class AssetLoader:
    def __init__(self):
        pass

    def load_icon(self):
        """Иконка окна игры."""
        icon = pygame.image.load(f"{ASSETS_PATH}icon.png").convert_alpha()
        return icon

    # ---------- ФОНЫ ----------

    def load_backgrounds(self):
        """Загрузка 2 фоновых картинок для меню/магазина."""
        backgrounds = []
        names = [
            "bg_shop_2.png",  # светлый фон первым
            "bg_shop_1.png",  # тёмный фон вторым
        ]
        for name in names:
            img = pygame.image.load(f"{ASSETS_PATH}bg/{name}").convert()
            backgrounds.append(img)
        return backgrounds

    # ---------- ЗВУКИ ----------

    def load_sounds(self):
        sounds = {
            'build': pygame.mixer.Sound(f"{ASSETS_PATH}sfx_build.wav"),
            'gold': pygame.mixer.Sound(f"{ASSETS_PATH}sfx_gold.wav"),
            'fall': pygame.mixer.Sound(f"{ASSETS_PATH}sfx_fall.wav"),
            'over': pygame.mixer.Sound(f"{ASSETS_PATH}sfx_over.wav"),
        }
        return sounds

    # ---------- СПРАЙТЫ БАШЕН ----------

    def load_tower_sprites(self, tower_id):
        """Загружает спрайты одной башни по её id и увеличивает центральный блок до 63x63."""
        base_path = f"{TOWERS_PATH}tower_{tower_id}/"

        def crop_and_scale(img):
            # центр 48x48 внутри исходного 96x48
            src_rect = pygame.Rect(24, 0, 48, 48)
            cropped = img.subsurface(src_rect).copy()
            new_w = 48 + 15  # 63
            new_h = 48 + 15  # 63
            return pygame.transform.smoothscale(cropped, (new_w, new_h))

        bot_raw = pygame.image.load(
            base_path + f"tower_{tower_id}_bot.png"
        ).convert_alpha()
        bot = crop_and_scale(bot_raw)

        # Загружаем ВСЕ 4 варианта mid спрайтов: 0, 1, 2, 3
        mid_frames = []
        for i in range(4):  # 0, 1, 2, 3
            img_raw = pygame.image.load(
                base_path + f"tower_{tower_id}_mid_{i}.png"
            ).convert_alpha()
            img = crop_and_scale(img_raw)
            mid_frames.append(img)

        sprites = {
            'bot': bot,
            'mid': mid_frames,  # список из 4 спрайтов
        }
        return sprites
