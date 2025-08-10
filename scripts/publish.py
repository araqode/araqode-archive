# araqode-archive
# A curated, multi-modal dataset

import time
from .env import load_env
from .api import AraqodeArchiveAPI

env = load_env()
api = AraqodeArchiveAPI(
    api_host=env.get('DATAVERSE_API_HOST'),
    api_token=env.get('DATAVERSE_API_TOKEN'),
    dataset_doi=env.get('DATASET_DOI')
)

# Get formatted local timestamp with timezone info using time module
timestamp = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())

api.sync_dataset(
    f"Syncing {env.get('DATASET_NAME')} at {timestamp}",
    download_missing=False,
    prune_remote=True
)