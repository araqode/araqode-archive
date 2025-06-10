# Dataset API endpoints
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

DATASET_DIR = Path(__file__).parent.parent.parent.parent / "dataset"

router = APIRouter()

@router.get("/api/list")
def list_files(path: str = ""):
    """List files and folders in the dataset directory."""
    base = DATASET_DIR / path
    if not base.exists():
        raise HTTPException(status_code=404, detail=f"[{base}] Path not found")
    items = []
    for entry in base.iterdir():
        items.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "path": str((Path(path) / entry.name).as_posix())
        })
    return {"items": items}

@router.get("/api/file")
def get_file(path: str):
    """Download or preview a file from the dataset."""
    file_path = DATASET_DIR / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
