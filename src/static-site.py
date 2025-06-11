# Static site generator for dataset API and web UI
import os
import shutil
import json
from pathlib import Path
from .server.api.dataset_utils import list_dataset_dir

# Paths
ROOT = Path(__file__).parent.parent.resolve()

# Inputs
DATASET_BUILD = ROOT / "dataset"
WEB_BUILD = ROOT / "src" / "web" / "dist"
WEB_INDEX_BUILD = WEB_BUILD / "index.html"

# Outputs
DIST = ROOT / "dist"
WEB_DIST = DIST / "web"
DATASET_DIST = DIST / "dataset"
API_DIST = DIST / "api"
API_LIST_DIST = API_DIST / "list"

# Clean and create dist structure
def prepare_dist():
    if DIST.exists():
        shutil.rmtree(DIST)
    (API_LIST_DIST).mkdir(parents=True, exist_ok=True)

def rel_path(path):
    return path.relative_to(DATASET_BUILD).as_posix()

def generate_api():
    # Walk dataset and generate list/file outputs
    for dirpath, dirnames, filenames in os.walk(DATASET_BUILD):
        rel = rel_path(Path(dirpath))
        # Use shared utility to generate items
        items = list_dataset_dir(DATASET_BUILD, rel)["items"]
        # Write list output to mimic /api/list/{path:path}.json
        if rel != ".":
            list_json_path = API_LIST_DIST / f"{rel}.json"
        else:
            list_json_path = API_LIST_DIST / "root.json"
        list_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(list_json_path, "w", encoding="utf-8") as f:
            json.dump({"items": items}, f, indent=2)

def copy_web():
    # Copy web/dist to dist/web
    shutil.copytree(WEB_BUILD, WEB_DIST)
    # Copy web/index.html to dist/index.html
    shutil.copy2(WEB_INDEX_BUILD, DIST / "index.html")

def copy_dataset():
    # Copy dataset files to dist/dataset
    shutil.copytree(DATASET_BUILD, DATASET_DIST, dirs_exist_ok=True)

def main():
    prepare_dist()
    generate_api()
    copy_web()
    copy_dataset()
    print("Static site generated in dist/")

if __name__ == "__main__":
    main()
