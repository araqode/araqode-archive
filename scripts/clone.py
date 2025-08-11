# araqode-archive
# A curated, multi-modal dataset

import os
import shutil
from .constants import DATASET_DOWNLOAD_DIR
from .env import load_env
from .api import AraqodeArchiveAPI

env = load_env()
api = AraqodeArchiveAPI(
    api_host=env.get('DATAVERSE_API_HOST'),
    api_token=env.get('DATAVERSE_API_TOKEN'),
    dataset_doi=env.get('DATASET_DOI')
)

# Clean dataset dir to download fresh
if os.path.exists(DATASET_DOWNLOAD_DIR):
    shutil.rmtree(DATASET_DOWNLOAD_DIR)

api.sync_dataset(
    f"",
    download_missing=True,
    prune_remote=False
)