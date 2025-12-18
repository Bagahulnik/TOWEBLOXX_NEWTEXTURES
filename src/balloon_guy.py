"""
Модуль balloon_guy.py - персонажи на воздушных шарах
Создаёт анимированных персонажей, которые летают на фоне башни,
добавляя динамику и живость игровому процессу.
"""
import pygame
import random
from src.constants import ASSETS_PATH, SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class BalloonGuy(pygame.sprite.Sprite):
    """
    Класс персонажа на воздушном шаре.
    Летает вверх по экрану с анимацией, создавая атмосферу.
    После вылета за экран перезапускается с новой позицией и задержкой.
    """
    def __init__(self, person_id, start_x, speed_y, start_delay_frames=0):
        super().__init__()

        self.frames = []
        base_path = f"{ASSETS_PATH}people/person_{person_id}/"
        target_size = (50, 100)
        # Загружаем 4 кадра анимации для каждого персонажа
        for i in range(4):
            img = pygame.image.load(
                base_path + f"person_{person_id}_{i}.png"
            ).convert_alpha()
            # Масштабируем до нужного размера
            img = pygame.transform.smoothscale(img, target_size)
            self.frames.append(img)
        # === ПАРАМЕТРЫ ПЕРСОНАЖА ===
        self.person_id = person_id
        self.base_x = start_x
        self.speed_y = speed_y
        # Настройка анимации
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

        # Стартуем за нижней границей экрана
        self.rect.centerx = start_x
        self.rect.top = SCREEN_HEIGHT + 100

        # Задержка в кадрах перед началом движения
        self.start_delay = start_delay_frames
        self.age = 0  # сколько кадров живёт этот запуск

        self.anim_counter = 0 # Счётчик кадров для смены спрайта
        self.anim_speed = 8 # Скорость анимации (меняем спрайт каждые 8 кадров)

    def reset_flight(self):
        """
        Перезапускает полёт персонажа после вылета за экран.
        Создаёт небольшое случайное смещение по X и новую задержку
        для разнообразия и избежания предсказуемости.
        """
        # Небольшое случайное смещение относительно базовой позиции (±40 пикселей)
        shift = random.randint(-40, 40)
        new_x = max(20, min(SCREEN_WIDTH - 20, self.base_x + shift))
        self.rect.centerx = new_x

        # стартуем чуть ниже экрана
        self.rect.top = SCREEN_HEIGHT + random.randint(40, 120)

        # новая задержка 0..2 секунд
        self.start_delay = random.randint(0, 2 * FPS)
        self.age = 0

    def update(self):
        """
        Обновляет состояние персонажа каждый кадр.
        Управляет задержкой старта, движением, анимацией и перезапуском.
        """
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
        # Циклично меняем кадры анимации для эффекта движения
        self.anim_counter += 1
        if self.anim_counter >= self.anim_speed:
            self.anim_counter = 0
            # Переключаемся на следующий кадр (циклично через все 4)
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
