import math
import pygame
from pygame import mixer

from src.block import Block
from src.tower import Tower
from src.constants import *


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

        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        self.score = 0
        self.misses = 0
        self.force = INITIAL_FORCE
        self.coins_earned = 0

        self.bg_anim_active = False
        self.bg_anim_progress = 0
        self.bg_anim_target_y = 0

        self.score_font = pygame.font.Font("freesansbold.ttf", 32)
        self.miss_font = pygame.font.Font("freesansbold.ttf", 24)
        self.over_font = pygame.font.Font("freesansbold.ttf", 64)
        self.mini_font = pygame.font.Font("freesansbold.ttf", 16)
        self.reason_font = pygame.font.Font("freesansbold.ttf", 24)
        self.coins_font = pygame.font.Font("freesansbold.ttf", 24)

        # шрифты для подсказок
        self.hint_title_font = pygame.font.Font("freesansbold.ttf", 40)
        self.hint_text_font = pygame.font.Font("freesansbold.ttf", 28)

        self.BLINK_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BLINK_EVENT, 800)

        self.game_over = False
        self.game_over_reason = None

        # подсказка в начале игры
        self.show_start_hint = True

    def show_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        misses_text = self.miss_font.render(
            f"Промахи: {self.misses}/{MAX_MISSES}", True, BLACK
        )
        self.screen.blit(misses_text, (10, 50))

    def draw_background(self):
        self.screen.blit(self.bg_big, (0, self.bg_y))

    def draw(self):
        self.draw_background()
        self.screen.blit(self.crane_image, (0, 0))

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
        self.tower.wobble()

        if self.tower.get_display():
            self.tower.display(self.screen, scroll_y=0)
        self.block.display(self.screen, self.tower, scroll_y=0)

        # подсказка в начале игры
        if self.show_start_hint:
            self.draw_start_hint()

    def draw_start_hint(self):
        """Полупрозрачная подсказка в начале игры."""
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

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.show_start_hint:
                    self.show_start_hint = False
                if self.block.get_state() == "ready":
                    self.block.drop(self.tower)

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
        # чтобы стартовая подсказка не рисовалась поверх экрана конца
        self.show_start_hint = False

    def reset(self):
        self.current_tower_id = self.save_manager.get_selected_tower()
        self.tower_sprites = self.asset_loader.load_tower_sprites(self.current_tower_id)

        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        self.misses = 0
        self.score = 0

        self.bg_y = SCREEN_HEIGHT - self.bg_big.get_height()
        self.bg_anim_active = False
        self.bg_anim_progress = 0
        self.force = INITIAL_FORCE

        self.game_over = False
        self.game_over_reason = None
        self.coins_earned = 0

        # при новом запуске показываем подсказку снова
        self.show_start_hint = True

    def show_game_over_screen(self):
        title = self.over_font.render("GAME OVER", True, BLACK)
        score_text = self.score_font.render(f"SCORE: {self.score}", True, BLACK)

        if self.game_over_reason == "misses":
            reason_str = f"Слишком много промахов ({MAX_MISSES})"
        else:
            reason_str = "Башня обрушилась"

        reason_text = self.reason_font.render(reason_str, True, (200, 0, 0))

        coins_str = f"+{self.coins_earned} монет"
        coins_text = self.coins_font.render(coins_str, True, BLACK)

        button_text = self.mini_font.render("НАЖМИТЕ ЛЮБУЮ КНОПКУ", True, BLACK)
        blank_rect = button_text.get_rect()
        blank = pygame.Surface((blank_rect.size), pygame.SRCALPHA).convert_alpha()

        instructions = [button_text, blank]
        index = 1
        waiting = True

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYUP:
                    waiting = False
                    return 'menu'
                if event.type == self.BLINK_EVENT:
                    index = 1 if index == 0 else 0

            self.screen.blit(self.bg_end, (0, 0))

            cx = SCREEN_WIDTH // 2

            # панель в стиле кнопок меню
            panel_width = SCREEN_WIDTH - 80
            panel_height = 260
            base_color = (180, 200, 230)
            border_color = (20, 20, 20)

            panel_rect = pygame.Rect(
                cx - panel_width // 2,
                160,
                panel_width,
                panel_height
            )

            # тень
            shadow_rect = panel_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=16)

            # сама «кнопка»
            pygame.draw.rect(self.screen, base_color, panel_rect, border_radius=16)
            pygame.draw.rect(self.screen, border_color, panel_rect, 3, border_radius=16)

            # текст внутри панели
            y = panel_rect.top + 55
            title_rect = title.get_rect(center=(cx, y))
            self.screen.blit(title, title_rect)

            y += 50
            score_rect = score_text.get_rect(center=(cx, y))
            self.screen.blit(score_text, score_rect)

            y += 45
            reason_rect = reason_text.get_rect(center=(cx, y))
            self.screen.blit(reason_text, reason_rect)

            y += 40
            coins_rect = coins_text.get_rect(center=(cx, y))
            self.screen.blit(coins_text, coins_rect)

            y += 40
            instr_rect = instructions[index].get_rect(center=(cx, y))
            self.screen.blit(instructions[index], instr_rect)

            pygame.display.update()

        return 'menu'
