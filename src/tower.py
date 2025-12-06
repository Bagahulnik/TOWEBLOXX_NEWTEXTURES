import pygame
from src.constants import *


class Tower(pygame.sprite.Sprite):
    def __init__(self, tower_sprites):
        pygame.sprite.Sprite.__init__(self)
        self.tower_sprites = tower_sprites
        self.size = 0
    
        # Спрайты
        self.image = tower_sprites['mid'][0]
        self.image_gold = tower_sprites['gold']
    
        self.rect = self.image.get_rect()
        self.xbase = 0
        self.y = 600
        self.x = 0
        self.height = 0
        self.xlist = []
        self.sprite_list = []
        self.onscreen = 0
        self.change = 0
        self.speed = WOBBLE_SPEED
        self.wobbling = False
        self.scrolling = False
        self.golden = False
        self.redraw = False
        self.display_status = True
        self.collapse_reason = None  # Причина обрушения: "offset", "width"
    
    def get_display(self):
        return self.display_status
    
    def is_scrolling(self):
        return self.scrolling
    
    def is_golden(self):
        return self.golden
    
    def build(self, block):
        """Добавить блок к башне"""
        self.size += 1
        self.onscreen += 1
        
        if self.size == 1:
            self.xbase = block.xlast
            self.xlist.append(self.xbase)
            # Первый блок - это всегда bot спрайт
            self.sprite_list.append(('bot', 0))
        else:
            self.xlist.append(block.xlast)
            # Средние блоки - по кругу от 0 до 3
            self.sprite_list.append((block.sprite_type, block.sprite_index))
        
        if self.size <= 5:
            self.height = self.size * BLOCK_HEIGHT
            self.y = 600 - self.height
        else:
            self.height += BLOCK_HEIGHT
            self.y -= BLOCK_HEIGHT
    
    def get_width(self):
        """Получить ширину башни"""
        width = BLOCK_WIDTH
        if self.size == 0 or self.size == -1:
            return width
        
        if self.xlist[-1] > self.xbase:
            width = (self.xlist[-1] - self.xbase) + BLOCK_WIDTH
        
        if self.xlist[-1] < self.xbase:
            width = -((self.xbase - self.xlist[-1]) + BLOCK_WIDTH)
        
        return width
    
    def draw(self):
        """Отрисовка башни"""
        if self.size >= 1:
            surf = pygame.Surface((800, self.onscreen * BLOCK_HEIGHT), pygame.SRCALPHA)
            surf.convert_alpha()
            
            if self.redraw:
                buildlist = self.xlist[-self.onscreen:]
                spritelist = self.sprite_list[-self.onscreen:]
            else:
                buildlist = self.xlist
                spritelist = self.sprite_list
            
            for i in range(len(buildlist)):
                sprite_type, sprite_index = spritelist[i]
                
                # Выбор спрайта
                if self.golden and i == len(buildlist) - 1:
                    block_img = self.image_gold
                elif sprite_type == 'bot':
                    block_img = self.tower_sprites['bot']
                else:  # mid
                    block_img = self.tower_sprites['mid'][sprite_index]
                
                y_pos = self.onscreen * BLOCK_HEIGHT - BLOCK_HEIGHT * (i + 1)
                surf.blit(block_img, (buildlist[i], y_pos))
        else:
            surf = pygame.Surface((0, 0))
        
        self.rect = surf.get_rect()
        return surf
    
    def unbuild(self, block):
        """Удалить верхний блок"""
        self.display_status = False
        if self.y > block.y:
            block.y = self.y
            self.size -= 1
        
        surf = pygame.Surface((800, (self.onscreen - 1) * BLOCK_HEIGHT), pygame.SRCALPHA)
        surf.convert_alpha()
        
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
        """Обрушение башни"""
        self.y += 5
        if direction == "l":
            self.x -= 5
        elif direction == "r":
            self.x += 5
    
    def wobble(self):
        """Шатание башни"""
        width = self.get_width()
        if ((width > 100 or width < -100) and self.size >= 5) or self.size >= 20:
            self.wobbling = True
        
        if self.wobbling:
            self.change += self.speed
        
        if self.change > WOBBLE_LIMIT:
            self.speed = -WOBBLE_SPEED
        elif self.change < -WOBBLE_LIMIT:
            self.speed = WOBBLE_SPEED
    
    def display(self, screen):
        """Отображение башни на экране"""
        surf = self.draw()
        screen.blit(surf, (self.x + self.change, self.y))
    
    def scroll(self):
        """Прокрутка башни"""
        if self.y <= 440:
            self.y += 5
            self.scrolling = True
        else:
            self.height = 160
            self.scrolling = False
            self.onscreen = MAX_ONSCREEN_BLOCKS
    
    def reset(self):
        """Сброс для прокрутки"""
        self.redraw = True
        if self.onscreen >= 7:
            self.onscreen = MAX_ONSCREEN_BLOCKS
            self.y = 440
