import pygame
from pygame import mixer
from src.game import Game
from src.shop import Shop
from src.ui import MainMenu
from src.save_manager import SaveManager
from src.asset_loader import AssetLoader
from src.constants import *


def main():
    # Инициализация Pygame
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tower Brocks")
    
    # Загрузка ресурсов
    asset_loader = AssetLoader()
    icon = asset_loader.load_icon()
    pygame.display.set_icon(icon)
    
    backgrounds = asset_loader.load_backgrounds()
    
    # Менеджер сохранений
    save_manager = SaveManager()
    
    # FPS
    clock = pygame.time.Clock()
    
    # Состояние приложения
    state = 'menu'  # menu, game, shop
    game = None
    shop = None
    main_menu = MainMenu(screen)
    
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
                    game = Game(screen, save_manager, asset_loader)
                elif action == 'shop':
                    state = 'shop'
                    shop = Shop(screen, save_manager, asset_loader)
                elif action == 'quit':
                    running = False
            
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
            main_menu.draw(backgrounds[0])
        
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
                shop.draw(backgrounds[0])
        
        pygame.display.update()
    
    pygame.quit()


if __name__ == "__main__":
    main()
