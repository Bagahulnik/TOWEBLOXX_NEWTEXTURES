import pygame

from src.constants import ASSETS_PATH, UI_PATH, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK


class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font,
        color=(180, 200, 230),
        text_color=BLACK,
        hover_color=(150, 180, 220),
        click_sound=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.click_sound = click_sound

    def draw(self, screen):
        base_color = self.hover_color if self.is_hovered else self.color

        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=10)

        pygame.draw.rect(screen, base_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, 2, border_radius=10)

        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                if self.click_sound:
                    self.click_sound.play()
                return True

        return False


class TowerCard:
    def __init__(
        self,
        x,
        y,
        tower_id,
        tower_name,
        price,
        is_unlocked,
        is_selected,
        preview_sprite,
        click_sound=None,
    ):
        self.rect = pygame.Rect(x, y, 180, 180)
        self.tower_id = tower_id
        self.tower_name = tower_name
        self.price = price
        self.is_unlocked = is_unlocked
        self.is_selected = is_selected
        self.preview_sprite = preview_sprite
        self.is_hovered = False
        self.click_sound = click_sound

        self.font = pygame.font.Font("freesansbold.ttf", 18)
        self.small_font = pygame.font.Font("freesansbold.ttf", 14)

        self.button_rect = pygame.Rect(
            self.rect.x + 20,
            self.rect.y + self.rect.height - 36,
            self.rect.width - 40,
            26,
        )

        # флаг и таймер ошибки (мигание красным)
        self.error_flash = False
        self.error_flash_timer = 0  # в кадрах

    def trigger_error_flash(self, frames=20):
        """Включить мигание красным на несколько кадров."""
        self.error_flash = True
        self.error_flash_timer = frames

    def update(self):
        """Обновить состояние (уменьшаем таймер мигания)."""
        if self.error_flash:
            self.error_flash_timer -= 1
            if self.error_flash_timer <= 0:
                self.error_flash = False

    def draw(self, screen):
        base_color = (180, 200, 230)
        border_color = (20, 20, 20)

        # если ошибка активна — мигаем красным
        if self.error_flash and (self.error_flash_timer // 3) % 2 == 0:
            card_color = (255, 120, 120)
        else:
            card_color = base_color

        if self.is_selected:
            pygame.draw.rect(screen, (144, 238, 144), self.rect, border_radius=8)
            pygame.draw.rect(screen, border_color, self.rect, 4, border_radius=8)
        else:
            pygame.draw.rect(screen, card_color, self.rect, border_radius=8)
            pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=8)

        if self.preview_sprite:
            sprite_rect = self.preview_sprite.get_rect(
                center=(self.rect.centerx, self.rect.y + 55)
            )
            screen.blit(self.preview_sprite, sprite_rect)

        name_surf = self.font.render(self.tower_name, True, BLACK)
        name_rect = name_surf.get_rect(
            center=(self.rect.centerx, self.rect.y + 105)
        )
        screen.blit(name_surf, name_rect)

        if not self.is_unlocked:
            price_surf = self.small_font.render(
                f"{self.price} монет", True, BLACK
            )
            price_rect = price_surf.get_rect(
                center=(self.rect.centerx, self.rect.y + 130)
            )
            screen.blit(price_surf, price_rect)

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
                # ВНИМАНИЕ: сам клик-звук теперь будет играться в Shop
                # только если монет хватает. Здесь звук не трогаем.
                return "button"

        return None


