import time
import threading
import random
from src.cache import RobustCache
from src.implementations.lru_policy import LRUPolicy
from src.implementations.lfu_policy import LFUPolicy
from src.implementations.database_loader import DatabaseLoader
from src.implementations.safe_write_back_writer import SafeWriteBackWriter
from src.implementations.write_through_writer import WriteThroughWriter
from src.distributed_cache import DistributedCache
from src.utils.logger import logger, setup_logger

# Helper to simulate a real DB
class MockDB:
    def __init__(self, data):
        self.data = data
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            # Simulate latency
            # time.sleep(0.001) 
            return self.data.get(key)
    
    def set(self, key, value):
        with self.lock:
            # time.sleep(0.005) # Writes are slower
            self.data[key] = value

def run_traffic(client, duration_sec=2):
    """Simulates high traffic load."""
    start_time = time.time()
    ops = 0
    while time.time() - start_time < duration_sec:
        key = f"user:{random.randint(1, 100)}" # Hot keys range
        
        if random.random() < 0.2: # 20% Writes
            val = f"Data-{random.randint(1000, 9999)}"
            client.put(key, val)
        else: # 80% Reads
            client.get(key)
        ops += 1
    return ops

if __name__ == "__main__":
    # Lower log level to verify internal workings, or set to INFO for high-level stats
    setup_logger(level=20) # INFO

    logger.info("=== Initializing Distributed Cache System ===")
    
    # Shared DB
    db = MockDB({"user:1": "Alice", "user:2": "Bob"})

    # Create 3 Nodes
    # Node 0: LRU + WriteBack
    node0 = RobustCache(
        capacity=10, 
        eviction_policy=LRUPolicy(), 
        loader=DatabaseLoader(db),
        writer=SafeWriteBackWriter(db)
    )
    
    # Node 1: LFU + WriteThrough
    node1 = RobustCache(
        capacity=10, 
        eviction_policy=LFUPolicy(), 
        loader=DatabaseLoader(db),
        writer=WriteThroughWriter(db)
        # writer=SafeWriteBackWriter(db) # We can use WriteBack here too if we want
    )
    
    # Node 2: LRU + ReadOnly (No Writer)
    node2 = RobustCache(
        capacity=10, 
        eviction_policy=LRUPolicy(), 
        loader=DatabaseLoader(db),
        writer=None 
    )

    cluster = DistributedCache([node0, node1, node2])

    logger.info("=== Starting Stress Test (1k req/min simulation) ===")
    
    threads = []
    num_threads = 5
    results = []

    # Run in parallel
    for i in range(num_threads):
        t = threading.Thread(target=lambda: results.append(run_traffic(cluster, duration_sec=3)), name=f"Client-{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    total_ops = sum(results)
    logger.info(f"=== Stress Test Complete ===")
    logger.info(f"Total Operations: {total_ops} in 3 seconds")
    logger.info(f"Throughput: {total_ops / 3:.2f} ops/sec")
    
    # Verification
    logger.info("=== Verifying Consistency ===")
    test_key = "user:1"
    cluster.put(test_key, "UPDATED_ALICE")
    time.sleep(0.5) # Allow write-back
    val = cluster.get(test_key)
    logger.info(f"Read {test_key}: {val} (Expected: UPDATED_ALICE)")

    # Request Coalescing Test
    logger.info("=== Verifying Request Coalescing ===")
    # We'll use a new key that is NOT in cache
    thundering_key = "user:999"
    db.set(thundering_key, "Hidden_Treasure")
    
    def fetch_concurrently():
        cluster.get(thundering_key)

    coalesce_threads = [threading.Thread(target=fetch_concurrently, name=f"Coalesce-{i}") for i in range(5)]
    
    logger.info(f"Launching 5 threads to fetch {thundering_key} simultaneously...")
    for t in coalesce_threads: t.start()
    for t in coalesce_threads: t.join()
    
    logger.info("Check logs upwards. You should see '[Loader] Fetching user:999' ONLY ONCE.")

    # Shutdown
    cluster.close()
    logger.info("=== System Shutdown ===")
