from typing import TypeVar, Generic
from src.interfaces.writer import CacheWriter
from src.utils.logger import logger

K = TypeVar('K')
V = TypeVar('V')

class WriteThroughWriter(CacheWriter[K, V]):
    """
    Write-Through Strategy:
    Writes data synchronously to the source of truth (DB) 
    BEFORE it is confirmed as written to the cache.
    Ensures strong consistency but higher latency for writes.
    """
    def __init__(self, db_adapter):
        self.db = db_adapter

    def write(self, key: K, value: V) -> None:
        try:
            logger.info(f"[Write-Through] Writing {key} to DB synchronously...")
            self.db.set(key, value)
            logger.info(f"[Write-Through] Successfully wrote {key} to DB.")
        except Exception as e:
            logger.error(f"[Write-Through] Failed to write {key} to DB: {e}")
            raise e

    def delete(self, key: K) -> None:
        # Implementation depends on DB adapter support
        pass
