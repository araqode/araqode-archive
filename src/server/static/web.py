# Static web serving endpoints
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

WEB_DIR = Path(__file__).parent.parent.parent / "web" / "dist"

router = APIRouter()

@router.get("/")
def root():
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(), status_code=200)
    return HTMLResponse("<h1>Web UI not found</h1>", status_code=404)
