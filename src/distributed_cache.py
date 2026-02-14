from typing import List, TypeVar, Optional
from src.distribution.consistent_hashing import ConsistentHashing
from src.cache import RobustCache
from src.utils.logger import logger

K = TypeVar('K')
V = TypeVar('V')

class DistributedCache:
    """
    Client interface for the Distributed Cache system.
    Routes requests to the appropriate Cache Node using Consistent Hashing.
    """
    def __init__(self, nodes: List[RobustCache]):
        # In a real system, 'nodes' would be network addresses. 
        # Here, we pass actual RobustCache instances to simulate nodes.
        self.nodes = nodes
        self.node_map = {f"Node-{i}": node for i, node in enumerate(nodes)}
        self.hashing = ConsistentHashing(list(self.node_map.keys()))
        logger.info(f"[DistributedCache] Initialized with {len(nodes)} nodes.")

    def get(self, key: str) -> Optional[V]:
        node_name = self.hashing.get_node(key)
        if not node_name:
            logger.error("[DistributedCache] No nodes available!")
            return None
            
        node = self.node_map[node_name]
        logger.debug(f"[Router] Routing GET {key} -> {node_name}")
        return node.get(key)

    def put(self, key: str, value: V):
        node_name = self.hashing.get_node(key)
        if not node_name:
            logger.error("[DistributedCache] No nodes available!")
            return
            
        node = self.node_map[node_name]
        logger.debug(f"[Router] Routing PUT {key} -> {node_name}")
        node.put(key, value)
        
    def add_node(self, node: RobustCache, name: str):
        self.node_map[name] = node
        self.hashing.add_node(name)
        
    def remove_node(self, name: str):
        if name in self.node_map:
            self.hashing.remove_node(name)
            del self.node_map[name]

    def close(self):
        """Shut down all writers in all nodes."""
        for name, node in self.node_map.items():
             if node.writer and hasattr(node.writer, 'close'):
                 logger.info(f"[DistributedCache] Closing writer for {name}")
                 node.writer.close()
