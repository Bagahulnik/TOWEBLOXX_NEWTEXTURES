import pygame
from src.constants import (
    ASSETS_PATH,
    TOWERS_PATH,
    BLOCK_WIDTH,
    BLOCK_HEIGHT,
    UI_PATH,
    SFX_PATH,
)


class AssetLoader:
    def __init__(self):
        pass

    def load_icon(self):
        """Иконка окна игры."""
        icon = pygame.image.load(f"{UI_PATH}icon.png").convert_alpha()
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
            "build": pygame.mixer.Sound(f"{SFX_PATH}sfx_build.wav"),
            "gold": pygame.mixer.Sound(f"{SFX_PATH}sfx_gold.wav"),
            "fall": pygame.mixer.Sound(f"{SFX_PATH}sfx_fall.wav"),
            "over": pygame.mixer.Sound(f"{SFX_PATH}sfx_over.wav"),
        }
        return sounds

    # ---------- СПРАЙТЫ БАШЕН ----------

    def load_tower_sprites(self, tower_id):
        """
        Загружает спрайты одной башни по её id.
        Исходный спрайт 96x48, полезная текстура ~72x48 (по 12px слева/справа пустота),
        вырезаем 72x48 и растягиваем в блок 63x63.
        """
        base_path = f"{TOWERS_PATH}tower_{tower_id}/"

        def crop_and_scale(img: pygame.Surface) -> pygame.Surface:
            # полезная часть 72x48 в центре 96x48: от x = 12 до x = 84
            src_rect = pygame.Rect(12, 0, 72, 48)
            cropped = img.subsurface(src_rect).copy()

            # растягиваем в размер блока 72x72
            scaled = pygame.transform.smoothscale(
                cropped, (BLOCK_WIDTH, BLOCK_HEIGHT)
            )
            return scaled

        # bot
        bot_raw = pygame.image.load(
            base_path + f"tower_{tower_id}_bot.png"
        ).convert_alpha()
        bot = crop_and_scale(bot_raw)

        # mid 0..3
        mid_frames = []
        for i in range(4):  # 0, 1, 2, 3
            img_raw = pygame.image.load(
                base_path + f"tower_{tower_id}_mid_{i}.png"
            ).convert_alpha()
            img = crop_and_scale(img_raw)
            mid_frames.append(img)

        sprites = {
            "bot": bot,
            "mid": mid_frames,
        }
        return sprites
