from collections import defaultdict, OrderedDict
from typing import TypeVar, Optional, Dict
from src.interfaces.eviction_policy import EvictionPolicy
from src.utils.logger import logger

K = TypeVar('K')

class LFUPolicy(EvictionPolicy[K]):
    """
    Least Frequently Used (LFU) Eviction Policy.
    Tracks frequency of access for each key.
    Evicts the key with the lowest frequency.
    Tie-breaking: Least Recently Used among the keys with the same lowest frequency.
    """
    def __init__(self):
        self.key_freq: Dict[K, int] = {}
        # Map frequency -> OrderedDict of keys (ordered by insertion/access time for LRU tie-breaking)
        self.freq_keys: Dict[int, OrderedDict[K, None]] = defaultdict(OrderedDict)
        self.min_freq: int = 0

    def on_access(self, key: K):
        # If key exists, increase its frequency
        if key in self.key_freq:
            old_freq = self.key_freq[key]
            # Remove from old frequency bucket
            del self.freq_keys[old_freq][key]
            
            # Clean up empty bucket
            if not self.freq_keys[old_freq]:
                del self.freq_keys[old_freq]
                # Update min_freq if we just emptied the bucket of min_freq
                if self.min_freq == old_freq:
                    self.min_freq += 1
            
            new_freq = old_freq + 1
        else:
            # New key
            new_freq = 1
            self.min_freq = 1 # Reset min_freq for new item

        self.key_freq[key] = new_freq
        self.freq_keys[new_freq][key] = None # Add to new bucket
        
        # logger.debug(f"[LFU] Accessed {key}, new freq: {new_freq}")

    def evict(self) -> Optional[K]:
        if not self.key_freq:
            return None
            
        # Get the bucket for min_freq
        victim_candidates = self.freq_keys[self.min_freq]
        
        # Pop the first item (LRU behavior within this frequency bucket)
        victim_key, _ = victim_candidates.popitem(last=False)
        
        # Clean up
        if not victim_candidates:
            del self.freq_keys[self.min_freq]
        
        del self.key_freq[victim_key]
        
        logger.info(f"[LFU] Evicting key: {victim_key} (freq: {self.min_freq})")
        return victim_key
