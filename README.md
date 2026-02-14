# ⚡ Robust Distributed Cache

A production-grade, thread-safe Distributed Cache system implemented in Python. 
Designed to demonstrate advanced Low-Level Design (LLD) principles, concurrency patterns, and distributed system concepts.

---

## 🚀 Key Features

### 1. Distributed Consistency (Consistent Hashing)
- Implements a **Hash Ring with Virtual Nodes** to evenly distribute keys across cache instances.
- Minimizes key remapping when nodes are added or removed, ensuring high availability and horizontal scalability.

### 2. Thundering Herd Protection (Request Coalescing)
- Implements **Singleflight** pattern (`src/utils/request_coalescer.py`).
- Ensures that concurrent requests for the same missing key trigger only **one** backend database fetch.
- All other requests wait and share the result, preventing DB overload during cache expiry storms.

### 3. Advanced Eviction Policies
- **LFU (Least Frequently Used)**: O(1) implementation using frequency buckets and Doubly Linked Lists.
- **LRU (Least Recently Used)**: Standard O(1) implementation using OrderedDict.
- Pluggable interface (`EvictionPolicy`) allows easy addition of new policies (e.g., ARC, FIFO).

### 4. Robust Write Strategies
- **Write-Through**: Synchronous writes to the DB for strong consistency.
- **Write-Back**: Asynchronous writes using a background worker queue with graceful shutdown handling. Ensures high write throughput.

### 5. Production-Ready Engineering
- **Thread Safety**: Granular locking (RLock) ensures safe concurrent access.
- **Safe Shutdown**: Graceful termination of background writers to prevent data loss.
- **Structured Logging**: detailed thread-aware logging for debugging and observability.
- **Interface Segregation**: Clean separation of `Loader`, `Writer`, and `Eviction` interfaces.

---

## 📂 Project Structure

```text
src/
├── cache.py                  # Main RobustCache implementation
├── distributed_cache.py      # Client-side router (The "SDK")
├── distribution/
│   └── consistent_hashing.py # Hash Ring logic
├── implementations/
│   ├── database_loader.py
│   ├── lfu_policy.py         # O(1) LFU
│   ├── lru_policy.py
│   ├── safe_write_back_writer.py
│   └── write_through_writer.py
├── interfaces/               # Abstract Base Classes (Contracts)
│   ├── eviction_policy.py
│   ├── loader.py
│   └── writer.py
└── utils/
    ├── logger.py             # Structured Logging
    └── request_coalescer.py  # Singleflight logic
```

## 🛠️ Setup & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/robust-distributed-cache.git
   cd robust-distributed-cache
   ```

2. **Run the demo (Stress Test)**:
   ```bash
   python3 main.py
   ```
   *Runs a multithreaded simulation verifying throughput, consistency, and coalescing.*

---

## 🔮 Future Roadmap

To further enhance this system for enterprise-scale workloads, the following features are planned:

- [ ] **TTL (Time-To-Live)**: Per-key expiration to ensure eventual consistency.
- [ ] **Bloom Filters**: To quickly check if a key *might* exist before querying the DB, reducing unnecessary hits for non-existent keys.
- [ ] **Network Layer (gRPC/TCP)**: Decouple nodes into separate processes/containers for true distributed deployment.
- [ ] **Metrics & Observability**: Integration with Prometheus for tracking Hit Rate, Eviction Count, and Latency.
- [ ] **WAL (Write Ahead Log)**: Durability for the cache itself explicitly for disaster recovery.

---

## 👤 Author

**Anirudh**  
*Building scalable systems with clean architecture.*

[LinkedIn](#) | [GitHub](#)
