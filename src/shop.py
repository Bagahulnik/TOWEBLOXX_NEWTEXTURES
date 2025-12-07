import pygame
from src.ui import Button, TowerCard
from src.constants import *
from src.asset_loader import AssetLoader


class Shop:
    def __init__(self, screen, save_manager, asset_loader: AssetLoader):
        self.screen = screen
        self.save_manager = save_manager
        self.asset_loader = asset_loader

        self.font_title = pygame.font.Font("freesansbold.ttf", 40)
        self.font_coins = pygame.font.Font("freesansbold.ttf", 22)

        # Кнопка "Назад" ближе к нижнему краю
        self.back_button = Button(
            20, SCREEN_HEIGHT - 80, 180, 50, "Назад",
            pygame.font.Font("freesansbold.ttf", 28)
        )

        self.tower_cards = []
        self.create_tower_cards()

    def create_tower_cards(self):
        """Создание карточек башен: 2 в ширину, 4 в высоту."""
        self.tower_cards = []

        cols = 2           # 2 столбца
        card_w = 180
        card_h = 180
        h_gap = 30         # горизонтальный промежуток
        v_gap = 20         # вертикальный промежуток
        start_x = 60       # левый отступ
        start_y = 110      # верхний отступ под заголовок

        for i in range(1, 9):
            col = (i - 1) % cols      # 0 или 1
            row = (i - 1) // cols     # 0..3

            x = start_x + col * (card_w + h_gap)
            y = start_y + row * (card_h + v_gap)

            is_unlocked = self.save_manager.is_tower_unlocked(i)
            is_selected = self.save_manager.get_selected_tower() == i

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
        """Отрисовка магазина."""
        # фон под магазин — используем background из main.py
        self.screen.blit(background, (0, 0))

        # Заголовок
        title = self.font_title.render("Магазин башен", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(title, title_rect)

        # Монеты: иконка + число
        coins = self.save_manager.get_coins()
        coin_color = (255, 215, 0)
        coin_pos = (SCREEN_WIDTH - 90, 70)
        pygame.draw.circle(self.screen, coin_color, coin_pos, 10)
        pygame.draw.circle(self.screen, (180, 140, 0), coin_pos, 10, 2)

        coins_text = self.font_coins.render(str(coins), True, BLACK)
        coins_rect = coins_text.get_rect(midleft=(coin_pos[0] + 18, coin_pos[1]))
        self.screen.blit(coins_text, coins_rect)

        # Карточки
        for card in self.tower_cards:
            card.draw(self.screen)

        # Кнопка "Назад"
        self.back_button.draw(self.screen)

    def handle_event(self, event):
        """Обработка событий магазина."""
        # Назад
        if self.back_button.handle_event(event):
            return "back"

        # Карточки
        for card in self.tower_cards:
            res = card.handle_event(event)
            if res == "button":
                return self.handle_card_button(card)
        return None

    def handle_card_button(self, card: TowerCard):
        """Нажатие на кнопку на карточке."""
        tower_id = card.tower_id

        if not card.is_unlocked:
            # Покупка
            if self.save_manager.spend_coins(card.price):
                self.save_manager.unlock_tower(tower_id)
                self.save_manager.set_selected_tower(tower_id)
                self.create_tower_cards()
                return "purchased"
            else:
                return "not_enough_coins"
        else:
            # Выбор
            self.save_manager.set_selected_tower(tower_id)
            self.create_tower_cards()
            return "selected"

    def update_cards(self):
        """Обновить состояние карточек (после покупки/выбора)."""
        for card in self.tower_cards:
            card.is_unlocked = self.save_manager.is_tower_unlocked(card.tower_id)
            card.is_selected = self.save_manager.get_selected_tower() == card.tower_id
