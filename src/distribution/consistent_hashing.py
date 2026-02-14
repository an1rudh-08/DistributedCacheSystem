import hashlib
import bisect
from typing import List, Any
from src.utils.logger import logger

class ConsistentHashing:
    """
    Implements a Consistent Hashing Ring with Virtual Nodes.
    Ensures even distribution of keys across nodes and minimizes data movement
    when nodes are added or removed.
    """
    def __init__(self, nodes: List[Any] = None, replicas: int = 3):
        self.replicas = replicas
        self.ring: dict = {}
        self.sorted_keys: List[int] = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        """MD5 hash for stable distribution."""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: Any):
        """Adds a node to the ring with `replicas` virtual nodes."""
        logger.info(f"[ConsistentHash] Adding node: {node}")
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node: Any):
        """Removes a node and all its virtual nodes from the ring."""
        logger.info(f"[ConsistentHash] Removing node: {node}")
        keys_to_remove = []
        for key, n in self.ring.items():
            if n == node:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key: str) -> Any:
        """Returns the node responsible for the given key."""
        if not self.ring:
            return None
        
        hashed_key = self._hash(key)
        # Find the first node clockwise in the ring with a hash >= key's hash
        idx = bisect.bisect(self.sorted_keys, hashed_key)
        
        # Wrap around to the beginning if we reached the end
        if idx == len(self.sorted_keys):
            idx = 0
            
        node_key = self.sorted_keys[idx]
        return self.ring[node_key]
