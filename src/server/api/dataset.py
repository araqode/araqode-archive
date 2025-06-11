# Dataset API endpoints
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from .dataset_utils import list_dataset_dir

DATASET_DIR = Path(__file__).parent.parent.parent.parent / "dataset"

router = APIRouter()

@router.get("/api/list/root.json")
def list_files_root():
    return list_files("")

@router.get("/api/list/{path:path}.json")
def list_files(path: str = ""):
    """List files and folders in the dataset directory."""
    try:
        return list_dataset_dir(DATASET_DIR, path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
