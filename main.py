import pygame
from pygame import mixer
from src.game import Game
from src.shop import Shop
from src.ui import MainMenu, SettingsMenu
from src.save_manager import SaveManager
from src.asset_loader import AssetLoader
from src.constants import *


def main():
    # Инициализация Pygame
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tower Bloxx")
    
    # Загрузка ресурсов
    asset_loader = AssetLoader()
    icon = asset_loader.load_icon()
    pygame.display.set_icon(icon)
    
    backgrounds = asset_loader.load_backgrounds()  # 2 фона bg_shop_1/bg_shop_2
    
    # Музыка глобально
    pygame.mixer.music.load(f"{ASSETS_PATH}bgm.wav")
    pygame.mixer.music.play(-1)
    
    # Менеджер сохранений
    save_manager = SaveManager()
    
    # FPS
    clock = pygame.time.Clock()
    
    # ДВА НЕЗАВИСИМЫХ МУТА
    music_muted = False
    sfx_muted = False
    
    # Состояние приложения
    state = 'menu'   # menu, game, shop, settings
    game = None
    shop = None
    main_menu = MainMenu(screen)
    settings_menu = SettingsMenu(screen)
    
    # текущий индекс фона для меню/магазина/настроек
    current_bg_index = 0
    
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Обработка событий в зависимости от состояния
            if state == 'menu':
                action = main_menu.handle_event(event)
                if action == 'play':
                    state = 'game'
                    game = Game(screen, save_manager, asset_loader, sound_muted=sfx_muted)
                elif action == 'shop':
                    state = 'shop'
                    shop = Shop(screen, save_manager, asset_loader)
                elif action == 'settings':
                    state = 'settings'
                    # передаём текущее состояние в меню настроек
                    settings_menu.music_muted = music_muted
                    settings_menu.sfx_muted = sfx_muted
                    settings_menu.bg_index = current_bg_index
                elif action == 'quit':
                    running = False
            
            elif state == 'settings':
                action = settings_menu.handle_event(event)
                if action == 'back':
                    state = 'menu'
                elif action == 'mute_music':
                    music_muted = not music_muted
                    settings_menu.music_muted = music_muted
                    pygame.mixer.music.set_volume(0.0 if music_muted else 1.0)
                elif action == 'mute_sfx':
                    sfx_muted = not sfx_muted
                    settings_menu.sfx_muted = sfx_muted
                    if game:
                        game.sound_muted = sfx_muted
                        for sound in game.sounds.values():
                            sound.set_volume(0.0 if sfx_muted else 1.0)
                elif action == 'toggle_bg':
                    current_bg_index = settings_menu.bg_index
            
            elif state == 'game':
                if game:
                    game.handle_game_events(event)
            
            elif state == 'shop':
                if shop:
                    action = shop.handle_event(event)
                    if action == 'back':
                        state = 'menu'
        
        # Отрисовка в зависимости от состояния
        screen.fill(WHITE)
        
        if state == 'menu':
            main_menu.draw(backgrounds[current_bg_index])
        
        elif state == 'settings':
            settings_menu.draw(backgrounds[current_bg_index])
        
        elif state == 'game':
            if game:
                game.update()
                game.draw()
                
                if game.game_over:
                    result = game.show_game_over_screen()
                    if result == 'quit':
                        running = False
                    elif result == 'menu':
                        state = 'menu'
                        game = None
        
        elif state == 'shop':
            if shop:
                shop.draw(backgrounds[current_bg_index])
        
        pygame.display.update()
    
    pygame.quit()


if __name__ == "__main__":
    main()
