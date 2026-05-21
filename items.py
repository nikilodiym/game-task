import math
import pygame


class HealthItem(pygame.sprite.Sprite):
    HEAL_AMOUNT = 35
    LIFETIME = 12.0

    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = self._make_image()
        self.pos = pygame.math.Vector2(x, y)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.heal_amount = self.HEAL_AMOUNT
        self.lifetime = self.LIFETIME
        self._t = 0.0

    @staticmethod
    def _make_image() -> pygame.Surface:
        surf = pygame.Surface((58, 58), pygame.SRCALPHA)
        red = (220, 45, 45)
        pygame.draw.rect(surf, red, (25, 5, 8, 48), border_radius=4)
        pygame.draw.rect(surf, red, (5, 25, 48, 8), border_radius=4)
        return surf

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self._t += dt
        bob = int(math.sin(self._t * 3.5) * 3)
        self.rect.center = (int(self.pos.x), int(self.pos.y) + bob)
