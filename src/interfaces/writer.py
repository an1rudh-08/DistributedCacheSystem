from abc import ABC, abstractmethod
from typing import TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')

class CacheWriter(ABC, Generic[K, V]):
    """Responsible ONLY for writing data to the source of truth."""
    @abstractmethod
    def write(self, key: K, value: V) -> None:
        pass
        
    @abstractmethod
    def delete(self, key: K) -> None:
        pass
