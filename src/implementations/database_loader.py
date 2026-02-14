from typing import Optional
from src.interfaces.loader import CacheLoader
from src.utils.logger import logger

class DatabaseLoader(CacheLoader[str, str]):
    def __init__(self, db_conn):
        self.db = db_conn
    
    def load(self, key: str) -> Optional[str]:
        logger.info(f"[Loader] Fetching {key} from DB...")
        return self.db.get(key)
