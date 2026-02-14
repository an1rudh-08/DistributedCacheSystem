from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

K = TypeVar('K')

class EvictionPolicy(ABC, Generic[K]):
    @abstractmethod
    def on_access(self, key: K): pass
    @abstractmethod
    def evict(self) -> Optional[K]: pass
