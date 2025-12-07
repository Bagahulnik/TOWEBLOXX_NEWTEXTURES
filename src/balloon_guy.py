import pygame
import random
from src.constants import ASSETS_PATH, SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class BalloonGuy(pygame.sprite.Sprite):
    def __init__(self, person_id, start_x, speed_y, start_delay_frames=0):
        super().__init__()

        self.frames = []
        base_path = f"{ASSETS_PATH}people/person_{person_id}/"
        target_size = (50, 100)

        for i in range(4):
            img = pygame.image.load(
                base_path + f"person_{person_id}_{i}.png"
            ).convert_alpha()
            img = pygame.transform.smoothscale(img, target_size)
            self.frames.append(img)

        self.person_id = person_id
        self.base_x = start_x
        self.speed_y = speed_y

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

        # старт пока за экраном
        self.rect.centerx = start_x
        self.rect.top = SCREEN_HEIGHT + 100

        # задержка старта в кадрах
        self.start_delay = start_delay_frames
        self.age = 0  # сколько кадров живёт этот запуск

        self.anim_counter = 0
        self.anim_speed = 8

    def reset_flight(self):
        """Новый вылет: слегка сместить по X и задать случайную задержку."""
        # небольшое хаотичное смещение по X (+-40px, но не выходим за экран)
        shift = random.randint(-40, 40)
        new_x = max(20, min(SCREEN_WIDTH - 20, self.base_x + shift))
        self.rect.centerx = new_x

        # стартуем чуть ниже экрана
        self.rect.top = SCREEN_HEIGHT + random.randint(40, 120)

        # новая задержка 0..2 секунд
        self.start_delay = random.randint(0, 2 * FPS)
        self.age = 0

    def update(self):
        self.age += 1

        # ждём «взлёта»
        if self.age <= self.start_delay:
            return

        # движение по вертикали
        self.rect.y += self.speed_y

        # вылетел вверх — запускаем заново (новая задержка и сдвиг)
        if self.rect.bottom < -40:
            self.reset_flight()
            return

        # анимация
        self.anim_counter += 1
        if self.anim_counter >= self.anim_speed:
            self.anim_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
