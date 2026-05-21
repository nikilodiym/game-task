import math
import os
import pygame


class Bullet(pygame.sprite.Sprite):
    SPEED = 560
    DAMAGE = 25
    LIFETIME = 2.4

    def __init__(self, x: float, y: float, direction: tuple):
        super().__init__()
        raw = pygame.image.load(os.path.join("assets", "bullet.png")).convert_alpha()
        self.image = pygame.transform.scale(raw, (40, 40))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.pos = pygame.math.Vector2(x, y)
        self.radius = 6

        mag = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        if mag > 0:
            vx, vy = direction[0] / mag * self.SPEED, direction[1] / mag * self.SPEED
        else:
            vx, vy = self.SPEED, 0.0
        self.velocity = pygame.math.Vector2(vx, vy)
        self.lifetime = self.LIFETIME

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.pos += self.velocity * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
