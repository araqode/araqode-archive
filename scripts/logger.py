# araqode-archive
# A curated, multi-modal dataset

from logging import getLogger, Formatter, FileHandler, StreamHandler, DEBUG
from .constants import TMP_DIR
from .env import ensure_local_dir

def setup_logger(name, log_file, level=DEBUG):
    """Function to setup a logger with a file handler and console handler."""
    logger = getLogger(name)
    logger.setLevel(level)
    fmt = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'

    # File handler
    file_handler = FileHandler(log_file)
    file_handler.setLevel(level)
    file_formatter = Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = StreamHandler()
    console_handler.setLevel(level)
    console_formatter = Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

ensure_local_dir(TMP_DIR)
api_logger = setup_logger('api', f'{TMP_DIR}/api.log')