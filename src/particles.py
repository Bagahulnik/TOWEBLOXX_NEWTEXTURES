import pygame
import math
import random
from src.constants import *

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.max_particles = 200  # УВЕЛИЧИЛИ!
        
    def add_explosion(self, x, y, color=(255, 255, 200), count=40):  # БЫЛО 25
        """🔥 ВЗРЫВ при золотом блоке"""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                particle = {
                    'x': x, 'y': y - BLOCK_HEIGHT//4,  # ↑ НА 1/4 БЛОКА ВЫШЕ
                    'vx': random.uniform(-6, 6),
                    'vy': random.uniform(-5, 1),
                    'life': 60,  # Дольше живут
                    'max_life': 60,
                    'color': color,
                    'size': random.uniform(4, 8)  # Больше
                }
                self.particles.append(particle)
    
    def add_build_particles(self, x, y, count=25):  # БЫЛО 15
        """💨 Пыль при обычном строительстве"""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                particle = {
                    'x': x, 'y': y - BLOCK_HEIGHT//4,  # ↑ НА 1/4 БЛОКА ВЫШЕ
                    'vx': random.uniform(-4, 4),
                    'vy': random.uniform(-1, 2),
                    'life': 40,
                    'max_life': 40,
                    'color': (230, 210, 170),
                    'size': random.uniform(2, 5)
                }
                self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.12  # Меньше гравитация
            particle['vx'] *= 0.96  # Медленнее затухает
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            alpha_ratio = particle['life'] / particle['max_life']
            size = int(particle['size'] * alpha_ratio)
            alpha = int(255 * alpha_ratio ** 0.7)  # Плавнее угасание
            
            if size > 0:
                # БОЛЬШЕ И ЯРЧЕ
                surf = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*particle['color'][:3], alpha), (size*2, size*2), max(1, size))
                screen.blit(surf, (int(particle['x'] - size*2), int(particle['y'] - size*2)))
