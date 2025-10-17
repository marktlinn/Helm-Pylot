import logging
import os

logging.basicConfig(level=os.environ.get("LOG_LEVEL", logging.DEBUG))
logger = logging.getLogger()

__all__ = [logger]
