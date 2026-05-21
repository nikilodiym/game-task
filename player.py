import math
import os
import pygame

from core.events import EventManager, EventType
from core.strategies import SingleShotStrategy, ShootingStrategy


class Player(pygame.sprite.Sprite):
    SPEED = 220
    MAX_HP = 100
    SIZE = 54

    def __init__(self, x: float, y: float):
        super().__init__()
        raw = pygame.image.load(os.path.join("assets", "player.png")).convert_alpha()
        self.base_image = pygame.transform.scale(raw, (self.SIZE * 2, self.SIZE * 2))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.pos = pygame.math.Vector2(x, y)
        self.radius = self.SIZE - 4
        self.hp = self.MAX_HP
        self._shoot_timer = 0.0
        self._strategy: ShootingStrategy = SingleShotStrategy()
        self.alive_flag = True

    def set_strategy(self, strategy: ShootingStrategy) -> None:
        self._strategy = strategy

    def handle_input(self, keys, dt: float) -> None:
        move = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:    move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x += 1
        if move.length_squared() > 0:
            move = move.normalize()
        self.pos += move * self.SPEED * dt

    def clamp(self, world_w: int, world_h: int) -> None:
        self.pos.x = max(self.SIZE, min(world_w - self.SIZE, self.pos.x))
        self.pos.y = max(self.SIZE, min(world_h - self.SIZE, self.pos.y))
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def rotate_to(self, world_target: tuple) -> None:
        dx = world_target[0] - self.pos.x
        dy = world_target[1] - self.pos.y
        angle = -math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def try_shoot(self, world_target: tuple, bullet_groups: list) -> list:
        if self._shoot_timer > 0:
            return []
        dx = world_target[0] - self.pos.x
        dy = world_target[1] - self.pos.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            return []
        direction = (dx / dist, dy / dist)
        self._shoot_timer = self._strategy.cooldown
        return self._strategy.shoot(self.pos, direction, bullet_groups)

    def update(self, dt: float) -> None:
        if self._shoot_timer > 0:
            self._shoot_timer -= dt

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        EventManager().emit(EventType.PLAYER_HIT, {"amount": amount, "hp": self.hp})
        if self.hp <= 0 and self.alive_flag:
            self.alive_flag = False
            EventManager().emit(EventType.PLAYER_DIED, {})

    def heal(self, amount: int) -> None:
        self.hp = min(self.MAX_HP, self.hp + amount)
