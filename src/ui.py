import pygame
from src.constants import *


class Button:
    def __init__(self, x, y, width, height, text, font,
                 color=(180, 200, 230),          # базовый цвет
                 text_color=BLACK,
                 hover_color=(150, 180, 220)):   # при наведении
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
        if self.text:
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
        # немного больше: шире и выше
        self.rect = pygame.Rect(x, y, 180, 180)
        self.tower_id = tower_id
        self.tower_name = tower_name
        self.price = price
        self.is_unlocked = is_unlocked
        self.is_selected = is_selected
        self.preview_sprite = preview_sprite
        self.is_hovered = False

        self.font = pygame.font.Font("freesansbold.ttf", 18)
        self.small_font = pygame.font.Font("freesansbold.ttf", 14)

        # Кнопка "Купить"/"Выбрать" внутри карточки
        self.button_rect = pygame.Rect(
            self.rect.x + 20,
            self.rect.y + self.rect.height - 36,  # ближе к низу
            self.rect.width - 40,
            26
        )

    def draw(self, screen):
        if self.is_selected:
            color = (144, 238, 144)
        elif self.is_hovered:
            color = (200, 220, 255)
        else:
            color = (210, 210, 210)

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=8)

        # Превью
        if self.preview_sprite:
            sprite_rect = self.preview_sprite.get_rect(
                center=(self.rect.centerx, self.rect.y + 55)
            )
            screen.blit(self.preview_sprite, sprite_rect)

        # Название
        name_surf = self.font.render(self.tower_name, True, BLACK)
        name_rect = name_surf.get_rect(
            center=(self.rect.centerx, self.rect.y + 105)
        )
        screen.blit(name_surf, name_rect)

        # Цена (если не куплено)
        if not self.is_unlocked:
            price_surf = self.small_font.render(
                f"{self.price} монет", True, BLACK
            )
            price_rect = price_surf.get_rect(
                center=(self.rect.centerx, self.rect.y + 130)
            )
            screen.blit(price_surf, price_rect)

        # Кнопка
        if not self.is_unlocked:
            btn_text = "Купить"
            btn_color = (255, 215, 0)
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
            'settings': Button(center_x, 440, btn_w, btn_h, "Настройки", self.font_button),
            'quit': Button(center_x, 530, btn_w, btn_h, "Выход", self.font_button),
        }

    def draw(self, background):
        self.screen.blit(background, (0, 0))

        # Название игры с заливкой
        title_text = "Tower Bloxx"
        title_surf = self.font_title.render(title_text, True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))

        # фон под заголовком как у кнопок
        padding_x = 30
        padding_y = 15
        bg_rect = pygame.Rect(
            title_rect.left - padding_x,
            title_rect.top - padding_y,
            title_rect.width + padding_x * 2,
            title_rect.height + padding_y * 2,
        )
        pygame.draw.rect(self.screen, (180, 200, 230), bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, (20, 20, 20), bg_rect, 2, border_radius=12)
        self.screen.blit(title_surf, title_rect)

        for button in self.buttons.values():
            button.draw(self.screen)

    def handle_event(self, event):
        for key, button in self.buttons.items():
            if button.handle_event(event):
                return key
        return None


