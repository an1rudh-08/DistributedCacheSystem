from typing import Generic, Optional, TypeVar
from src.interfaces.eviction_policy import EvictionPolicy

K = TypeVar('K')

class LRUPolicy(EvictionPolicy[K]):
    # ... (Standard LRU logic using Doubly Linked List) ...
    def __init__(self):
        self.order = [] # Simplified for brevity
    def on_access(self, key: K):
        if key in self.order: self.order.remove(key)
        self.order.append(key)
    def evict(self) -> Optional[K]:
        return self.order.pop(0) if self.order else None
