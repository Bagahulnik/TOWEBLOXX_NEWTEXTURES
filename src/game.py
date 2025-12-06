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

        # Загрузка ресурсов
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
        self.misses = 0          # количество промахов
        self.screen_y = 0
        self.screen_x = 0
        self.force = INITIAL_FORCE

        # Шрифты
        self.score_font = pygame.font.Font("freesansbold.ttf", 32)
        self.miss_font = pygame.font.Font("freesansbold.ttf", 24)
        self.over_font = pygame.font.Font("freesansbold.ttf", 64)
        self.mini_font = pygame.font.Font("freesansbold.ttf", 16)

        # Музыка
        mixer.music.load(f"{ASSETS_PATH}bgm.wav")
        mixer.music.play(-1)

        # События
        self.BLINK_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BLINK_EVENT, 800)

        self.game_over = False
        self.game_over_reason = None   # "misses" или "collapse"

    # ----------------- Рисование -----------------

    def show_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        misses_text = self.miss_font.render(
            f"Промахи: {self.misses}/{MAX_MISSES}", True, BLACK
        )
        self.screen.blit(misses_text, (10, 50))

    def draw_background(self):
        if self.screen_y < 1200:
            self.screen.blit(self.backgrounds[1], (self.screen_x, self.screen_y - 600))
            self.screen.blit(self.backgrounds[0], (self.screen_x, self.screen_y))
            self.screen.blit(self.backgrounds[1], (self.screen_x, self.screen_y - 1200))
        else:
            self.screen.blit(self.backgrounds[1], (self.screen_x, self.screen_y - 1800))
            self.screen.blit(self.backgrounds[1], (self.screen_x, self.screen_y - 1200))
            if self.screen_y % 600 == 0:
                self.screen_y = 1200

    def draw(self):
        self.draw_background()
        self.show_score()

        self.tower.wobble()
        if self.tower.get_display():
            self.tower.display(self.screen)

        self.block.display(self.screen, self.tower)

    # ----------------- События -----------------

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.block.get_state() == "ready":
                    self.block.drop(self.tower)

    # ----------------- Логика игры -----------------

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
                else:
                    self.sounds['build'].play()
                    self.score += 1

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
            # ПРОМАХ: башню не трогаем
            self.misses += 1
            self.sounds['fall'].play()

            if self.misses >= MAX_MISSES:
                self.game_over_reason = "misses"
                self.end_game()
            else:
                # Новый блок, башня остаётся как есть
                self.block.respawn(self.tower)

        # Прокрутка экрана
        if self.tower.height >= BLOCK_HEIGHT * 5 and self.tower.size >= 5:
            self.tower.scroll()
            self.screen_y += 5

        # Проверка конца игры только для падения башни / блока
        self.check_game_over()

    def check_game_over(self):
        width = self.tower.get_width()

        # Обрушение от слишком большого смещения всей башни
        if width < -140:
            self.tower.collapse("l")
            self.sounds['over'].play()
            self.game_over_reason = "collapse"
        elif width > 140:
            self.tower.collapse("r")
            self.sounds['over'].play()
            self.game_over_reason = "collapse"

        # Башня ушла за низ экрана
        if self.tower.y > 600:
            self.block.x = 2000
            self.tower.size -= 1
            if not self.game_over_reason:
                self.game_over_reason = "collapse"
            self.end_game()

        # Блок после обрушения упал за экран
        elif self.block.get_state() == "over" and self.block.y > 600:
            self.tower.y = 2000
            self.tower.size -= 1
            if not self.game_over_reason:
                self.game_over_reason = "collapse"
            self.end_game()

        # ВАЖНО: здесь НЕТ обработки state == "miss"

    # ----------------- Конец игры -----------------

    def end_game(self):
        self.game_over = True
        coins_earned = self.score // 10
        self.save_manager.add_coins(coins_earned)
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

    def show_game_over_screen(self):
        over_text = self.over_font.render("GAME OVER", True, BLACK)
        score_text = self.score_font.render(f"SCORE: {self.score}", True, BLACK)

        if self.game_over_reason == "misses":
            reason_text = self.mini_font.render(
                f"Слишком много промахов ({MAX_MISSES})", True, (200, 0, 0)
            )
        else:
            reason_text = self.mini_font.render("Башня обрушилась", True, (200, 0, 0))

        coins_text = self.mini_font.render(f"+{self.score // 10} монет", True, BLACK)
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
            self.screen.blit(over_text, (200, 120))
            self.screen.blit(score_text, (280, 220))
            self.screen.blit(reason_text, (220, 270))
            self.screen.blit(coins_text, (320, 320))
            self.screen.blit(instructions[index], (250, 450))
            pygame.display.update()

        return 'menu'
