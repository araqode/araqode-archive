import os
from .constants import LOCAL_DATA_DIR
from .utils import load_env, get_dataverse_api, ensure_local_dir
from .api import download_file as api_download_file

# --- Main Execution ---
def main():
    env = load_env()
    BASE_URL = env["DATAVERSE_BASE_URL"]
    API_TOKEN = env["DATAVERSE_API_TOKEN"]
    DATASET_PID = env["DATAVERSE_DATASET_PID"]
    api = get_dataverse_api(BASE_URL, API_TOKEN)
    ensure_local_dir(LOCAL_DATA_DIR)
    download_dataset(api, DATASET_PID, LOCAL_DATA_DIR)

# --- Helper Functions ---
def download_file(file_info, dest_dir, base_url, api_token):
    """
    Downloads a single file from Dataverse using its file id and saves it to dest_dir, preserving directory structure.
    """
    file_id = file_info.get('dataFile', {}).get('id')
    filename = file_info.get('dataFile', {}).get('filename')
    directory_label = file_info.get('directoryLabel', '')
    if not file_id or not filename:
        print(f"Skipping file with missing id or filename: {file_info}")
        return
    # Build local path
    local_dir = os.path.join(dest_dir, directory_label) if directory_label else dest_dir
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    print(f"Downloading: {filename} to {local_path} ...")
    try:
        api_download_file(base_url, api_token, file_id, local_path)
        print(f"Downloaded: {local_path}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

def download_dataset(api, dataset_pid, dest_dir):
    print(f"Fetching dataset metadata for {dataset_pid} ...")
    resp = api.get_dataset(dataset_pid)
    if resp.status_code != 200:
        print(f"Error fetching dataset: {resp.text}")
        return
    files = resp.json().get('data', {}).get('latestVersion', {}).get('files', [])
    if not files:
        print("No files found in dataset.")
        return
    print(f"Found {len(files)} files. Starting download...")
    for file_info in files:
        download_file(file_info, dest_dir, api.base_url, api.api_token)

if __name__ == "__main__":
    main()
