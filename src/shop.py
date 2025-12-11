import pygame


from src.ui import Button, TowerCard
from src.constants import *
from src.asset_loader import AssetLoader



class Shop:
    def __init__(
        self,
        screen,
        save_manager,
        asset_loader: AssetLoader,
        click_sound=None,
        error_sound=None,
        coin_sound=None,  # ✅ ДОБАВЛЕН ПАРАМЕТР
    ):
        self.screen = screen
        self.save_manager = save_manager
        self.asset_loader = asset_loader
        self.click_sound = click_sound
        self.error_sound = error_sound
        self.coin_sound = coin_sound  # ✅ ИСПРАВЛЕНО (было без self)


        self.font_title = pygame.font.Font("freesansbold.ttf", 32)
        self.font_coins = pygame.font.Font("freesansbold.ttf", 22)


        btn_w, btn_h = 220, 55
        self.back_button = Button(
            (SCREEN_WIDTH - btn_w) // 2,
            SCREEN_HEIGHT - 57,
            btn_w,
            btn_h,
            "Назад",
            pygame.font.Font("freesansbold.ttf", 28),
            click_sound=click_sound,
        )


        self.tower_cards = []
        self.create_tower_cards()


    def create_tower_cards(self):
        """Создание карточек башен: 2 в ширину, 4 в высоту, по центру экрана."""
        self.tower_cards = []


        cols = 2
        card_w = 180
        card_h = 180
        h_gap = 30
        v_gap = 20


        total_width = cols * card_w + (cols - 1) * h_gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 120


        for i in range(1, 9):
            col = (i - 1) % cols
            row = (i - 1) // cols
            x = start_x + col * (card_w + h_gap)
            y = start_y + row * (card_h + v_gap)


            is_unlocked = self.save_manager.is_tower_unlocked(i)
            is_selected = self.save_manager.get_selected_tower() == i


            sprites = self.asset_loader.load_tower_sprites(i)
            preview = sprites["mid"][0]


            card = TowerCard(
                x,
                y,
                i,
                TOWER_NAMES[i],
                TOWER_PRICES[i],
                is_unlocked,
                is_selected,
                preview,
                click_sound=None,  # клик по кнопке теперь не проигрывает звук сам
            )
            self.tower_cards.append(card)


    def draw(self, background):
        """Отрисовка магазина."""
        self.screen.blit(background, (0, 0))


        title_text = "Магазин башен"
        title_surf = self.font_title.render(title_text, True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 70))


        padding_x = 30
        padding_y = 10
        title_bg_rect = pygame.Rect(
            title_rect.left - padding_x,
            title_rect.top - padding_y,
            title_rect.width + padding_x * 2,
            title_rect.height + padding_y * 2,
        )


        base_color = (180, 200, 230)
        border_color = (20, 20, 20)


        pygame.draw.rect(self.screen, base_color, title_bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, title_bg_rect, 2, border_radius=12)
        self.screen.blit(title_surf, title_rect)


        coins = self.save_manager.get_coins()
        coin_color = (255, 215, 0)
        coin_pos = (SCREEN_WIDTH - 90, 70)


        pygame.draw.circle(self.screen, coin_color, coin_pos, 10)
        pygame.draw.circle(self.screen, (180, 140, 0), coin_pos, 10, 2)


        coins_text = self.font_coins.render(str(coins), True, BLACK)
        coins_rect = coins_text.get_rect(midleft=(coin_pos[0] + 18, coin_pos[1]))
        self.screen.blit(coins_text, coins_rect)


        # обновляем карточки перед рисованием (для мигания)
        for card in self.tower_cards:
            card.update()
            card.draw(self.screen)


        self.back_button.draw(self.screen)


    def handle_event(self, event):
        """Обработка событий магазина."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"


        if self.back_button.handle_event(event):
            return "back"


        for card in self.tower_cards:
            res = card.handle_event(event)
            if res == "button":
                return self.handle_card_button(card)


        return None


    def handle_card_button(self, card: TowerCard):
        """Нажатие на кнопку на карточке."""
        tower_id = card.tower_id


        if not card.is_unlocked:
            # сначала проверяем, хватает ли монет — без звука клика
            if self.save_manager.spend_coins(card.price):
                # 🪙 ПОКУПКА УСПЕШНА → ЗВУК МОНЕТЫ
                if self.coin_sound:
                    self.coin_sound.play()
                self.save_manager.unlock_tower(tower_id)
                self.save_manager.set_selected_tower(tower_id)
                self.create_tower_cards()
                return "purchased"
            else:
                # монет не хватает → ТОЛЬКО ошибка + мигание красным
                if self.error_sound:
                    self.error_sound.play()
                card.trigger_error_flash()
                return "not_enough_coins"
        else:
            # выбор уже купленной башни: нормальный клик
            if self.click_sound:
                self.click_sound.play()
            self.save_manager.set_selected_tower(tower_id)
            self.create_tower_cards()
            return "selected"


    def update_cards(self):
        """Обновить состояние карточек (после покупки/выбора)."""
        for card in self.tower_cards:
            card.is_unlocked = self.save_manager.is_tower_unlocked(card.tower_id)
            card.is_selected = (
                self.save_manager.get_selected_tower() == card.tower_id
            )
