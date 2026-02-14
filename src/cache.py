import threading
from typing import Generic, TypeVar, Optional, Dict
from src.interfaces.loader import CacheLoader
from src.interfaces.writer import CacheWriter
from src.interfaces.eviction_policy import EvictionPolicy
from src.utils.logger import logger
from src.utils.request_coalescer import RequestCoalescer

K = TypeVar('K')
V = TypeVar('V')

# --- 4. The Cache: Composition over Inheritance ---

class RobustCache(Generic[K, V]):
    def __init__(self, 
                 capacity: int, 
                 eviction_policy: EvictionPolicy[K],
                 loader: Optional[CacheLoader[K, V]] = None,
                 writer: Optional[CacheWriter[K, V]] = None):
        
        self.capacity = capacity
        self.storage: Dict[K, V] = {}
        self.eviction = eviction_policy
        self.loader = loader
        self.writer = writer
        self.lock = threading.RLock()
        self.coalescer = RequestCoalescer() # Initialize Coalescer

    def get(self, key: K) -> Optional[V]:
        # 1. Cache Hit (Fast Path)
        with self.lock:
            if key in self.storage:
                self.eviction.on_access(key)
                logger.debug(f"[Cache] HIT for {key}")
                return self.storage[key]

        logger.debug(f"[Cache] MISS for {key}")

        # 2. Cache Miss - Coalesced Load
        if self.loader:
            # Use Coalescer to ensure only one DB load happens
            value = self.coalescer.do(key, lambda: self._load_from_source(key))
            return value
        
        return None

    def _load_from_source(self, key: K) -> Optional[V]:
        """
        Helper for Coalescer.
        Loads from DB and Updates Cache.
        """
        value = self.loader.load(key)
        if value is not None:
             # We need to acquire lock inside put/put_internal, so it's safe to call here.
             # However, we must be careful not to deadlock if _put_internal uses the same lock
             # and we are already holding it. 
             # Here we are NOT holding self.lock (we released it after step 1).
             self._put_internal_thread_safe(key, value)
        return value

    def _put_internal_thread_safe(self, key: K, value: V):
        with self.lock:
            self._put_internal(key, value)

    def put(self, key: K, value: V):
        with self.lock:
            # 1. Write-Through / Write-Back - Delegate to Writer if it exists
            if self.writer:
                self.writer.write(key, value)
            
            # 2. Update Cache
            self._put_internal(key, value)

    def _put_internal(self, key: K, value: V):
        if key not in self.storage and len(self.storage) >= self.capacity:
            victim = self.eviction.evict()
            if victim:
                del self.storage[victim]
        
        self.storage[key] = value
        self.eviction.on_access(key)