class MainMenu:
    def __init__(self, screen, click_sound=None):
        self.screen = screen
        self.font_title = pygame.font.Font("freesansbold.ttf", 64)
        self.font_button = pygame.font.Font("freesansbold.ttf", 32)
        self.click_sound = click_sound

        btn_w, btn_h = 260, 70
        center_x = SCREEN_WIDTH // 2 - btn_w // 2

        self.buttons = {
            "play": Button(
                center_x,
                260,
                btn_w,
                btn_h,
                "Играть",
                self.font_button,
                click_sound=click_sound,
            ),
            "shop": Button(
                center_x,
                350,
                btn_w,
                btn_h,
                "Магазин",
                self.font_button,
                click_sound=click_sound,
            ),
            "settings": Button(
                center_x,
                440,
                btn_w,
                btn_h,
                "Настройки",
                self.font_button,
                click_sound=click_sound,
            ),
            "quit": Button(
                center_x,
                530,
                btn_w,
                btn_h,
                "Выход",
                self.font_button,
                click_sound=click_sound,
            ),
        }

    def draw(self, background):
        self.screen.blit(background, (0, 0))

        title_text = "Tower Bloxx"
        title_surf = self.font_title.render(title_text, True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))

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
    def __init__(self, screen, click_sound=None):
        self.screen = screen
        self.font_title = pygame.font.Font("freesansbold.ttf", 48)
        self.font_label = pygame.font.Font("freesansbold.ttf", 32)
        self.font_button = pygame.font.Font("freesansbold.ttf", 28)
        self.click_sound = click_sound

        self.music_muted = False
        self.sfx_muted = False
        self.bg_index = 0
        self.music_index = 0

        # иконки громкости
        raw_loud = pygame.image.load(f"{UI_PATH}loud.png").convert_alpha()
        raw_silence = pygame.image.load(f"{UI_PATH}silence.png").convert_alpha()
        ICON_SIZE = (40, 40)
        self.icon_loud = pygame.transform.smoothscale(raw_loud, ICON_SIZE)
        self.icon_silence = pygame.transform.smoothscale(raw_silence, ICON_SIZE)

        # иконки фона
        raw_dark = pygame.image.load(f"{UI_PATH}dark.png").convert_alpha()
        raw_light = pygame.image.load(f"{UI_PATH}light.png").convert_alpha()
        self.icon_dark = pygame.transform.smoothscale(raw_dark, ICON_SIZE)
        self.icon_light = pygame.transform.smoothscale(raw_light, ICON_SIZE)

        # стрелки
        raw_left = pygame.image.load(f"{UI_PATH}arrow_left.png").convert_alpha()
        raw_right = pygame.image.load(f"{UI_PATH}arrow_right.png").convert_alpha()
        self.ARROW_SIZE = (32, 32)
        self.icon_left = pygame.transform.smoothscale(raw_left, self.ARROW_SIZE)
        self.icon_right = pygame.transform.smoothscale(raw_right, self.ARROW_SIZE)

        self.arrow_left_rect = pygame.Rect(0, 0, *self.ARROW_SIZE)
        self.arrow_right_rect = pygame.Rect(0, 0, *self.ARROW_SIZE)

        # геометрия блока настроек
        labels_text = ["Музыка", "Звуки", "Фон меню/магазина"]
        max_label_width = 0
        for text in labels_text:
            surf = self.font_label.render(text, True, BLACK)
            max_label_width = max(max_label_width, surf.get_width())

        label_bg_width = max_label_width + 40
        btn_size = 60
        gap_between = 20
        total_width = label_bg_width + gap_between + btn_size
        start_x = (SCREEN_WIDTH - total_width) // 2
        self.label_x = start_x
        btn_x = start_x + label_bg_width + gap_between

        top_y = 220
        gap_y = 100

        self.mute_music_button = Button(
            btn_x, top_y, btn_size, btn_size, "", self.font_button, click_sound=click_sound
        )
        self.mute_sfx_button = Button(
            btn_x,
            top_y + gap_y,
            btn_size,
            btn_size,
            "",
            self.font_button,
            click_sound=click_sound,
        )
        self.bg_toggle_button = Button(
            btn_x,
            top_y + gap_y * 2,
            btn_size,
            btn_size,
            "",
            self.font_button,
            click_sound=click_sound,
        )

        self.label_bg_width = label_bg_width
        self.back_button = Button(
            20,
            SCREEN_HEIGHT - 80,
            180,
            50,
            "Назад",
            self.font_button,
            click_sound=click_sound,
        )

    def draw(self, background):
        self.screen.blit(background, (0, 0))

        title_text = "Настройки"
        title_surf = self.font_title.render(title_text, True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))

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

        base_color = (180, 200, 230)
        border_color = (20, 20, 20)

        # --- Блок музыки: "< Музыка 1/5 >" ---
        music_block_rect = pygame.Rect(
            self.label_x,
            self.mute_music_button.rect.centery - 30,
            self.label_bg_width,
            60,
        )

        pygame.draw.rect(self.screen, base_color, music_block_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, music_block_rect, 2, border_radius=10)

        center_y = music_block_rect.centery
        pad_side = 12

        self.arrow_left_rect.center = (
            music_block_rect.left + pad_side + self.ARROW_SIZE[0] // 2,
            center_y,
        )
        self.arrow_right_rect.center = (
            music_block_rect.right - pad_side - self.ARROW_SIZE[0] // 2,
            center_y,
        )

        for rect, icon in [(self.arrow_left_rect, self.icon_left),
                           (self.arrow_right_rect, self.icon_right)]:
            pad = 4
            bg_r = pygame.Rect(
                rect.left - pad,
                rect.top - pad,
                rect.width + pad * 2,
                rect.height + pad * 2,
            )
            pygame.draw.rect(self.screen, base_color, bg_r, border_radius=8)
            pygame.draw.rect(self.screen, border_color, bg_r, 2, border_radius=8)
            self.screen.blit(icon, rect)

        text_surf = self.font_label.render("Музыка", True, BLACK)
        track_surf = self.font_label.render(f"{self.music_index + 1}/5", True, BLACK)

        available_left = self.arrow_left_rect.right + 10
        available_right = self.arrow_right_rect.left - 10

        track_rect = track_surf.get_rect()
        track_rect.centery = center_y
        track_rect.right = available_right - 20

        mid_x = (available_left + track_rect.left) / 2
        text_rect = text_surf.get_rect()
        text_rect.centery = center_y
        text_rect.centerx = mid_x + 20

        self.screen.blit(text_surf, text_rect)
        self.screen.blit(track_surf, track_rect)

        # --- Остальные подписи (звук / фон) ---
        labels_rest = [
            ("Звуки", self.mute_sfx_button),
            ("Фон меню/магазина", self.bg_toggle_button),
        ]

        for text, btn in labels_rest:
            surf = self.font_label.render(text, True, BLACK)
            label_bg_rect = pygame.Rect(
                self.label_x,
                btn.rect.centery - 30,
                self.label_bg_width,
                60,
            )
            pygame.draw.rect(self.screen, base_color, label_bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, label_bg_rect, 2, border_radius=10)
            txt_rect = surf.get_rect(center=label_bg_rect.center)
            self.screen.blit(surf, txt_rect)

        self.mute_music_button.draw(self.screen)
        self.mute_sfx_button.draw(self.screen)
        self.bg_toggle_button.draw(self.screen)

        icon_music = self.icon_silence if self.music_muted else self.icon_loud
        icon_sfx = self.icon_silence if self.sfx_muted else self.icon_loud
        icon_bg = self.icon_dark if self.bg_index == 0 else self.icon_light

        self.screen.blit(
            icon_music,
            icon_music.get_rect(center=self.mute_music_button.rect.center),
        )
        self.screen.blit(
            icon_sfx,
            icon_sfx.get_rect(center=self.mute_sfx_button.rect.center),
        )
        self.screen.blit(
            icon_bg,
            icon_bg.get_rect(center=self.bg_toggle_button.rect.center),
        )

        self.back_button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

        if self.mute_music_button.handle_event(event):
            self.music_muted = not self.music_muted
            return "mute_music"

        if self.mute_sfx_button.handle_event(event):
            self.sfx_muted = not self.sfx_muted
            return "mute_sfx"

        if self.bg_toggle_button.handle_event(event):
            self.bg_index = 1 - self.bg_index
            return "toggle_bg"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.arrow_left_rect.collidepoint(event.pos):
                if self.click_sound:
                    self.click_sound.play()
                self.music_index = (self.music_index - 1) % 5
                return "music_change"

            if self.arrow_right_rect.collidepoint(event.pos):
                if self.click_sound:
                    self.click_sound.play()
                self.music_index = (self.music_index + 1) % 5
                return "music_change"

        if self.back_button.handle_event(event):
            return "back"

        return None
