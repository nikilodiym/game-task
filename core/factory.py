import random


class EntityFactory:
    @staticmethod
    def create_enemy(enemy_type: str, x: float, y: float):
        from enemy import Enemy, FastEnemy, TankEnemy
        types = {"normal": Enemy, "fast": FastEnemy, "tank": TankEnemy}
        return types.get(enemy_type, Enemy)(x, y)

    @staticmethod
    def create_enemy_for_wave(wave: int, x: float, y: float):
        if wave <= 2:
            return EntityFactory.create_enemy("normal", x, y)
        elif wave <= 4:
            t = random.choices(["normal", "fast"], weights=[0.55, 0.45])[0]
            return EntityFactory.create_enemy(t, x, y)
        else:
            t = random.choices(["normal", "fast", "tank"], weights=[0.5, 0.3, 0.2])[0]
            return EntityFactory.create_enemy(t, x, y)

    @staticmethod
    def create_item(item_type: str, x: float, y: float):
        from items import HealthItem
        if item_type == "health":
            return HealthItem(x, y)
        return None
