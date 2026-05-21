import math


class ShootingStrategy:
    cooldown: float = 0.25

    def shoot(self, pos, direction, groups: list) -> list:
        raise NotImplementedError


class SingleShotStrategy(ShootingStrategy):
    cooldown = 0.22

    def shoot(self, pos, direction, groups: list) -> list:
        from bullet import Bullet
        bullet = Bullet(pos[0], pos[1], direction)
        for g in groups:
            g.add(bullet)
        return [bullet]


class SpreadShotStrategy(ShootingStrategy):
    cooldown = 0.40

    def __init__(self, spread_angle: float = 18.0, count: int = 3):
        self.spread_angle = spread_angle
        self.count = count

    def shoot(self, pos, direction, groups: list) -> list:
        from bullet import Bullet
        bullets = []
        base_angle = math.atan2(direction[1], direction[0])
        spread_rad = math.radians(self.spread_angle)
        for i in range(self.count):
            offset = (i - self.count // 2) * spread_rad
            a = base_angle + offset
            d = (math.cos(a), math.sin(a))
            bullet = Bullet(pos[0], pos[1], d)
            for g in groups:
                g.add(bullet)
            bullets.append(bullet)
        return bullets
