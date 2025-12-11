import os
import pygame
from pygame import mixer

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
        """Загружает все звуки игры."""
        sounds = {}
        sound_files = {
            'build': 'sfx_build.wav',
            'fall': 'sfx_fall.wav',
            'over': 'sfx_over.wav',
            'gold': 'sfx_gold.wav',
            'click': 'sfx_click.mp3',
            'error': 'sfx_error.mp3',
            'coin': 'sfx_coin.mp3',
        }
        
        # 🎙️ ГОЛОСОВЫЕ ФРАЗЫ
        phrase_files = {
            'start': 'start.mp3',
            'go': 'go.mp3',
            'good_job': 'good_job.mp3',
            'amazing': 'amazing.mp3',
            'fantastic': 'fantastic.mp3',
            'nice_try': 'nice_try.mp3',
            'top_score': 'top_score.mp3',
            'perfect': 'perfect.mp3'
        }

        # Загрузка обычных звуков из SFX_PATH
        for name, file in sound_files.items():
            try:
                sounds[name] = mixer.Sound(f"{SFX_PATH}{file}")
            except pygame.error as e:
                print(f"❌ Не удалось загрузить звук {file}: {e}")
        
        # 🎙️ ЗАГРУЗКА ФРАЗ из assets/phrases/
        for name, file in phrase_files.items():
            try:
                sounds[name] = mixer.Sound(f"{ASSETS_PATH}phrases/{file}")
            except pygame.error as e:
                print(f"❌ Не удалось загрузить фразу {file}: {e}")

        return sounds

    # ---------- СПРАЙТЫ БАШЕН ----------
    def load_tower_sprites(self, tower_id):
        """
        Загружает спрайты одной башни по её id.
        Исходный спрайт 96x48, полезная текстура ~72x48 (по 12px слева/справа пустота),
        вырезаем 72x48 и растягиваем в блок 72x72.
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
