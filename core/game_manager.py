from core.events import EventManager, EventType


class GameManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.score: int = 0
        self.wave: int = 1
        self.game_state: str = "playing"
        self.enemies_killed_this_wave: int = 0
        self.enemies_per_wave: int = 8

        em = EventManager()
        em.subscribe(EventType.ENEMY_KILLED, self._on_enemy_killed)
        em.subscribe(EventType.PLAYER_DIED, self._on_player_died)

    def _on_enemy_killed(self, data) -> None:
        self.score += 10 * self.wave
        self.enemies_killed_this_wave += 1

    def _on_player_died(self, data) -> None:
        self.game_state = "dead"

    def wave_target(self) -> int:
        return self.enemies_per_wave + (self.wave - 1) * 4

    def advance_wave(self) -> None:
        self.wave += 1
        self.enemies_killed_this_wave = 0

    def reset(self) -> None:
        self._initialized = False
        EventManager().clear()
        self.initialize()
