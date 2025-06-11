import requests

# Dataverse API helper methods

def delete_file(base_url, api_token, file_id):
    """Delete a file from Dataverse by file_id."""
    delete_url = f"{base_url}/api/files/{file_id}"
    headers = {"X-Dataverse-key": api_token}
    resp = requests.delete(delete_url, headers=headers)
    return resp

def download_file(base_url, api_token, file_id, dest_path):
    """Download a file from Dataverse by file_id to dest_path."""
    download_url = f"{base_url}/api/access/datafile/{file_id}"
    headers = {"X-Dataverse-key": api_token}
    with requests.get(download_url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return dest_path
