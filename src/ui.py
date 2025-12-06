import pygame
from src.constants import *


class Button:
    def __init__(self, x, y, width, height, text, font, color=(100, 100, 100), 
                 text_color=BLACK, hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, screen):
        """Отрисовка кнопки"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        """Обработка событий"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class TowerCard:
    def __init__(self, x, y, tower_id, tower_name, price, is_unlocked, is_selected, preview_sprite):
        self.rect = pygame.Rect(x, y, 150, 200)
        self.tower_id = tower_id
        self.tower_name = tower_name
        self.price = price
        self.is_unlocked = is_unlocked
        self.is_selected = is_selected
        self.preview_sprite = preview_sprite
        self.is_hovered = False
        
        self.font = pygame.font.Font("freesansbold.ttf", 16)
        self.small_font = pygame.font.Font("freesansbold.ttf", 12)
    
    def draw(self, screen):
        """Отрисовка карточки башни"""
        # Фон карточки
        if self.is_selected:
            color = (100, 255, 100)
        elif self.is_hovered:
            color = (200, 200, 200)
        else:
            color = (150, 150, 150)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3)
        
        # Превью спрайта
        if self.preview_sprite:
            sprite_rect = self.preview_sprite.get_rect(center=(self.rect.centerx, self.rect.y + 70))
            screen.blit(self.preview_sprite, sprite_rect)
        
        # Название
        name_surf = self.font.render(self.tower_name, True, BLACK)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.y + 140))
        screen.blit(name_surf, name_rect)
        
        # Цена или статус
        if not self.is_unlocked:
            price_surf = self.small_font.render(f"{self.price} монет", True, BLACK)
            price_rect = price_surf.get_rect(center=(self.rect.centerx, self.rect.y + 170))
            screen.blit(price_surf, price_rect)
        elif self.is_selected:
            status_surf = self.small_font.render("Выбрано", True, BLACK)
            status_rect = status_surf.get_rect(center=(self.rect.centerx, self.rect.y + 170))
            screen.blit(status_surf, status_rect)
        else:
            status_surf = self.small_font.render("Открыто", True, BLACK)
            status_rect = status_surf.get_rect(center=(self.rect.centerx, self.rect.y + 170))
            screen.blit(status_surf, status_rect)
    
    def handle_event(self, event):
        """Обработка событий"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font("freesansbold.ttf", 64)
        self.font_button = pygame.font.Font("freesansbold.ttf", 32)
        
        self.buttons = {
            'play': Button(300, 250, 200, 60, "Играть", self.font_button),
            'shop': Button(300, 330, 200, 60, "Магазин", self.font_button),
            'quit': Button(300, 410, 200, 60, "Выход", self.font_button)
        }
    
    def draw(self, background):
        """Отрисовка главного меню"""
        self.screen.blit(background, (0, 0))
        
        # Заголовок
        title = self.font_title.render("Tower Brocks", True, BLACK)
        title_rect = title.get_rect(center=(400, 120))
        self.screen.blit(title, title_rect)
        
        # Кнопки
        for button in self.buttons.values():
            button.draw(self.screen)
    
    def handle_event(self, event):
        """Обработка событий"""
        for key, button in self.buttons.items():
            if button.handle_event(event):
                return key
        return None
