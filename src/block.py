import pygame
from math import sin, cos
from src.constants import *


class Block(pygame.sprite.Sprite):
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

    def set_sprite_for_block_number(self, block_number):
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
        return self.game_force

    def drop(self, tower):
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

            if self.y >= target_y:
                if tower.size == 0 or self.collided(tower):
                    self.state = "landed"
                else:
                    if self.y >= SCREEN_HEIGHT + 100:
                        self.state = "miss"

    def get_state(self):
        return self.state

    def collided(self, tower):
        if tower.size == 0:
            return False

        half = BLOCK_WIDTH * 0.5
        x_ok = (self.xlast < tower.xlist[-1] + half) and \
               (self.xlast > tower.xlist[-1] - half)

        y_ok = (tower.y - self.y <= BLOCK_HEIGHT + 10)

        if x_ok and y_ok:
            if (self.xlast < tower.xlist[-1] + 5) and \
               (self.xlast > tower.xlist[-1] - 5):
                tower.golden = True
            else:
                tower.golden = False
            return True
        else:
            tower.golden = False
            return False

    def to_build(self, tower):
        self.state = "scroll"
        if tower.size == 0 or self.collided(tower):
            return True
        return False

    def collapse(self, tower):
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
        if direction == "l":
            self.angle += 1
        if direction == "r":
            self.angle -= 1
        self.rotimg = pygame.transform.rotate(self.image, self.angle)

    def to_fall(self, tower):
        self.y += 5
        if (self.xlast < tower.xlist[-2] + 30):
            self.x -= 2
            self.rotate("l")
        elif (self.xlast > tower.xlist[-2] - 30):
            self.x += 2
            self.rotate("r")

    def respawn(self, tower):
        if tower.size % 2 == 0:
            self.angle = -45
        else:
            self.angle = 45

        self.speed = 0
        self.state = "ready"

        hook_x = ROPE_ORIGIN_X + ROPE_LENGTH * sin(self.angle)
        hook_y = ROPE_ORIGIN_Y + ROPE_LENGTH * cos(self.angle)
        attach_y = hook_y + HOOK_BOTTOM_OFFSET

        self.x = hook_x - HOOK_ATTACH_OFFSET_X
        self.y = attach_y - HOOK_ATTACH_OFFSET_Y

        self.set_sprite_for_block_number(tower.size)

    def display(self, screen, tower, scroll_y=0):
        if not tower.is_scrolling():
            screen.blit(self.rotimg, (self.x, self.y + scroll_y))
