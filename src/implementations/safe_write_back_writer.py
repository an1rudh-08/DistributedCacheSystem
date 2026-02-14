import threading
import queue
from typing import TypeVar
from src.interfaces.writer import CacheWriter
from src.utils.logger import logger

K = TypeVar('K')
V = TypeVar('V')

# Define STOP_SIGNAL
STOP_SIGNAL = object()

class SafeWriteBackWriter(CacheWriter[K, V]):
    def __init__(self, db_adapter):
        self.db = db_adapter
        self.queue = queue.Queue()
        
        # SDE-3 FIX: We still use daemon=True so it doesn't block program exit 
        # IF we crash, but we rely on explicit close() to ensure data safety.
        self.worker = threading.Thread(target=self._flusher, daemon=True, name="WriteBackWorker")
        self.worker.start()

    def write(self, key: K, value: V):
        self.queue.put((key, value))

    def delete(self, key: K):
        pass

    def close(self):
        """
        Graceful Shutdown:
        1. Send Stop Signal.
        2. Wait for worker to finish processing pending items.
        """
        logger.info("[Writer] Initiating Graceful Shutdown...")
        self.queue.put(STOP_SIGNAL) # 1. Inject Poison Pill
        self.worker.join()          # 2. Block until queue is drained
        logger.info("[Writer] Shutdown Complete. All data persisted.")

    def _flusher(self):
        while True:
            item = self.queue.get()
            
            # Check for Poison Pill
            if item is STOP_SIGNAL:
                self.queue.task_done()
                logger.info("  [Worker] Stop Signal received. Exiting loop.")
                break 
            
            # Normal Processing
            try:
                key, value = item
                logger.info(f"  [Worker] Persisting {key} -> {value}")
                self.db.set(key, value) # Simulate DB write
            except Exception as e:
                logger.error(f"  [Worker] Error writing {key}: {e}")
            finally:
                self.queue.task_done()
