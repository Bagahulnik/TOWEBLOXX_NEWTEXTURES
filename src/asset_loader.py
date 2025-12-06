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
        """Загрузка 5 фоновых картинок 540x960, идущих последовательно по вертикали."""
        backgrounds = []
        names = [
            "bg_main.png",
            "bg_sky.png",
            "bg_space.png",
            "bg_total_space.png",
            "bg_total_space_2.png",
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
        """Загружает спрайты одной башни по её id."""
        base_path = f"{TOWERS_PATH}tower_{tower_id}/"

        bot = pygame.image.load(
            base_path + f"tower_{tower_id}_bot.png"
        ).convert_alpha()

        mid_frames = []
        for i in range(4):
            img = pygame.image.load(
                base_path + f"tower_{tower_id}_mid_{i}.png"
            ).convert_alpha()
            mid_frames.append(img)

        sprites = {
            'bot': bot,
            'mid': mid_frames,
        }

        return sprites
