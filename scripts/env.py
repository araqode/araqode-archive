# araqode-archive
# A curated, multi-modal dataset

import os
from dotenv import load_dotenv
from .constants import ENV_VARS

def load_env():
    """Load environment variables from a .env file."""
    load_dotenv()
    env = {
        var: os.environ.get(var)
        for var in ENV_VARS
    }
    return env

def ensure_local_dir(path):
    """Ensure that the local directory exists."""
    os.makedirs(path, exist_ok=True)
