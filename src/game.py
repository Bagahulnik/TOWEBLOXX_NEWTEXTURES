import math
import pygame
from pygame import mixer

from src.block import Block
from src.tower import Tower
from src.constants import *
from src.balloon_guy import BalloonGuy


class ImageButton:
    """Кнопка с картинкой и фоном как в настройках."""
    def __init__(self, x, y, image_path, size=(60, 60), click_sound=None):
        raw_image = pygame.image.load(image_path).convert_alpha()
        # уменьшаем спрайт на 2px по длине и ширине
        sprite_size = (size[0] - 2, size[1] - 2)
        self.image = pygame.transform.smoothscale(raw_image, sprite_size)
        self.size = size
        self.rect = pygame.Rect(x - size[0] // 2, y - size[1] // 2, size[0], size[1])
        self.is_hovered = False
        self.click_sound = click_sound

    def draw(self, screen):
        base_color = (180, 200, 230)
        border_color = (20, 20, 20)
        # затемняем цвет при наведении
        if self.is_hovered:
            base_color = (140, 160, 190)
        # фон кнопки
        pygame.draw.rect(screen, base_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        # центрируем картинку (она на 2px меньше)
        img_x = self.rect.x + 1
        img_y = self.rect.y + 1
        screen.blit(self.image, (img_x, img_y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.click_sound:
                    self.click_sound.play()
                return True
        return False


class Game:
    def __init__(self, screen, save_manager, asset_loader, sound_muted=False):
        self.screen = screen
        self.save_manager = save_manager
        self.asset_loader = asset_loader
        self.sound_muted = sound_muted

        self.crane_image = pygame.image.load(f"{CRANE_PATH}crane.png").convert_alpha()
        self.rope_hook_image = pygame.image.load(f"{CRANE_PATH}rope_with_hook.png").convert_alpha()

        # фоны
        self.bg_big = pygame.image.load(f"{ASSETS_PATH}bg/bg_group.png").convert()
        self.bg_y = SCREEN_HEIGHT - self.bg_big.get_height()
        
        # фон для конечного экрана
        self.bg_end = pygame.image.load(f"{ASSETS_PATH}bg/bg_end.png").convert()

        self.sounds = asset_loader.load_sounds()
        if self.sound_muted:
            for sound in self.sounds.values():
                sound.set_volume(0.0)

        self.current_tower_id = save_manager.get_selected_tower()
        self.tower_sprites = asset_loader.load_tower_sprites(self.current_tower_id)

        # башня и блок
        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        # летающие человечки
        self.balloon_guys = pygame.sprite.Group()
        self._create_balloon_guys()

        self.score = 0
        self.misses = 0
        self.force = INITIAL_FORCE
        self.coins_earned = 0

        # параметры анимации скролла фона (старая рабочая система)
        self.bg_anim_active = False
        self.bg_anim_progress = 0
        self.bg_anim_target_y = 0

        self.score_font = pygame.font.Font("freesansbold.ttf", 32)
        self.miss_font = pygame.font.Font("freesansbold.ttf", 24)
        self.over_font = pygame.font.Font("freesansbold.ttf", 64)
        self.mini_font = pygame.font.Font("freesansbold.ttf", 16)
        self.reason_font = pygame.font.Font("freesansbold.ttf", 24)
        self.coins_font = pygame.font.Font("freesansbold.ttf", 24)
        self.hint_font = pygame.font.Font("freesansbold.ttf", 18)

        # шрифты для подсказок
        self.hint_title_font = pygame.font.Font("freesansbold.ttf", 40)
        self.hint_text_font = pygame.font.Font("freesansbold.ttf", 28)
        self.confirm_font = pygame.font.Font("freesansbold.ttf", 24)
        self.confirm_small_font = pygame.font.Font("freesansbold.ttf", 18)

        self.BLINK_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BLINK_EVENT, 800)

        self.game_over = False
        self.game_over_reason = None

        # подсказка в начале игры
        self.show_start_hint = True

        # окно подтверждения выхода
        self.show_exit_confirm = False

        # человечки начинают лететь только после первого скролла фона
        self.people_enabled = False

        # кнопки для game over экрана (размер 60×60, опущены ниже текста)
        cx = SCREEN_WIDTH // 2
        btn_y = 430
        spacing = 100
        click_sound = self.sounds['click']
        self.btn_back = ImageButton(cx - spacing, btn_y, f"{UI_PATH}arrow_back.png", size=(60, 60), click_sound=click_sound)
        self.btn_shop = ImageButton(cx, btn_y, f"{UI_PATH}store.png", size=(60, 60), click_sound=click_sound)
        self.btn_restart = ImageButton(cx + spacing, btn_y, f"{UI_PATH}restart.png", size=(60, 60), click_sound=click_sound)

        # кнопка рестарт в правом верхнем углу во время игры (опущена на 5px с 30 до 35)
        self.btn_restart_game = ImageButton(SCREEN_WIDTH - 40, 35, f"{UI_PATH}restart.png", size=(50, 50), click_sound=click_sound)

    def _create_balloon_guys(self):
        xs = [80, 180, 300, 420]
        speed_y = -1.2
        # порядок вылета: 0, 2, 1, 3
        order = [0, 2, 1, 3]

        for n, idx in enumerate(order):
            delay_frames = n * 2 * FPS  # 0, 2, 4, 6 секунд
            guy = BalloonGuy(
                person_id=idx + 1,
                start_x=xs[idx],
                speed_y=speed_y,
                start_delay_frames=delay_frames,
            )
            self.balloon_guys.add(guy)

    def show_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, BLACK)
        misses_text = self.miss_font.render(
            f"Промахи: {self.misses}/{MAX_MISSES}", True, BLACK
        )

        padding_x = 10
        padding_y = 10

        w = max(score_text.get_width(), misses_text.get_width()) + padding_x * 2
        h = score_text.get_height() + misses_text.get_height() + padding_y * 3

        panel_rect = pygame.Rect(8, 8, w, h)

        base_color = (180, 200, 230)
        border_color = (20, 20, 20)

        pygame.draw.rect(self.screen, base_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, panel_rect, 2, border_radius=10)

        x_center = panel_rect.centerx
        y = panel_rect.top + padding_y + score_text.get_height() // 2

        score_rect = score_text.get_rect(center=(x_center, y))
        self.screen.blit(score_text, score_rect)

        y += score_text.get_height() + padding_y
        misses_rect = misses_text.get_rect(center=(x_center, y))
        self.screen.blit(misses_text, misses_rect)

    def draw_background(self):
        self.screen.blit(self.bg_big, (0, self.bg_y))

    def draw(self):
        self.draw_background()
        self.screen.blit(self.crane_image, (0, 0))

        # людишки (когда включены)
        if self.people_enabled:
            self.balloon_guys.draw(self.screen)

        rope_end_x = ROPE_ORIGIN_X + ROPE_LENGTH * math.sin(self.block.angle)
        rope_end_y = ROPE_ORIGIN_Y + ROPE_LENGTH * math.cos(self.block.angle)

        angle_deg = math.degrees(self.block.angle)
        rot_rope_hook = pygame.transform.rotate(self.rope_hook_image, angle_deg)
        rope_hook_rect = rot_rope_hook.get_rect()

        mid_x = (ROPE_ORIGIN_X + rope_end_x) / 2
        mid_y = (ROPE_ORIGIN_Y + rope_end_y) / 2
        rope_hook_rect.center = (mid_x, mid_y)

        self.screen.blit(rot_rope_hook, rope_hook_rect)

        self.show_score()
        # кнопка рестарт в правом верхнем углу
        self.btn_restart_game.draw(self.screen)
        
        self.tower.wobble()

        if self.tower.get_display():
            self.tower.display(self.screen, scroll_y=0)
        self.block.display(self.screen, self.tower, scroll_y=0)

        # подсказка в начале игры
        if self.show_start_hint:
            self.draw_start_hint()

        if self.show_exit_confirm:
            self.draw_exit_confirm()

    def draw_start_hint(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        title = self.hint_title_font.render("Подсказка", True, WHITE)
        line1 = self.hint_text_font.render("Нажмите SPACE,", True, WHITE)
        line2 = self.hint_text_font.render("чтобы поставить блок", True, WHITE)

        cx = SCREEN_WIDTH // 2
        title_rect = title.get_rect(center=(cx, 260))
        line1_rect = line1.get_rect(center=(cx, 310))
        line2_rect = line2.get_rect(center=(cx, 350))

        self.screen.blit(title, title_rect)
        self.screen.blit(line1, line1_rect)
        self.screen.blit(line2, line2_rect)

    def draw_exit_confirm(self):
        """Окно подтверждения выхода во время игры."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel_width = 450
        panel_height = 220
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        panel_rect = pygame.Rect(cx - panel_width // 2, cy - panel_height // 2, panel_width, panel_height)
        base_color = (180, 200, 230)
        border_color = (20, 20, 20)

        pygame.draw.rect(self.screen, base_color, panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, border_color, panel_rect, 3, border_radius=16)

        # многострочный текст
        title1 = self.confirm_font.render("Вы уверены что", True, BLACK)
        title2 = self.confirm_font.render("хотите выйти?", True, BLACK)
        line1 = self.confirm_small_font.render("ENTER - подтвердить", True, BLACK)
        line2 = self.confirm_small_font.render("ESC - отменить", True, BLACK)

        title1_rect = title1.get_rect(center=(cx, cy - 50))
        title2_rect = title2.get_rect(center=(cx, cy - 20))
        line1_rect = line1.get_rect(center=(cx, cy + 30))
        line2_rect = line2.get_rect(center=(cx, cy + 60))

        self.screen.blit(title1, title1_rect)
        self.screen.blit(title2, title2_rect)
        self.screen.blit(line1, line1_rect)
        self.screen.blit(line2, line2_rect)

    def handle_game_events(self, event):
        if self.show_exit_confirm:
            # обработка окна подтверждения выхода
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'confirm_exit'
                elif event.key == pygame.K_ESCAPE:
                    self.show_exit_confirm = False
                    return None

        # кнопка рестарт в игре
        if self.btn_restart_game.handle_event(event):
            return 'restart_game'

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_exit_confirm = True
            elif event.key == pygame.K_SPACE:
                if self.show_start_hint:
                    self.show_start_hint = False
                if self.block.get_state() == "ready":
                    self.block.drop(self.tower)
        return None

    def update(self):
        state = self.block.get_state()

        if state == "ready":
            self.block.game_force = self.force
            self.block.swing()

        elif state == "dropped":
            self.block.drop(self.tower)

        elif state == "landed":
            if self.block.to_build(self.tower):
                self.tower.build(self.block)

                self.force *= 1.015

                if self.tower.is_golden():
                    if not self.sound_muted:
                        self.sounds['gold'].play()
                    self.score += 2
                    self.save_manager.add_coins(10)
                    self.coins_earned += 10
                else:
                    if not self.sound_muted:
                        self.sounds['build'].play()
                    self.score += 1
                    self.save_manager.add_coins(5)
                    self.coins_earned += 5

            if self.tower.size >= 2:
                self.block.collapse(self.tower)

        elif state == "over":
            surf = self.tower.unbuild(self.block)
            self.screen.blit(surf, (self.tower.x + self.tower.change, self.tower.y + 64))
            self.block.to_fall(self.tower)

            if not self.game_over_reason:
                if not self.sound_muted:
                    self.sounds['fall'].play()
                    self.sounds['over'].play()
                self.game_over_reason = "collapse"
                self.end_game()

        elif state == "scroll" and not self.tower.is_scrolling():
            self.block.respawn(self.tower)
            if self.tower.size >= 5:
                self.tower.reset()

        elif state == "miss":
            self.misses += 1
            if not self.sound_muted:
                self.sounds['fall'].play()

            if self.misses >= MAX_MISSES:
                self.game_over_reason = "misses"
                self.end_game()
            else:
                self.block.respawn(self.tower)

        # СТАРАЯ РАБОЧАЯ ЛОГИКА СКРОЛЛА ФОНА
        if self.bg_anim_active:
            self.bg_anim_progress += 1
            progress_ratio = self.bg_anim_progress / BG_SCROLL_DURATION

            self.bg_y = self.bg_anim_target_y * progress_ratio + self.bg_y * (1 - progress_ratio)

            if self.bg_anim_progress >= BG_SCROLL_DURATION:
                self.bg_y = self.bg_anim_target_y
                self.bg_anim_active = False
                self.bg_anim_progress = 0
        else:
            if self.tower.size >= TOWER_BLOCKS_PER_STEP:
                self.tower.size = BASE_ONSCREEN_BLOCKS
                self.tower.onscreen = self.tower.size
                self.tower.height = self.tower.size * BLOCK_HEIGHT
                base_y = SCREEN_HEIGHT - BLOCK_HEIGHT
                self.tower.y = base_y - (self.tower.height - BLOCK_HEIGHT)
                self.tower.xlist = self.tower.xlist[-self.tower.size:]
                self.tower.sprite_list = self.tower.sprite_list[-self.tower.size:]
                self.tower.golden_list = self.tower.golden_list[-self.tower.size:]

                self.bg_anim_active = True
                self.bg_anim_progress = 0
                self.bg_anim_target_y = self.bg_y + BG_SCROLL_STEP

                min_bg_y = SCREEN_HEIGHT - self.bg_big.get_height()
                if self.bg_anim_target_y < min_bg_y:
                    self.bg_anim_target_y = min_bg_y

                # как только первый раз начали скроллить фон — запускаем людей
                if not self.people_enabled:
                    self.people_enabled = True

        if self.people_enabled:
            self.balloon_guys.update()

        self.check_game_over()

    def check_game_over(self):
        width = self.tower.get_width()

        if width < -140:
            self.tower.collapse("l")
            if not self.game_over_reason:
                if not self.sound_muted:
                    self.sounds['over'].play()
                self.game_over_reason = "collapse"
                self.end_game()
        elif width > 140:
            self.tower.collapse("r")
            if not self.game_over_reason:
                if not self.sound_muted:
                    self.sounds['over'].play()
                self.game_over_reason = "collapse"
                self.end_game()

    def end_game(self):
        self.game_over = True
        self.save_manager.update_high_score(self.score)
        self.show_start_hint = False

    def reset(self):
        self.current_tower_id = self.save_manager.get_selected_tower()
        self.tower_sprites = self.asset_loader.load_tower_sprites(self.current_tower_id)

        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        self.misses = 0
        self.score = 0

        # сброс фона (старая система)
        self.bg_y = SCREEN_HEIGHT - self.bg_big.get_height()
        self.bg_anim_active = False
        self.bg_anim_progress = 0

        self.force = INITIAL_FORCE

        self.game_over = False
        self.game_over_reason = None
        self.coins_earned = 0

        self.show_start_hint = True
        self.show_exit_confirm = False
        self.people_enabled = False

    def draw_game_over_screen(self):
        """Рисует экран game over на виртуальном screen."""
        self.screen.blit(self.bg_end, (0, 0))

        title = self.over_font.render("GAME OVER", True, BLACK)
        score_text = self.score_font.render(f"SCORE: {self.score}", True, BLACK)

        if self.game_over_reason == "misses":
            reason_str = f"Слишком много промахов ({MAX_MISSES})"
        else:
            reason_str = "Башня обрушилась"

        reason_text = self.reason_font.render(reason_str, True, (200, 0, 0))
        coins_str = f"+{self.coins_earned} монет"
        coins_text = self.coins_font.render(coins_str, True, BLACK)

        cx = SCREEN_WIDTH // 2
        panel_width = SCREEN_WIDTH - 80
        panel_height = 380
        base_color = (180, 200, 230)
        border_color = (20, 20, 20)

        panel_rect = pygame.Rect(cx - panel_width // 2, 160, panel_width, panel_height)
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4

        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=16)
        pygame.draw.rect(self.screen, base_color, panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, border_color, panel_rect, 3, border_radius=16)

        y = panel_rect.top + 40
        title_rect = title.get_rect(center=(cx, y))
        self.screen.blit(title, title_rect)

        y += 60
        score_rect = score_text.get_rect(center=(cx, y))
        self.screen.blit(score_text, score_rect)

        y += 45
        reason_rect = reason_text.get_rect(center=(cx, y))
        self.screen.blit(reason_text, reason_rect)

        y += 40
        coins_rect = coins_text.get_rect(center=(cx, y))
        self.screen.blit(coins_text, coins_rect)

        # кнопки внутри панели
        self.btn_back.draw(self.screen)
        self.btn_shop.draw(self.screen)
        self.btn_restart.draw(self.screen)

        # подсказки под кнопками
        hint_y = 500
        hint1 = self.hint_font.render("ESC", True, BLACK)
        hint2 = self.hint_font.render("S", True, BLACK)
        hint3 = self.hint_font.render("R", True, BLACK)
        btn_spacing = 100
        self.screen.blit(hint1, hint1.get_rect(center=(cx - btn_spacing, hint_y)))
        self.screen.blit(hint2, hint2.get_rect(center=(cx, hint_y)))
        self.screen.blit(hint3, hint3.get_rect(center=(cx + btn_spacing, hint_y)))

    def handle_game_over_input(self, event):
        """Обрабатывает нажатия на экране game over."""
        if self.btn_back.handle_event(event):
            return 'menu'
        if self.btn_shop.handle_event(event):
            return 'shop'
        if self.btn_restart.handle_event(event):
            return 'restart'

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'menu'
            elif event.key == pygame.K_s:
                return 'shop'
            elif event.key == pygame.K_r:
                return 'restart'
        return None
