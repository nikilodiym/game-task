import os
import pygame
from core.events import EventManager, EventType


class Enemy(pygame.sprite.Sprite):
    SPEED = 80
    HP = 100
    DAMAGE = 15
    SIZE = 62

    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = self._load_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.pos = pygame.math.Vector2(x, y)
        self.radius = self.SIZE - 4
        self.hp = self.HP
        self.damage = self.DAMAGE
        self._dmg_cd = 0.0

    def _load_image(self) -> pygame.Surface:
        raw = pygame.image.load(os.path.join("assets", "zombie.png")).convert_alpha()
        size = self.SIZE * 2
        return pygame.transform.scale(raw, (size, size))

    def update(self, dt: float, player_pos: pygame.math.Vector2) -> None:
        direction = player_pos - self.pos
        if direction.length() > 0:
            self.pos += direction.normalize() * self.SPEED * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        if self._dmg_cd > 0:
            self._dmg_cd -= dt

    def take_damage(self, amount: int) -> bool:
        self.hp -= amount
        if self.hp <= 0:
            EventManager().emit(EventType.ENEMY_KILLED, {"pos": self.pos.copy()})
            self.kill()
            return True
        return False

    def can_damage(self) -> bool:
        return self._dmg_cd <= 0

    def reset_damage_cooldown(self) -> None:
        self._dmg_cd = 0.9


class FastEnemy(Enemy):
    SPEED = 145
    HP = 55
    DAMAGE = 10
    SIZE = 44


class TankEnemy(Enemy):
    SPEED = 45
    HP = 300
    DAMAGE = 25
    SIZE = 88
