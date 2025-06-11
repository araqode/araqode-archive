# Dataset Server

## Setup

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```
2. Run the server:
   ```bash
   cd src/server
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

- The server exposes:
  - `/api/list?path=...` for browsing dataset files/folders
  - `/api/file?path=...` for downloading/previewing files
  - `/dataset/...` for static file serving
