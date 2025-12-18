"""
Модуль tower.py - класс построенной башни
Управляет структурой башни, её отрисовкой, качанием и прокруткой.
Хранит информацию о всех размещённых блоках и их координатах.
"""
import pygame

from src.constants import *


class Tower(pygame.sprite.Sprite):
    """
    Класс башни - основная конструкция, которую строит игрок.
    Отвечает за хранение блоков, динамическое качание и визуализацию.
    """
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
        # Списки для хранения данных о каждом блоке
        self.xlist = [] # Горизонтальные координаты всех блоков
        self.sprite_list = [] # Типы и индексы спрайтов блоков
        self.golden_list = [] # Флаги золотых блоков (идеальные попадания)

        self.onscreen = 0

        # Динамическое качание делает игру сложнее с ростом высоты
        self.change = 0  # Текущее смещение от центра (в пикселях)
        self.speed = WOBBLE_SPEED # Скорость качания
        self.wobbling = False # Флаг активности качания

        self.scrolling = False
        self.golden = False
        self.redraw = False
        self.display_status = True
        self.collapse_reason = None

    def get_display(self):
        """Возвращает статус отображения башни"""
        return self.display_status

    def is_scrolling(self):
        return self.scrolling

    def is_golden(self):
        return self.golden

    def get_top_y(self):
        """Возвращает Y координату верха башни"""
        return self.y

    def build(self, block):
        """
        Добавляет новый блок в башню после успешного приземления.
        Обновляет размер, высоту и списки координат/спрайтов.
        """
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

        # Пересчитываем высоту и Y координату башни
        self.height = self.size * BLOCK_HEIGHT
        base_y = SCREEN_HEIGHT - BLOCK_HEIGHT
        self.y = base_y - (self.height - BLOCK_HEIGHT)
        
        # ИСПРАВЛЕНИЕ: сбрасываем смещение качания при добавлении блока
        # чтобы избежать визуального дёргания
        self.change = 0


    def get_width(self):
        """
        Вычисляет общую ширину башни.
        Положительная если башня наклонена вправо, отрицательная влево.
        """
        width = BLOCK_WIDTH
        if self.size <= 0:
            return width

        if self.xlist[-1] > self.xbase:
            width = (self.xlist[-1] - self.xbase) + BLOCK_WIDTH
        if self.xlist[-1] < self.xbase:
            width = -((self.xbase - self.xlist[-1]) + BLOCK_WIDTH)

        return width

    def draw(self):
        """
        Создаёт поверхность с отрисованной башней.
        Рисует все блоки снизу вверх с правильными спрайтами.
        Возвращает готовую поверхность для отображения.
        """
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
        """
        Удаляет верхний блок из башни при промахе.
        Используется для анимации разрушения или падения блока.
        """
        self.display_status = False
        # Синхронизируем позицию блока с верхом башни
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
        """
        Анимация разрушения башни (сдвиг и падение).
        Сейчас не используется в игре.
        """
        self.y += 5
        if direction == "l":
            self.x -= 5
        elif direction == "r":
            self.x += 5

    def wobble(self):
        """
        Обновляет качание башни вокруг центральной оси.
        
        Логика качания:
        - Амплитуда растёт с высотой башни и её кривизной
        - Скорость качания увеличивается после 15 блоков
        - Качание активируется при достижении 3 блоков
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
        """
        Отображает башню на экране с учётом качания и прокрутки.
        scroll_y используется для плавной прокрутки при росте башни.
        """
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
