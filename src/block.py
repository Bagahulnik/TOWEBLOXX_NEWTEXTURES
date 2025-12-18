"""
Модуль block.py - класс падающего блока
Управляет физикой блока: маятниковое качание, падение, столкновения.
Проверяет точность попадания и определяет золотые блоки.
"""
import pygame
from math import sin, cos
from src.constants import *

class Block(pygame.sprite.Sprite):
    """
    Класс блока, который игрок сбрасывает на башню.
    Реализует маятниковое движение, свободное падение и проверку коллизий.
    """
    def __init__(self, tower_sprites, origin=(ROPE_ORIGIN_X, ROPE_ORIGIN_Y), block_number=0):
        pygame.sprite.Sprite.__init__(self)
        self.tower_sprites = tower_sprites
        self.origin = origin
        self.block_number = block_number
        self.game_force = INITIAL_FORCE

        # выбор спрайта
        if block_number == 0:
            self.image = tower_sprites['bot']
            self.sprite_type = 'bot'
            self.sprite_index = 0
        else:
            # Циклически используем 4 спрайта: 0, 1, 2, 3, 0, 1, 2, 3...
            self.sprite_index = (block_number - 1) % 4
            self.image = tower_sprites['mid'][self.sprite_index]
            self.sprite_type = 'mid'

        self.rotimg = self.image

        # стартовые координаты блока
        self.x = ROPE_ORIGIN_X - BLOCK_WIDTH // 2
        self.y = ROPE_ORIGIN_Y + ROPE_LENGTH
        self.xlast = 0
        self.xchange = 100
        self.speed = 0
        self.acceleration = 0
        self.speedmultiplier = 1
        self.rect = self.image.get_rect()

        self.state = "ready"
        self.angle = 45
        self.collision_checked = False  # флаг проверки столкновения

    def set_sprite_for_block_number(self, block_number):
        """
        Устанавливает спрайт блока на основе его номера.
        Используется при создании нового блока после размещения предыдущего.
        """
        self.block_number = block_number
        if block_number == 0:
            self.image = self.tower_sprites['bot']
            self.sprite_type = 'bot'
            self.sprite_index = 0
        else:
            # Циклически все 4 варианта mid
            self.sprite_index = (block_number - 1) % 4
            self.image = self.tower_sprites['mid'][self.sprite_index]
            self.sprite_type = 'mid'
        self.rotimg = self.image

    def swing(self):
        """
        Обновляет маятниковое движение блока на верёвке.
        Использует физическую модель маятника с синусоидальным ускорением.
        """
        hook_x = ROPE_ORIGIN_X + ROPE_LENGTH * sin(self.angle)
        hook_y = ROPE_ORIGIN_Y + ROPE_LENGTH * cos(self.angle)

        if self.state == "ready":
            attach_y = hook_y + HOOK_BOTTOM_OFFSET
            self.x = hook_x - HOOK_ATTACH_OFFSET_X
            self.y = attach_y - HOOK_ATTACH_OFFSET_Y

        self.angle += self.speed
        self.acceleration = sin(self.angle) * self.get_force()
        self.speed += self.acceleration

    def get_force(self):
        """Возвращает текущую силу маятника, которая растёт с прогрессом игры"""
        return self.game_force

    def drop(self, tower):
        """
        Обрабатывает падение блока после сброса.
        Применяет гравитацию и проверяет столкновение с башней.
        """
        if self.state == "ready":
            self.state = "dropped"
            self.xlast = self.x
            self.speed = 0

        if self.state == "dropped":
            self.speed += GRAVITY
            self.y += self.speed

            if tower.size == 0:
                target_y = SCREEN_HEIGHT - 424
            else:
                target_y = tower.y - BLOCK_HEIGHT

            # Проверяем столкновение когда достигли или прошли target_y
            if self.y >= target_y and not self.collision_checked:
                self.collision_checked = True
                
                if tower.size == 0 or self.collided(tower):
                    # Попал - фиксируем Y точно на уровне башни
                    self.y = target_y
                    self.speed = 0
                    self.state = "landed"
                else:
                    # Промах - продолжаем падать
                    pass

            # Окончательно переходим в miss только внизу экрана
            if self.y >= SCREEN_HEIGHT + 100:
                self.state = "miss"


    def get_state(self):
        """Возвращает текущее состояние блока"""
        return self.state

    def collided(self, tower):
        """
        Проверяет столкновение блока с верхом башни.
        Определяет:
        1. Есть ли достаточное перекрытие по X (минимум 50%)
        2. Не слишком ли большое смещение относительно предыдущего блока
        3. Является ли попадание идеальным (золотым)
        
        Возвращает True при успешном попадании, False при промахе.
        """
        # Для первого блока всегда успех

        if tower.size == 0:
            return False

        base_x = tower.xlist[-1]
        top_x = self.xlast

        base_left = base_x
        base_right = base_x + BLOCK_WIDTH
        top_left = top_x
        top_right = top_x + BLOCK_WIDTH

        # длина перекрытия по X
        overlap = min(base_right, top_right) - max(base_left, top_left)

        # Нет пересечения - промах
        if overlap <= 0:
            tower.golden = False
            return False

        # проверяем смещение относительно ПРЕДЫДУЩЕГО блока
        if tower.size >= 2:
            prev_x = tower.xlist[-2]
        else:
            prev_x = tower.xbase
        
        offset = abs(self.xlast - prev_x)
        max_offset = BLOCK_WIDTH * 0.5
        
        # если смещение слишком большое - промах
        if offset >= max_offset:
            tower.golden = False
            return False

        # проверяем перекрытие хотя бы 50%
        if overlap >= BLOCK_WIDTH * 0.5:
            center_base = (base_left + base_right) / 2
            center_top = (top_left + top_right) / 2
            if abs(center_top - center_base) <= 5:
                tower.golden = True
            else:
                tower.golden = False
            return True
        else:
            tower.golden = False
            return False

    def to_build(self, tower):
        """
        Проверяет, можно ли добавить блок в башню.
        Возвращает True только если блок успешно приземлился.
        """
        if self.state == "landed":
            self.state = "scroll"
            return True
        return False

    def collapse(self, tower):
        """
        Проверяет условия обрушения башни на основе смещения блока.
        Устанавливает состояние "over" если смещение слишком велико.
        """
        if tower.size < 2:
            return
        if tower.size == 2:
            prev_x = tower.xbase
            threshold = BLOCK_WIDTH * 0.5
        else:
            prev_x = tower.xlist[-2]
            threshold = BLOCK_WIDTH * 0.5

        offset = abs(self.xlast - prev_x)
        if offset >= threshold:
            self.state = "over"
            tower.collapse_reason = "offset"

    def rotate(self, direction):
        """
        Поворачивает блок для анимации падения при обрушении.
        direction: "l" (влево) или "r" (вправо)
        """
        if direction == "l":
            self.angle += 1
        if direction == "r":
            self.angle -= 1
        self.rotimg = pygame.transform.rotate(self.image, self.angle)

    def to_fall(self, tower):
        """
        Анимация падения блока при обрушении башни.
        Блок падает и вращается в зависимости от направления смещения.
        """
        self.y += 5
        if (self.xlast < tower.xlist[-2] + 30):
            self.x -= 2
            self.rotate("l")
        elif (self.xlast > tower.xlist[-2] - 30):
            self.x += 2
            self.rotate("r")

    def respawn(self, tower):
        """
        Создаёт новый блок после размещения предыдущего.
        Сбрасывает все параметры и устанавливает начальное положение маятника.
        """
        if tower.size % 2 == 0:
            self.angle = -45
        else:
            self.angle = 45

        self.speed = 0
        self.state = "ready"
        self.collision_checked = False  # сбрасываем флаг

        hook_x = ROPE_ORIGIN_X + ROPE_LENGTH * sin(self.angle)
        hook_y = ROPE_ORIGIN_Y + ROPE_LENGTH * cos(self.angle)
        attach_y = hook_y + HOOK_BOTTOM_OFFSET

        self.x = hook_x - HOOK_ATTACH_OFFSET_X
        self.y = attach_y - HOOK_ATTACH_OFFSET_Y

        self.set_sprite_for_block_number(tower.size)

    def display(self, screen, tower, scroll_y=0):
        """
        Отрисовывает блок на экране.
        scroll_y используется для прокрутки при росте башни.
        """
        if not tower.is_scrolling():
            screen.blit(self.rotimg, (self.x, self.y + scroll_y))
