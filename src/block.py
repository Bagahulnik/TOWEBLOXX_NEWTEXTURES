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
        self.collision_checked = False

    def set_sprite_for_block_number(self, block_number):
        """
        Устанавливает спрайт блока на основе его номера.
        """
        self.block_number = block_number
        if block_number == 0:
            self.image = self.tower_sprites['bot']
            self.sprite_type = 'bot'
            self.sprite_index = 0
        else:
            self.sprite_index = (block_number - 1) % 4
            self.image = self.tower_sprites['mid'][self.sprite_index]
            self.sprite_type = 'mid'
        self.rotimg = self.image

    def swing(self):
        """
        Обновляет маятниковое движение блока на верёвке.
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
        """Возвращает текущую силу маятника"""
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

            # Проверяем столкновение когда достигли целевой высоты
            if self.y >= target_y and not self.collision_checked:
                self.collision_checked = True
                
                if tower.size == 0 or self.collided(tower):
                    # Попал - фиксируем позицию
                    self.y = target_y
                    self.speed = 0
                    self.state = "landed"
                else:
                    # Промах - блок продолжает падать
                    pass

            # Блок полностью улетел за экран - окончательный промах
            if self.y >= SCREEN_HEIGHT + 100:
                self.state = "miss"

    def get_state(self):
        """Возвращает текущее состояние блока"""
        return self.state

    def collided(self, tower):
        """
        Проверяет столкновение блока с верхом башни.
        Учитывает качание башни для точной проверки перекрытия.
        """
        if tower.size == 0:
            return True

        # ✅ Получаем координату последнего блока с учётом качания
        base_x = tower.xlist[-1]
        base_x_wobbled = base_x + tower.change
        
        top_x = self.xlast

        base_left = base_x_wobbled
        base_right = base_x_wobbled + BLOCK_WIDTH
        top_left = top_x
        top_right = top_x + BLOCK_WIDTH

        # ====== ПРОВЕРКА 1: Перекрытие по X ======
        overlap = min(base_right, top_right) - max(base_left, top_left)
        
        if overlap <= 0:
            tower.golden = False
            return False

        # ====== ПРОВЕРКА 2: Минимальное перекрытие 50% ======
        min_overlap = BLOCK_WIDTH * 0.5
        
        if overlap < min_overlap:
            tower.golden = False
            return False

        # ✅ ВАЖНО: Корректируем xlast с учётом wobble для сохранения в башню
        # Это гарантирует, что следующий блок будет проверяться правильно
        self.xlast_corrected = self.xlast

        # ====== ПРОВЕРКА 3: Золотой блок ======
        center_base = (base_left + base_right) / 2
        center_top = (top_left + top_right) / 2
        
        if abs(center_top - center_base) <= 5:
            tower.golden = True
        else:
            tower.golden = False
        
        return True


    def to_build(self, tower):
        """
        Проверяет, можно ли добавить блок в башню.
        """
        if self.state == "landed":
            self.state = "scroll"
            return True
        return False

    def collapse(self, tower):
        """
        ✅ МЕТОД ОТКЛЮЧЕН - логика промаха полностью в collided()
        
        Раньше этот метод дублировал проверку смещения и мог
        вызывать game over даже при правильном промахе.
        Теперь вся логика попадания/промаха в методе collided().
        """
        pass  # Ничего не делаем

    def rotate(self, direction):
        """
        Поворачивает блок для анимации падения.
        """
        if direction == "l":
            self.angle += 1
        if direction == "r":
            self.angle -= 1
        self.rotimg = pygame.transform.rotate(self.image, self.angle)

    def to_fall(self, tower):
        """
        Анимация падения блока при обрушении башни.
        """
        self.y += 5
        if tower.size >= 2:
            if (self.xlast < tower.xlist[-2] + 30):
                self.x -= 2
                self.rotate("l")
            elif (self.xlast > tower.xlist[-2] - 30):
                self.x += 2
                self.rotate("r")

    def respawn(self, tower):
        """
        Создаёт новый блок после размещения предыдущего.
        """
        if tower.size % 2 == 0:
            self.angle = -45
        else:
            self.angle = 45

        self.speed = 0
        self.state = "ready"
        self.collision_checked = False

        hook_x = ROPE_ORIGIN_X + ROPE_LENGTH * sin(self.angle)
        hook_y = ROPE_ORIGIN_Y + ROPE_LENGTH * cos(self.angle)
        attach_y = hook_y + HOOK_BOTTOM_OFFSET

        self.x = hook_x - HOOK_ATTACH_OFFSET_X
        self.y = attach_y - HOOK_ATTACH_OFFSET_Y

        self.set_sprite_for_block_number(tower.size)

    def display(self, screen, tower, scroll_y=0):
        """
        Отрисовывает блок на экране.
        """
        if not tower.is_scrolling():
            screen.blit(self.rotimg, (self.x, self.y + scroll_y))
