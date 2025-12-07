import math
import pygame
from pygame import mixer

from src.block import Block
from src.tower import Tower
from src.constants import *


class Game:
    def __init__(self, screen, save_manager, asset_loader):
        self.screen = screen
        self.save_manager = save_manager
        self.asset_loader = asset_loader

        self.crane_image = pygame.image.load(f"{ASSETS_PATH}crane.png").convert_alpha()
        self.rope_hook_image = pygame.image.load(f"{ASSETS_PATH}rope_with_hook.png").convert_alpha()

        # один высокий фон
        self.bg_big = pygame.image.load(f"{ASSETS_PATH}bg/bg_group.png").convert()
        self.bg_y = SCREEN_HEIGHT - self.bg_big.get_height()

        self.sounds = asset_loader.load_sounds()

        self.current_tower_id = save_manager.get_selected_tower()
        self.tower_sprites = asset_loader.load_tower_sprites(self.current_tower_id)

        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        self.score = 0
        self.misses = 0
        self.force = INITIAL_FORCE  # ← стартовая скорость
        self.coins_earned = 0

        # ---------- ПЛАВНАЯ АНИМАЦИЯ ФОНА ----------
        self.bg_anim_active = False
        self.bg_anim_progress = 0
        self.bg_anim_target_y = 0

        self.score_font = pygame.font.Font("freesansbold.ttf", 32)
        self.miss_font = pygame.font.Font("freesansbold.ttf", 24)
        self.over_font = pygame.font.Font("freesansbold.ttf", 64)
        self.mini_font = pygame.font.Font("freesansbold.ttf", 16)
        self.reason_font = pygame.font.Font("freesansbold.ttf", 24)
        self.coins_font = pygame.font.Font("freesansbold.ttf", 24)

        mixer.music.load(f"{ASSETS_PATH}bgm.wav")
        mixer.music.play(-1)

        self.BLINK_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BLINK_EVENT, 800)

        self.game_over = False
        self.game_over_reason = None

    # ---------- UI ----------

    def show_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        misses_text = self.miss_font.render(
            f"Промахи: {self.misses}/{MAX_MISSES}", True, BLACK
        )
        self.screen.blit(misses_text, (10, 50))

    # ---------- Фон ----------

    def draw_background(self):
        self.screen.blit(self.bg_big, (0, self.bg_y))

    # ---------- Рисование ----------

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

    # ---------- События ----------

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.block.get_state() == "ready":
                    self.block.drop(self.tower)

    # ---------- Логика ----------

    def update(self):
        state = self.block.get_state()

        # ← ПЕРЕДАЁМ ТЕКУЩУЮ СКОРОСТЬ В БЛОК ПЕРЕД swing()
        if state == "ready":
            self.block.game_force = self.force  # ← передаём ускоренную силу
            self.block.swing()

        elif state == "dropped":
            self.block.drop(self.tower)

        elif state == "landed":
            if self.block.to_build(self.tower):
                self.tower.build(self.block)

                # ← ПОСТЕПЕННОЕ УСКОРЕНИЕ СКОРОСТИ КАЧАНИЯ
                self.force *= 1.015  # +1.5% скорости за каждый блок

                if self.tower.is_golden():
                    self.sounds['gold'].play()
                    self.score += 2
                    self.save_manager.add_coins(10)
                    self.coins_earned += 10
                else:
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
            self.sounds['fall'].play()

            if self.misses >= MAX_MISSES:
                self.game_over_reason = "misses"
                self.end_game()
            else:
                self.block.respawn(self.tower)

        # ---------- ПЛАВНАЯ АНИМАЦИЯ ТОЛЬКО ФОНА ----------
        if self.bg_anim_active:
            self.bg_anim_progress += 1
            progress_ratio = self.bg_anim_progress / BG_SCROLL_DURATION
            
            # двигаем ТОЛЬКО фон плавно
            self.bg_y = self.bg_anim_target_y * progress_ratio + self.bg_y * (1 - progress_ratio)
            
            if self.bg_anim_progress >= BG_SCROLL_DURATION:
                # анимация завершена
                self.bg_y = self.bg_anim_target_y
                self.bg_anim_active = False
                self.bg_anim_progress = 0
        else:
            # проверяем триггер запуска анимации
            if self.tower.size >= TOWER_BLOCKS_PER_STEP:
                # 1) МОМЕНТАЛЬНО обрезаем башню
                self.tower.size = BASE_ONSCREEN_BLOCKS
                self.tower.onscreen = self.tower.size
                self.tower.height = self.tower.size * BLOCK_HEIGHT
                base_y = SCREEN_HEIGHT - BLOCK_HEIGHT
                self.tower.y = base_y - (self.tower.height - BLOCK_HEIGHT)
                self.tower.xlist = self.tower.xlist[-self.tower.size:]
                self.tower.sprite_list = self.tower.sprite_list[-self.tower.size:]
                self.tower.golden_list = self.tower.golden_list[-self.tower.size:]
                
                # 2) запускаем плавную анимацию ТОЛЬКО фона
                self.bg_anim_active = True
                self.bg_anim_progress = 0
                self.bg_anim_target_y = self.bg_y + BG_SCROLL_STEP
                
                # ограничиваем нижний край
                min_bg_y = SCREEN_HEIGHT - self.bg_big.get_height()
                if self.bg_anim_target_y < min_bg_y:
                    self.bg_anim_target_y = min_bg_y

        self.check_game_over()

    # ---------- Конец игры ----------

    def check_game_over(self):
        width = self.tower.get_width()

        if width < -140:
            self.tower.collapse("l")
            if not self.game_over_reason:
                self.sounds['over'].play()
                self.game_over_reason = "collapse"
                self.end_game()
        elif width > 140:
            self.tower.collapse("r")
            if not self.game_over_reason:
                self.sounds['over'].play()
                self.game_over_reason = "collapse"
                self.end_game()

    def end_game(self):
        self.game_over = True
        self.save_manager.update_high_score(self.score)

    def reset(self):
        self.current_tower_id = self.save_manager.get_selected_tower()
        self.tower_sprites = self.asset_loader.load_tower_sprites(self.current_tower_id)

        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        self.misses = 0
        self.score = 0

        # сбрасываем фон, анимацию и СКОРОСТЬ
        self.bg_y = SCREEN_HEIGHT - self.bg_big.get_height()
        self.bg_anim_active = False
        self.bg_anim_progress = 0
        self.force = INITIAL_FORCE  # ← сбрасываем скорость до начальной

        self.game_over = False
        self.game_over_reason = None
        self.coins_earned = 0

    def show_game_over_screen(self):
        over_text = self.over_font.render("GAME OVER", True, BLACK)
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
        blank = pygame.Surface((blank_rect.size), pygame.SRCALPHA)
        blank = blank.convert_alpha()

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

            self.screen.blit(self.bg_big, (0, self.bg_y))

            cx = SCREEN_WIDTH // 2

            over_rect = over_text.get_rect(center=(cx, 140))
            self.screen.blit(over_text, over_rect)

            score_rect = score_text.get_rect(center=(cx, 210))
            self.screen.blit(score_text, score_rect)

            reason_rect = reason_text.get_rect(center=(cx, 260))
            self.screen.blit(reason_text, reason_rect)

            coins_rect = coins_text.get_rect(center=(cx, 305))
            self.screen.blit(coins_text, coins_rect)

            instr_rect = instructions[index].get_rect(center=(cx, 360))
            self.screen.blit(instructions[index], instr_rect)

            pygame.display.update()

        return 'menu'
