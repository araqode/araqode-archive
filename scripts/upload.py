import os
from pyDataverse.models import Datafile
from scripts.api import delete_file
from scripts.constants import LOCAL_DATA_DIR
from scripts.utils import load_env, get_dataverse_api, ensure_local_dir

# --- Main Execution ---
def main():
    env = load_env()
    BASE_URL = env["DATAVERSE_BASE_URL"]
    API_TOKEN = env["DATAVERSE_API_TOKEN"]
    DATASET_PID = env["DATAVERSE_DATASET_PID"]
    REPO_NAME = env.get("REPO_NAME", "local script")
    api = get_dataverse_api(BASE_URL, API_TOKEN)
    ensure_local_dir(LOCAL_DATA_DIR)
    DATASET_FILES_CACHE = get_dataset_files_map(api, DATASET_PID)
    upload_directory(LOCAL_DATA_DIR, DATASET_PID, repo_name=REPO_NAME, files_cache=DATASET_FILES_CACHE, base_url=BASE_URL, api_token=API_TOKEN, api=api)

# --- Cache dataset files list ---
def get_dataset_files_map(api, dataset_pid):
    resp = api.get_dataset(dataset_pid)
    files_map = {}
    if resp.status_code == 200:
        files = resp.json().get('data', {}).get('latestVersion', {}).get('files', [])
        for file_info in files:
            f_name = file_info.get('dataFile', {}).get('filename')
            dir_label = file_info.get('directoryLabel', '')
            key = f"{dir_label}/{f_name}" if dir_label else f_name
            files_map[key] = file_info
    return files_map

# --- Helper Functions ---
def upload_file(local_file_path, dataset_pid, repo_name=None, files_cache=None, base_url=None, api_token=None, api=None):
    """
    Uploads a single file to the specified dataset using NativeApi and Datafile.
    If a file with the same name and directory exists, it will be deleted first (replace behavior).
    files_cache: dict of files in the dataset (cached)
    """
    if not os.path.exists(local_file_path):
        print(f"Error: File not found at {local_file_path}")
        return

    relative_path = os.path.relpath(local_file_path, LOCAL_DATA_DIR)
    remote_file_name = relative_path.replace("\\", "/")
    directory_label = os.path.dirname(remote_file_name)
    filename = os.path.basename(local_file_path)
    key = f"{directory_label}/{filename}" if directory_label else filename

    # Use cached files map
    if files_cache is not None and key in files_cache:
        file_info = files_cache[key]
        file_id = file_info.get('dataFile', {}).get('id')
        print(f"Existing file found: {key} (id={file_id}), deleting...")
        del_resp = delete_file(base_url, api_token, file_id)
        if del_resp.status_code == 200:
            print(f"Deleted existing file: {key}")
            del files_cache[key]
        else:
            print(f"Failed to delete existing file: {key} (status: {del_resp.status_code}) - {del_resp.text}")

    df = Datafile()
    df.set({
        "pid": dataset_pid,
        "filename": filename,
        "directoryLabel": directory_label,
        "description": f"Uploaded from {repo_name or 'local script'}."
    })
    print(f"Uploading: {local_file_path} as {remote_file_name}...")
    try:
        resp = api.upload_datafile(dataset_pid, local_file_path, df.json())
        resp.raise_for_status()
        print(f"Uploaded: {local_file_path} (Dataverse response: {resp.json()})")
        # Add new file to cache (simulate minimal info)
        if files_cache is not None:
            files_cache[key] = {
                'dataFile': {'filename': filename, 'id': None},
                'directoryLabel': directory_label
            }
    except Exception as e:
        print(f"Error uploading {local_file_path}: {e}")

def upload_files_from_list(file_paths, dataset_pid, repo_name=None, files_cache=None, base_url=None, api_token=None, api=None):
    for f_path in file_paths:
        upload_file(f_path, dataset_pid, repo_name=repo_name, files_cache=files_cache, base_url=base_url, api_token=api_token, api=api)

def upload_directory(local_directory_path, dataset_pid, repo_name=None, files_cache=None, base_url=None, api_token=None, api=None):
    if not os.path.isdir(local_directory_path):
        print(f"Error: Directory not found at {local_directory_path}")
        return
    print(f"Uploading directory: {local_directory_path}...")
    for root, _, files in os.walk(local_directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            upload_file(file_path, dataset_pid, repo_name=repo_name, files_cache=files_cache, base_url=base_url, api_token=api_token, api=api)

# --- Main Execution ---
if __name__ == "__main__":
    main()