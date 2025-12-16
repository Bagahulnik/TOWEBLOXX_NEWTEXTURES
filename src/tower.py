import pygame

from src.constants import *


class Tower(pygame.sprite.Sprite):
    def __init__(self, tower_sprites):
        pygame.sprite.Sprite.__init__(self)

        self.tower_sprites = tower_sprites

        self.size = 0
        self.image = tower_sprites['mid'][0]
        self.rect = self.image.get_rect()

        self.xbase = 0
        self.y = SCREEN_HEIGHT
        self.x = 0

        self.height = 0

        self.xlist = []
        self.sprite_list = []
        self.golden_list = []

        self.onscreen = 0

        # смещение башни для качания
        self.change = 0
        self.speed = WOBBLE_SPEED
        self.wobbling = False

        self.scrolling = False
        self.golden = False
        self.redraw = False
        self.display_status = True
        self.collapse_reason = None

    def get_display(self):
        return self.display_status

    def is_scrolling(self):
        return self.scrolling

    def is_golden(self):
        return self.golden

    def get_top_y(self):
        return self.y

    def build(self, block):
        # увеличиваем размер
        self.size += 1
        self.onscreen = self.size

        if self.size == 1:
            self.xbase = block.xlast
            self.xlist = [self.xbase]
            self.sprite_list = [('bot', 0)]
            self.golden_list = [False]
        else:
            self.xlist.append(block.xlast)
            self.sprite_list.append((block.sprite_type, block.sprite_index))
            self.golden_list.append(self.golden)

        # высота и позиция от земли, БЕЗ потолка по верёвке
        self.height = self.size * BLOCK_HEIGHT
        base_y = SCREEN_HEIGHT - BLOCK_HEIGHT
        self.y = base_y - (self.height - BLOCK_HEIGHT)
        
        # ИСПРАВЛЕНИЕ: сбрасываем смещение качания при добавлении блока
        # чтобы избежать визуального дёргания
        self.change = 0


    def get_width(self):
        width = BLOCK_WIDTH
        if self.size <= 0:
            return width

        if self.xlist[-1] > self.xbase:
            width = (self.xlist[-1] - self.xbase) + BLOCK_WIDTH
        if self.xlist[-1] < self.xbase:
            width = -((self.xbase - self.xlist[-1]) + BLOCK_WIDTH)

        return width

    def draw(self):
        if self.size >= 1:
            surf = pygame.Surface((800, self.onscreen * BLOCK_HEIGHT), pygame.SRCALPHA)
            surf = surf.convert_alpha()

            buildlist = self.xlist
            spritelist = self.sprite_list

            for i in range(len(buildlist)):
                sprite_type, sprite_index = spritelist[i]
                if sprite_type == 'bot':
                    block_img = self.tower_sprites['bot']
                else:
                    block_img = self.tower_sprites['mid'][sprite_index]

                y_pos = self.onscreen * BLOCK_HEIGHT - BLOCK_HEIGHT * (i + 1)
                surf.blit(block_img, (buildlist[i], y_pos))
        else:
            surf = pygame.Surface((0, 0), pygame.SRCALPHA)

        self.rect = surf.get_rect()
        return surf

    def unbuild(self, block):
        self.display_status = False

        if self.y > block.y:
            block.y = self.y

        self.size -= 1

        surf = pygame.Surface((800, (self.onscreen - 1) * BLOCK_HEIGHT), pygame.SRCALPHA)
        surf = surf.convert_alpha()

        buildlist = self.xlist[-self.onscreen:-1]
        spritelist = self.sprite_list[-self.onscreen:-1]

        for i in range(len(buildlist)):
            sprite_type, sprite_index = spritelist[i]
            if sprite_type == 'bot':
                block_img = self.tower_sprites['bot']
            else:
                block_img = self.tower_sprites['mid'][sprite_index]

            y_pos = (self.onscreen - 1) * BLOCK_HEIGHT - BLOCK_HEIGHT * (i + 1)
            surf.blit(block_img, (buildlist[i], y_pos))

        self.rect = surf.get_rect()
        return surf

    def collapse(self, direction):
        # сейчас не используется, оставлен на будущее
        self.y += 5
        if direction == "l":
            self.x -= 5
        elif direction == "r":
            self.x += 5

    def wobble(self):
        """Качание башни вокруг текущего X.

        Амплитуда зависит от высоты башни и кривизны,
        а скорость качания растёт с количеством блоков.
        """
        width = self.get_width()

        # как только башня стала достаточно высокой, включаем качание навсегда
        if self.size >= 3:
            self.wobbling = True

        if self.wobbling:
            # -------- СКОРОСТЬ В ЗАВИСИМОСТИ ОТ ВЫСОТЫ --------
            base_speed = WOBBLE_SPEED

            extra_speed = 0.0
            if self.size > 15:
                extra_steps = (self.size - 15) // 10
                extra_speed = 0.1 * (1 + extra_steps)
            current_speed = base_speed + extra_speed

            # -------- АМПЛИТУДА КАЧАНИЯ --------
            base_limit = WOBBLE_LIMIT + self.size * WOBBLE_GROWTH_PER_BLOCK

            wobble_bonus = 0
            abs_width = abs(width)

            if abs_width > 120:
                norm = min((abs_width - 120) / 80, 1.0)
                wobble_bonus = base_limit * (0.3 + 0.4 * norm)

            dynamic_limit = base_limit + wobble_bonus
            if dynamic_limit > WOBBLE_MAX_LIMIT:
                dynamic_limit = WOBBLE_MAX_LIMIT

            # -------- ДВИЖЕНИЕ ТУДА-СЮДА --------
            self.change += self.speed

            if self.change > dynamic_limit:
                self.speed = -abs(current_speed)
            elif self.change < -dynamic_limit:
                self.speed = abs(current_speed)


    def display(self, screen, scroll_y=0):
        surf = self.draw()
        x = int(self.x + self.change)
        y = int(self.y + scroll_y)
        screen.blit(surf, (x, y))

    def scroll(self):
        self.scrolling = False

    def reset(self):
        self.redraw = True
        self.change = 0
        self.speed = WOBBLE_SPEED
        self.wobbling = False
