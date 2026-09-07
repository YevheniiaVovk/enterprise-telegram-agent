import logging
import sys


def setup_logging():
    """Configure logging for the application."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
  
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

   
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    
    logging.getLogger("httpcore").setLevel(logging.WARNING)