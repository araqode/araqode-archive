# Dataset utility functions for reuse
from pathlib import Path

def list_dataset_dir(base: Path, rel_path: str = ""):
    """List files and folders in the dataset directory."""
    target = base / rel_path
    if not target.exists():
        raise FileNotFoundError(f"[{target}] Path not found")
    items = []
    for entry in target.iterdir():
        items.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "path": str((Path(rel_path) / entry.name).as_posix())
        })
    return {"items": items}
