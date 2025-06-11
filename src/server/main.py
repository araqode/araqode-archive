# FastAPI server for dataset browsing and script API
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from api.dataset import router as dataset_router
from static.web import router as web_router

# Use absolute path to dataset at project root
DATASET_DIR = Path(__file__).parent.parent.parent / "dataset"
WEB_DIR = Path(__file__).parent.parent / "web" / "dist"

app = FastAPI()

# Serve dataset as static files
app.mount("/dataset", StaticFiles(directory=DATASET_DIR), name="dataset")
# Serve the Preact web UI (static build) at /web
app.mount("/web", StaticFiles(directory=WEB_DIR, html=True), name="web")

# Include routers
app.include_router(dataset_router)
app.include_router(web_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
