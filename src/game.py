import pygame
import math
from pygame import mixer
from src.block import Block
from src.tower import Tower
from src.constants import *


class Game:
    def __init__(self, screen, save_manager, asset_loader):
        self.screen = screen
        self.save_manager = save_manager
        self.asset_loader = asset_loader

        # Кран и верёвка
        self.crane_image = pygame.image.load(f"{ASSETS_PATH}crane.png").convert_alpha()
        self.rope_image = pygame.image.load(f"{ASSETS_PATH}crane_rope.png").convert_alpha()
        self.hook_image = pygame.image.load(f"{ASSETS_PATH}hook.png").convert_alpha()
        self.rope_rect = self.rope_image.get_rect()

        # Ресурсы
        self.backgrounds = asset_loader.load_backgrounds()
        self.sounds = asset_loader.load_sounds()

        # Текущая башня
        self.current_tower_id = save_manager.get_selected_tower()
        self.tower_sprites = asset_loader.load_tower_sprites(self.current_tower_id)

        # Игровые объекты
        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        # Состояние игры
        self.score = 0
        self.misses = 0
        self.screen_y = 0
        self.screen_x = 0
        self.force = INITIAL_FORCE
        self.coins_earned = 0

        # Шрифты
        self.score_font = pygame.font.Font("freesansbold.ttf", 32)
        self.miss_font = pygame.font.Font("freesansbold.ttf", 24)
        self.over_font = pygame.font.Font("freesansbold.ttf", 64)
        self.mini_font = pygame.font.Font("freesansbold.ttf", 16)
        self.reason_font = pygame.font.Font("freesansbold.ttf", 24)
        self.coins_font = pygame.font.Font("freesansbold.ttf", 24)

        # Музыка
        mixer.music.load(f"{ASSETS_PATH}bgm.wav")
        mixer.music.play(-1)

        # События
        self.BLINK_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BLINK_EVENT, 800)

        self.game_over = False
        self.game_over_reason = None

    # -------- Рисование --------

    def show_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        misses_text = self.miss_font.render(
            f"Промахи: {self.misses}/{MAX_MISSES}", True, BLACK
        )
        self.screen.blit(misses_text, (10, 50))

    def draw_background(self):
        total_height = len(self.backgrounds) * SCREEN_HEIGHT
        offset = self.screen_y % total_height

        start_index = int(offset // SCREEN_HEIGHT)
        y_in_texture = offset % SCREEN_HEIGHT

        for i in range(3):
            idx = (start_index + i) % len(self.backgrounds)
            y = -y_in_texture + i * SCREEN_HEIGHT
            self.screen.blit(self.backgrounds[idx], (0, y))

    def draw(self):
        self.draw_background()
        self.screen.blit(self.crane_image, (0, 0))

        # ----- верёвка как спрайт поверх старой математики -----
        origin = (CRANE_ANCHOR_X, CRANE_ANCHOR_Y)

       # верёвка-спрайт
        angle_deg = -self.block.angle
        rot_rope = pygame.transform.rotate(self.rope_image, angle_deg)
        rope_rect = rot_rope.get_rect()
        rope_rect.midtop = (ROPE_ORIGIN_X, ROPE_ORIGIN_Y)
        self.screen.blit(rot_rope, rope_rect)

        # конец верёвки (крюк)
        hook_x = ROPE_ORIGIN_X + ROPE_LENGTH * math.sin(self.block.angle)
        hook_y = ROPE_ORIGIN_Y + ROPE_LENGTH * math.cos(self.block.angle)

        hook_rect = self.hook_image.get_rect()
        ANCHOR_IN_HOOK_X = hook_rect.width // 2   # центр по X
        ANCHOR_IN_HOOK_Y = 10  # подбери по Y под свой спрайт
        hook_rect.topleft = (
            hook_x - ANCHOR_IN_HOOK_X,
            hook_y - ANCHOR_IN_HOOK_Y,
        )
        self.screen.blit(self.hook_image, hook_rect)
        self.show_score()
        self.tower.wobble()
        if self.tower.get_display():
            self.tower.display(self.screen)
        self.block.display(self.screen, self.tower)
        self.screen.blit(self.hook_image, hook_rect)

    # -------- События --------

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.block.get_state() == "ready":
                    self.block.drop(self.tower)

    # -------- Логика --------

    def update(self):
        state = self.block.get_state()

        if state == "ready":
            self.block.swing()
        elif state == "dropped":
            self.block.drop(self.tower)
        elif state == "landed":
            if self.block.to_build(self.tower):
                self.tower.build(self.block)

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
            self.sounds['fall'].play()
            self.sounds['over'].play()

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

        if self.tower.height >= BLOCK_HEIGHT * 5 and self.tower.size >= 5:
            self.tower.scroll()
            self.screen_y += 5

        self.check_game_over()

    def check_game_over(self):
        width = self.tower.get_width()

        if width < -140:
            self.tower.collapse("l")
            self.sounds['over'].play()
            self.game_over_reason = "collapse"
        elif width > 140:
            self.tower.collapse("r")
            self.sounds['over'].play()
            self.game_over_reason = "collapse"

        if self.tower.y > SCREEN_HEIGHT:
            self.block.x = 2000
            self.tower.size -= 1
            if not self.game_over_reason:
                self.game_over_reason = "collapse"
            self.end_game()

        elif self.block.get_state() == "over" and self.block.y > SCREEN_HEIGHT:
            self.tower.y = 2000
            self.tower.size -= 1
            if not self.game_over_reason:
                self.game_over_reason = "collapse"
            self.end_game()

    # -------- Конец игры --------

    def end_game(self):
        self.game_over = True
        self.save_manager.update_high_score(self.score)

    def reset(self):
        self.current_tower_id = self.save_manager.get_selected_tower()
        self.tower_sprites = self.asset_loader.load_tower_sprites(self.current_tower_id)

        self.block = Block(self.tower_sprites, block_number=0)
        self.tower = Tower(self.tower_sprites)

        self.score = 0
        self.misses = 0
        self.screen_y = 0
        self.force = INITIAL_FORCE
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
        blank.convert_alpha()

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

            self.screen.blit(self.backgrounds[0], (0, 0))

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
