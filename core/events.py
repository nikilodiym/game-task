from enum import Enum, auto
from typing import Callable, Dict, List, Any


class EventType(Enum):
    PLAYER_HIT = auto()
    ENEMY_KILLED = auto()
    ITEM_PICKED = auto()
    PLAYER_DIED = auto()
    WAVE_COMPLETE = auto()


class EventManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: Dict[EventType, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def emit(self, event_type: EventType, data: Any = None) -> None:
        for cb in list(self._subscribers.get(event_type, [])):
            cb(data)

    def clear(self) -> None:
        self._subscribers.clear()
