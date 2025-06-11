import os
from dotenv import load_dotenv
from pyDataverse.api import NativeApi
from .constants import ENV_VARS

def load_env():
    load_dotenv()
    env = {var: os.environ.get(var) for var in ENV_VARS}
    return env

def get_dataverse_api(base_url, api_token):
    if not base_url or not api_token:
        raise EnvironmentError("Missing Dataverse API configuration.")
    return NativeApi(base_url, api_token)

def ensure_local_dir(path):
    os.makedirs(path, exist_ok=True)
