import pygame
from src.ui import Button, TowerCard
from src.constants import *


class Shop:
    def __init__(self, screen, save_manager, asset_loader):
        self.screen = screen
        self.save_manager = save_manager
        self.asset_loader = asset_loader
        
        self.font_title = pygame.font.Font("freesansbold.ttf", 48)
        self.font_coins = pygame.font.Font("freesansbold.ttf", 24)
        
        self.back_button = Button(50, 500, 150, 50, "Назад", 
                                 pygame.font.Font("freesansbold.ttf", 24))
        
        self.tower_cards = []
        self.create_tower_cards()
    
    def create_tower_cards(self):
        """Создание карточек башен"""
        self.tower_cards = []
        
        for i in range(1, 9):
            x = 50 + ((i - 1) % 4) * 180
            y = 100 + ((i - 1) // 4) * 220
            
            is_unlocked = self.save_manager.is_tower_unlocked(i)
            is_selected = self.save_manager.get_selected_tower() == i
            
            # Загрузка превью спрайта
            sprites = self.asset_loader.load_tower_sprites(i)
            preview = sprites['mid'][0]
            
            card = TowerCard(
                x, y, i,
                TOWER_NAMES[i],
                TOWER_PRICES[i],
                is_unlocked,
                is_selected,
                preview
            )
            self.tower_cards.append(card)
    
    def draw(self, background):
        """Отрисовка магазина"""
        self.screen.blit(background, (0, 0))
        
        # Заголовок
        title = self.font_title.render("Магазин башен", True, BLACK)
        title_rect = title.get_rect(center=(400, 40))
        self.screen.blit(title, title_rect)
        
        # Монеты
        coins_text = self.font_coins.render(
            f"Монеты: {self.save_manager.get_coins()}", 
            True, BLACK
        )
        self.screen.blit(coins_text, (600, 500))
        
        # Карточки башен
        for card in self.tower_cards:
            card.draw(self.screen)
        
        # Кнопка назад
        self.back_button.draw(self.screen)
    
    def handle_event(self, event):
        """Обработка событий"""
        # Кнопка назад
        if self.back_button.handle_event(event):
            return 'back'
        
        # Карточки башен
        for card in self.tower_cards:
            if card.handle_event(event):
                return self.handle_card_click(card)
        
        return None
    
    def handle_card_click(self, card):
        """Обработка клика по карточке"""
        tower_id = card.tower_id
        
        if not card.is_unlocked:
            # Попытка купить
            if self.save_manager.spend_coins(card.price):
                self.save_manager.unlock_tower(tower_id)
                self.save_manager.set_selected_tower(tower_id)
                self.create_tower_cards()  # Обновить карточки
                return 'purchased'
            else:
                return 'not_enough_coins'
        else:
            # Выбрать башню
            self.save_manager.set_selected_tower(tower_id)
            self.create_tower_cards()  # Обновить карточки
            return 'selected'
        
        return None
    
    def update_cards(self):
        """Обновление карточек"""
        for card in self.tower_cards:
            card.is_unlocked = self.save_manager.is_tower_unlocked(card.tower_id)
            card.is_selected = self.save_manager.get_selected_tower() == card.tower_id
