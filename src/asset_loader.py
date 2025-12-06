import pygame
import os
from src.constants import ASSETS_PATH, TOWERS_PATH


class AssetLoader:
    def __init__(self):
        self.tower_sprites = {}
        self.backgrounds = []
        self.sounds = {}
        
    def load_tower_sprites(self, tower_id):
        """Загружает спрайты для конкретной башни"""
        if tower_id in self.tower_sprites:
            return self.tower_sprites[tower_id]
        
        tower_path = f"{TOWERS_PATH}tower_{tower_id}/"
        
        try:
            sprites = {
                'bot': pygame.image.load(f"{tower_path}tower_{tower_id}_bot.png").convert_alpha(),
                'mid': [
                    pygame.image.load(f"{tower_path}tower_{tower_id}_mid_0.png").convert_alpha(),
                    pygame.image.load(f"{tower_path}tower_{tower_id}_mid_1.png").convert_alpha(),
                    pygame.image.load(f"{tower_path}tower_{tower_id}_mid_2.png").convert_alpha(),
                    pygame.image.load(f"{tower_path}tower_{tower_id}_mid_3.png").convert_alpha()
                ],
                'gold': None  # Опционально: золотой вариант
            }
            
            # Попытка загрузить золотой спрайт
            try:
                sprites['gold'] = pygame.image.load(f"{tower_path}tower_{tower_id}_gold.png").convert_alpha()
            except:
                # Если нет золотого спрайта, используем обычный с желтым оттенком
                sprites['gold'] = sprites['mid'][0].copy()
                sprites['gold'].fill((255, 215, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
            
            self.tower_sprites[tower_id] = sprites
            return sprites
            
        except FileNotFoundError as e:
            print(f"Ошибка загрузки спрайтов башни {tower_id}: {e}")
            # Возвращаем стандартные спрайты
            return self.load_tower_sprites(1)
    
    def load_backgrounds(self):
        """Загружает фоны"""
        self.backgrounds = [
            pygame.image.load(f"{ASSETS_PATH}background0.jpg").convert(),
            pygame.image.load(f"{ASSETS_PATH}background1.jpg").convert(),
            pygame.image.load(f"{ASSETS_PATH}background2.jpg").convert(),
            pygame.image.load(f"{ASSETS_PATH}background3.jpg").convert()
        ]
        return self.backgrounds
    
    def load_sounds(self):
        """Загружает звуки"""
        self.sounds = {
            'bgm': pygame.mixer.Sound(f"{ASSETS_PATH}bgm.wav"),
            'build': pygame.mixer.Sound(f"{ASSETS_PATH}build.wav"),
            'gold': pygame.mixer.Sound(f"{ASSETS_PATH}gold.wav"),
            'over': pygame.mixer.Sound(f"{ASSETS_PATH}overmusic.wav"),
            'fall': pygame.mixer.Sound(f"{ASSETS_PATH}fall.wav")
        }
        return self.sounds
    
    def load_icon(self):
        """Загружает иконку"""
        return pygame.image.load(f"{ASSETS_PATH}icon.png")
