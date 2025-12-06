import pygame
from src.constants import *


class Button:
    def __init__(self, x, y, width, height, text, font,
                 color=(100, 180, 255),          # небесно-голубой
                 text_color=WHITE,
                 hover_color=(80, 160, 235)):   # чуть темнее при наведении
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        """Отрисовка кнопки с тенью и закруглёнными углами."""
        base_color = self.hover_color if self.is_hovered else self.color

        # Тень
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=10)

        # Кнопка
        pygame.draw.rect(screen, base_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, 2, border_radius=10)

        # Текст
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Обработка событий."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class TowerCard:
    def __init__(self, x, y, tower_id, tower_name, price,
                 is_unlocked, is_selected, preview_sprite):
        # высота уменьшена с 210 до 200
        self.rect = pygame.Rect(x, y, 160, 200)
        self.tower_id = tower_id
        self.tower_name = tower_name
        self.price = price
        self.is_unlocked = is_unlocked
        self.is_selected = is_selected
        self.preview_sprite = preview_sprite
        self.is_hovered = False

        self.font = pygame.font.Font("freesansbold.ttf", 18)
        self.small_font = pygame.font.Font("freesansbold.ttf", 14)

        # Прямоугольник кнопки "Купить"/"Выбрать" внутри карточки
        self.button_rect = pygame.Rect(
            self.rect.x + 20,
            self.rect.y + 165,          # было 175
            self.rect.width - 40,
            26
        )

    def draw(self, screen):
        # Фон карточки
        if self.is_selected:
            color = (144, 238, 144)       # светло-зелёный
        elif self.is_hovered:
            color = (200, 220, 255)       # голубоватый
        else:
            color = (210, 210, 210)       # светло-серый

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=8)

        # Превью
        if self.preview_sprite:
            sprite_rect = self.preview_sprite.get_rect(
                center=(self.rect.centerx, self.rect.y + 70)
            )
            screen.blit(self.preview_sprite, sprite_rect)

        # Название
        name_surf = self.font.render(self.tower_name, True, BLACK)
        name_rect = name_surf.get_rect(
            center=(self.rect.centerx, self.rect.y + 125)  # было 135
        )
        screen.blit(name_surf, name_rect)

        # Цена (если не куплено)
        if not self.is_unlocked:
            price_surf = self.small_font.render(
                f"{self.price} монет", True, BLACK
            )
            price_rect = price_surf.get_rect(
                center=(self.rect.centerx, self.rect.y + 145)  # было 155
            )
            screen.blit(price_surf, price_rect)

        # Кнопка внизу карточки
        if not self.is_unlocked:
            btn_text = "Купить"
            btn_color = (255, 215, 0)     # жёлтая
        elif self.is_selected:
            btn_text = "Выбрано"
            btn_color = (120, 200, 120)
        else:
            btn_text = "Выбрать"
            btn_color = (180, 220, 255)

        pygame.draw.rect(screen, btn_color, self.button_rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, self.button_rect, 2, border_radius=6)

        btn_surf = self.small_font.render(btn_text, True, BLACK)
        btn_rect = btn_surf.get_rect(center=self.button_rect.center)
        screen.blit(btn_surf, btn_rect)

    def handle_event(self, event):
        """Возвращает 'button' или None."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return "button"

        return None


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font("freesansbold.ttf", 64)
        self.font_button = pygame.font.Font("freesansbold.ttf", 32)

        btn_w, btn_h = 260, 70
        center_x = SCREEN_WIDTH // 2 - btn_w // 2

        self.buttons = {
            'play': Button(center_x, 260, btn_w, btn_h, "Играть", self.font_button),
            'shop': Button(center_x, 350, btn_w, btn_h, "Магазин", self.font_button),
            'quit': Button(center_x, 440, btn_w, btn_h, "Выход", self.font_button),
        }

    def draw(self, background):
        """Отрисовка главного меню."""
        self.screen.blit(background, (0, 0))

        title = self.font_title.render("Tower Bloxx", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(title, title_rect)

        for button in self.buttons.values():
            button.draw(self.screen)

    def handle_event(self, event):
        """Обработка событий."""
        for key, button in self.buttons.items():
            if button.handle_event(event):
                return key
        return None

