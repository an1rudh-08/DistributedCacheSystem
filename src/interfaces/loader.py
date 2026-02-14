from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

K = TypeVar('K')
V = TypeVar('V')

class CacheLoader(ABC, Generic[K, V]):
    """Responsible ONLY for loading data from the source of truth."""
    @abstractmethod
    def load(self, key: K) -> Optional[V]:
        pass
