import pygame
from math import sin, cos
from src.constants import *


class Block(pygame.sprite.Sprite):
    def __init__(self, tower_sprites, origin=(400, 3), block_number=0):
        pygame.sprite.Sprite.__init__(self)
        self.tower_sprites = tower_sprites
        self.origin = origin
        self.block_number = block_number  # Номер блока для определения спрайта
        
        # Загрузка спрайта
        if block_number == 0:
            # Первый блок всегда bot
            self.image = tower_sprites['bot']
            self.sprite_type = 'bot'
            self.sprite_index = 0
        else:
            # Последующие блоки - mid от 0 до 3 по кругу
            self.sprite_index = (block_number - 1) % 4
            self.image = tower_sprites['mid'][self.sprite_index]
            self.sprite_type = 'mid'
        
        self.rotimg = self.image
        
        self.x = 37
        self.y = 150
        self.xlast = 0
        self.xchange = 100
        self.speed = 0
        self.acceleration = 0
        self.speedmultiplier = 1
        self.rect = self.image.get_rect()
        
        # Состояния: ready, dropped, landed, scroll, over
        self.state = "ready"
        self.angle = 45
    
    def set_sprite_for_block_number(self, block_number):
        """Устанавливает спрайт в зависимости от номера блока"""
        self.block_number = block_number
        
        if block_number == 0:
            # Первый блок всегда bot
            self.image = self.tower_sprites['bot']
            self.sprite_type = 'bot'
            self.sprite_index = 0
        else:
            # Последующие блоки - mid от 0 до 3 по кругу
            self.sprite_index = (block_number - 1) % 4
            self.image = self.tower_sprites['mid'][self.sprite_index]
            self.sprite_type = 'mid'
        
        self.rotimg = self.image
    
    def swing(self):
        """Качание блока на веревке"""
        self.x = 370 + ROPE_LENGTH * sin(self.angle)
        self.y = 20 + ROPE_LENGTH * cos(self.angle)
        self.angle += self.speed
        self.acceleration = sin(self.angle) * self.get_force()
        self.speed += self.acceleration
    
    def get_force(self):
        """Получить текущую силу (увеличивается со временем)"""
        return INITIAL_FORCE
    
    def drop(self, tower):
        """Падение блока"""
        if self.state == "ready":
            self.state = "dropped"
            self.xlast = self.x
        
        if self.collided(tower):
            self.state = "landed"
        
        if tower.size == 0 and self.y >= 536:
            self.state = "landed"
        
        if tower.size >= 1 and self.y >= 536 and not self.collided(tower):
            self.state = "miss"
        
        if self.state == "dropped":
            self.speed += GRAVITY
            self.y += self.speed
    
    def get_state(self):
        return self.state
    
    def collided(self, tower):
        """Проверка столкновения с башней"""
        if tower.size == 0:
            return False
        
        if (self.xlast < tower.xlist[-1] + 90) and \
           (self.xlast > tower.xlist[-1] - 90) and \
           (tower.y - self.y <= 55):
            
            if (self.xlast < tower.xlist[-1] + 5) and \
               (self.xlast > tower.xlist[-1] - 5):
                tower.golden = True
            else:
                tower.golden = False
            return True
        else:
            return False
    
    def to_build(self, tower):
        """Проверка возможности постройки"""
        self.state = "scroll"
        if tower.size == 0 or self.collided(tower):
            return True
        return False
    
    def collapse(self, tower):
        """Проверка обрушения башни из-за смещения"""
        if tower.size < 2:
            return
    
        # Вычисляем смещение текущего блока относительно предыдущего
        offset = abs(self.xlast - tower.xlist[-2])
    
        # Если смещение больше 50% ширины блока - башня рушится
        if offset > BLOCK_WIDTH * COLLAPSE_THRESHOLD:
            if self.collided(tower):
                self.state = "over"
                tower.collapse_reason = "offset"  # Причина: смещение
    
    def rotate(self, direction):
        """Вращение блока"""
        if direction == "l":
            self.angle += 1 % 360
        if direction == "r":
            self.angle -= 1 % 360
        self.rotimg = pygame.transform.rotate(self.image, self.angle)
    
    def to_fall(self, tower):
        """Падение блока после промаха"""
        self.y += 5
        
        if (self.xlast < tower.xlist[-2] + 30):
            self.x -= 2
            self.rotate("l")
        elif (self.xlast > tower.xlist[-2] - 30):
            self.x += 2
            self.rotate("r")
    
    def display(self, screen, tower):
        """Отображение блока"""
        if not tower.is_scrolling():
            pygame.draw.circle(screen, RED, self.origin, 5, 0)
            screen.blit(self.rotimg, (self.x, self.y))
            if self.state == "ready":
                self.draw_rope(screen)
    
    def draw_rope(self, screen):
        """Отрисовка веревки"""
        for offset in [0, 1, 2, -1, -2]:
            pygame.draw.aaline(screen, BLACK, 
                             (self.origin[0] + offset, self.origin[1]), 
                             (self.x + 48 + offset, self.y))  # 48 = BLOCK_WIDTH/2
        pygame.draw.circle(screen, RED, 
                         (int(self.x + 48), int(self.y + 2.5)), 5, 0)
    
    def respawn(self, tower):
        """Возрождение блока"""
        if tower.size % 2 == 0:
            self.angle = -45
        else:
            self.angle = 45
        
        self.y = 150
        self.x = 370
        self.speed = 0
        self.state = "ready"
        
        # Установить спрайт для следующего блока
        self.set_sprite_for_block_number(tower.size)