class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        # размер текста как у названия игры/кнопок
        self.font_title = pygame.font.Font("freesansbold.ttf", 48)
        self.font_label = pygame.font.Font("freesansbold.ttf", 32)
        self.font_button = pygame.font.Font("freesansbold.ttf", 28)

        # иконки громкости
        raw_loud = pygame.image.load(f"{ASSETS_PATH}ui/loud.png").convert_alpha()
        raw_silence = pygame.image.load(f"{ASSETS_PATH}ui/silence.png").convert_alpha()
        ICON_SIZE = (40, 40)
        self.icon_loud = pygame.transform.smoothscale(raw_loud, ICON_SIZE)
        self.icon_silence = pygame.transform.smoothscale(raw_silence, ICON_SIZE)

        # иконки фона
        raw_dark = pygame.image.load(f"{ASSETS_PATH}ui/dark.png").convert_alpha()
        raw_light = pygame.image.load(f"{ASSETS_PATH}ui/light.png").convert_alpha()
        self.icon_dark = pygame.transform.smoothscale(raw_dark, ICON_SIZE)
        self.icon_light = pygame.transform.smoothscale(raw_light, ICON_SIZE)

        # Вычисляем максимальную ширину среди всех подписей для центрирования
        labels_text = ["Музыка", "Звуки", "Фон меню/магазина"]
        max_label_width = 0
        for text in labels_text:
            surf = self.font_label.render(text, True, BLACK)
            if surf.get_width() > max_label_width:
                max_label_width = surf.get_width()

        # Ширина блока с подписью
        label_bg_width = max_label_width + 40
        
        # Размеры кнопки
        btn_size = 60
        gap_between = 20  # расстояние между подписью и кнопкой
        
        # Общая ширина блока (подпись + промежуток + кнопка)
        total_width = label_bg_width + gap_between + btn_size
        
        # Центрируем блок
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # позиция подписей
        label_x = start_x
        # позиция кнопок
        btn_x = start_x + label_bg_width + gap_between
        
        top_y = 220
        gap_y = 100

        # кнопки по центру
        self.mute_music_button = Button(btn_x, top_y, btn_size, btn_size, "", self.font_button)
        self.mute_sfx_button = Button(btn_x, top_y + gap_y, btn_size, btn_size, "", self.font_button)
        self.bg_toggle_button = Button(btn_x, top_y + gap_y * 2, btn_size, btn_size, "", self.font_button)

        # сохраняем параметры для отрисовки
        self.label_x = label_x
        self.label_bg_width = label_bg_width

        # кнопка "Назад"
        self.back_button = Button(20, SCREEN_HEIGHT - 80, 180, 50, "Назад", self.font_button)

        # состояния
        self.music_muted = False
        self.sfx_muted = False
        self.bg_index = 0   # 0 = dark/bg_shop_1, 1 = light/bg_shop_2

    def draw(self, background):
        self.screen.blit(background, (0, 0))

        # слово "Настройки" с заливкой цвета кнопок
        title_text = "Настройки"
        title_surf = self.font_title.render(title_text, True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))

        # фон под заголовком как у кнопок
        padding_x = 20
        padding_y = 10
        bg_rect = pygame.Rect(
            title_rect.left - padding_x,
            title_rect.top - padding_y,
            title_rect.width + padding_x * 2,
            title_rect.height + padding_y * 2,
        )
        pygame.draw.rect(self.screen, (180, 200, 230), bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, (20, 20, 20), bg_rect, 2, border_radius=12)
        self.screen.blit(title_surf, title_rect)

        # подписи с одинаковой шириной заливки
        labels = [
            ("Музыка", self.mute_music_button),
            ("Звуки", self.mute_sfx_button),
            ("Фон меню/магазина", self.bg_toggle_button),
        ]

        for text, btn in labels:
            surf = self.font_label.render(text, True, BLACK)
            
            # заливка фиксированной ширины
            label_bg_rect = pygame.Rect(
                self.label_x,
                btn.rect.centery - 30,
                self.label_bg_width,
                60
            )
            pygame.draw.rect(self.screen, (180, 200, 230), label_bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (20, 20, 20), label_bg_rect, 2, border_radius=10)
            
            # текст по центру заливки
            text_rect = surf.get_rect(center=label_bg_rect.center)
            self.screen.blit(surf, text_rect)

        # кнопки
        self.mute_music_button.draw(self.screen)
        self.mute_sfx_button.draw(self.screen)
        self.bg_toggle_button.draw(self.screen)

        # иконки для состояний
        icon_music = self.icon_silence if self.music_muted else self.icon_loud
        icon_sfx = self.icon_silence if self.sfx_muted else self.icon_loud
        icon_bg = self.icon_dark if self.bg_index == 0 else self.icon_light

        self.screen.blit(icon_music, icon_music.get_rect(center=self.mute_music_button.rect.center))
        self.screen.blit(icon_sfx, icon_sfx.get_rect(center=self.mute_sfx_button.rect.center))
        self.screen.blit(icon_bg, icon_bg.get_rect(center=self.bg_toggle_button.rect.center))

        # кнопка назад
        self.back_button.draw(self.screen)

    def handle_event(self, event):
        if self.mute_music_button.handle_event(event):
            self.music_muted = not self.music_muted
            return 'mute_music'

        if self.mute_sfx_button.handle_event(event):
            self.sfx_muted = not self.sfx_muted
            return 'mute_sfx'

        if self.bg_toggle_button.handle_event(event):
            self.bg_index = 1 - self.bg_index
            return 'toggle_bg'

        if self.back_button.handle_event(event):
            return 'back'

        return None
