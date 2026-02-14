import logging
import sys

def setup_logger(name: str = "DistributedCache", level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a structured logger.
    Format: timestamp - [ThreadName] - Level - Message
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter
        # Include Thread separation for debugging concurrency
        formatter = logging.Formatter(
            '%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

# Singleton instance for easy import
logger = setup_logger()
