# araqode-archive
# A curated, multi-modal dataset

import os
import json
import hashlib
import requests
from ratelimit import limits, sleep_and_retry
from pyDataverse.models import Datafile
from pyDataverse.api import NativeApi, DataAccessApi
from .constants import DATASET_DOWNLOAD_DIR, TMP_DIR
from .env import ensure_local_dir
from .logger import api_logger


class AraqodeArchiveAPI:
    """API class for interacting with the araqode-archive dataset."""

    # Throttle: 10 requests per second
    CALLS = 10
    PERIOD = 1

    @staticmethod
    @sleep_and_retry
    @limits(calls=CALLS, period=PERIOD)
    def __throttle():
        """Add throttling to limit API requests per second"""
        api_logger.debug("throttling...")

    native_api: NativeApi
    data_access_api: DataAccessApi
    dataset_doi: str

    dataset_info: dict | None = None

    def __init__(self, api_host, api_token, dataset_doi):
        """Initialize the API with host, token, and dataset DOI."""
        if not api_host or not api_token or not dataset_doi:
            raise EnvironmentError("Missing Dataverse API configuration.")

        self.native_api = NativeApi(f"https://{api_host}", api_token)
        self.data_access_api = DataAccessApi(f"https://{api_host}", api_token)
        self.dataset_doi = dataset_doi

        ensure_local_dir(DATASET_DOWNLOAD_DIR)
        ensure_local_dir(TMP_DIR)
    
    def __check_if_file_exists(self, local_file_path):
        """Check if a file already exists in the dataset info."""
        if self.dataset_info is None:
            self.__throttle()
            self.dataset_info = self.native_api.get_dataset(self.dataset_doi).json()

        filename = os.path.basename(local_file_path)
        directory_label = os.path.dirname(
            os.path.relpath(local_file_path, DATASET_DOWNLOAD_DIR)
        )
        remote_file_path = f"{directory_label}/{filename}"

        files = self.dataset_info.get('data', {}).get('latestVersion', {}).get('files', [])
        datafile = None
        for file_info in files:
            if file_info.get('dataFile', {}).get('filename') == filename and \
                file_info.get('directoryLabel', '') == directory_label:
                    datafile = file_info
                    break
        
        if datafile:
            api_logger.debug(f"File \"{local_file_path}\" as \"{remote_file_path}\" found in dataset {self.dataset_doi}.")
            return datafile
        else:
            api_logger.debug(f"File \"{local_file_path}\" as \"{remote_file_path}\" not found in dataset {self.dataset_doi}.")
            return None

    def __upload_file(self, local_file_path, description: str):
        """Upload a file to the dataset.

        This method creates a duplicate entry if the file already exists,
        Use the `upload_file` method instead for safer operations.
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File not found: {local_file_path}")

        filename = os.path.basename(local_file_path)
        directory_label = os.path.dirname(
            os.path.relpath(local_file_path, DATASET_DOWNLOAD_DIR)
        )
        remote_file_path = f"{directory_label}/{filename}"

        datafile = Datafile()
        datafile.set({
            "pid": self.dataset_doi,
            "filename": filename,
            "directoryLabel": directory_label,
            "description": description
        })

        self.__throttle()
        response = self.native_api.upload_datafile(
            self.dataset_doi,
            local_file_path,
            datafile.json()
        )

        if response.status_code != 200 and response.status_code != 201:
            # 200 OK or 201 Created
            raise Exception(f"Failed to upload file: {response.text}")

        response = response.json()

        # Update dataset info cache
        self.dataset_info.get('data', {}).get('latestVersion', {}).get('files', []).append(
            response.get('data', {}).get('files', [])[0]
        )

        api_logger.info(f"File \"{local_file_path}\" as \"{remote_file_path}\" uploaded to dataset {self.dataset_doi}.")
        return response

    def __replace_file(self, file_id, local_file_path, description: str):
        """Replace an existing file in the dataset.

        Use the `replace_file` method instead for safer operations.
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File not found: {local_file_path}")
        
        filename = os.path.basename(local_file_path)
        directory_label = os.path.dirname(
            os.path.relpath(local_file_path, DATASET_DOWNLOAD_DIR)
        )
        remote_file_path = f"{directory_label}/{filename}"

        datafile = Datafile()
        datafile.set({
            "pid": self.dataset_doi,
            "filename": filename,
            "directoryLabel": directory_label,
            "description": description
        })

        self.__throttle()
        response = self.native_api.replace_datafile(
            file_id,
            local_file_path,
            datafile.json(),
            is_filepid=False
        )

        if response.status_code != 200:
            raise Exception(f"Failed to replace file: {response.text}")

        response = response.json()

        # Update dataset info cache
        files = self.dataset_info.get('data', {}).get('latestVersion', {}).get('files', [])
        for i, file_info in enumerate(files):
            if file_info.get('dataFile', {}).get('id') == file_id:
                files[i] = response.get('data', {}).get('files', [])[0]
                break

        api_logger.info(f"File \"{local_file_path}\" as \"{remote_file_path}\" replaced in dataset {self.dataset_doi}.")
        return response

    def upload_file(self, local_file_path, description: str):
        """Upload a file to the dataset, checking for duplicates."""
        existing_file = self.__check_if_file_exists(local_file_path)

        if existing_file:
            md5_info = existing_file.get('dataFile', {}).get('md5', '')
            md5_hash = hashlib.md5(open(local_file_path, 'rb').read()).hexdigest()
            if md5_info == md5_hash:
                return {
                    "data": {
                        "files": [existing_file],
                    }
                }
            else:
                return self.__replace_file(
                    existing_file.get('dataFile', {}).get('id'),
                    local_file_path,
                    description
                )

        return self.__upload_file(local_file_path, description)
    
    def download_file(self, local_file_path):
        """Download a file from the dataset."""
        existing_file = self.__check_if_file_exists(local_file_path)
        if not existing_file:
            raise FileNotFoundError(f"File not found in dataset: {local_file_path}")

        if os.path.exists(local_file_path):
            md5_info = existing_file.get('dataFile', {}).get('md5', '')
            md5_hash = hashlib.md5(open(local_file_path, 'rb').read()).hexdigest()
            if md5_info == md5_hash:
                return  # File already exists and is up-to-date

        remote_file_path = f"{existing_file.get('directoryLabel', '')}/{existing_file.get('dataFile', {}).get('filename', '')}"

        file_id = existing_file.get('dataFile', {}).get('id')
        endpoint = f"{self.data_access_api.base_url_api}/access/datafile/{file_id}"
        headers = {
            "X-Dataverse-key": self.data_access_api.api_token,
        }

        ensure_local_dir(os.path.dirname(local_file_path))
        self.__throttle()
        with requests.get(endpoint, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(local_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        api_logger.info(f"File \"{local_file_path}\" as \"{remote_file_path}\" downloaded from dataset {self.dataset_doi}.")

    def replace_file(self, local_file_path, description: str):
        """Replace an existing file in the dataset."""
        existing_file = self.__check_if_file_exists(local_file_path)
        if not existing_file:
            return self.__upload_file(local_file_path, description)

        md5_info = existing_file.get('dataFile', {}).get('md5', '')
        md5_hash = hashlib.md5(open(local_file_path, 'rb').read()).hexdigest()
        if md5_info == md5_hash:
            return {
                "data": {
                    "files": [existing_file],
                }
            }

        file_id = existing_file.get('dataFile', {}).get('id')
        return self.__replace_file(file_id, local_file_path, description)

    def delete_file(self, local_file_path):
        """Delete a file from the dataset."""
        existing_file = self.__check_if_file_exists(local_file_path)
        if not existing_file:
            raise FileNotFoundError(f"File not found in dataset: {local_file_path}")

        remote_file_path = f"{existing_file.get('directoryLabel', '')}/{existing_file.get('dataFile', {}).get('filename', '')}"

        file_id = existing_file.get('dataFile', {}).get('id')
        endpoint = f"{self.native_api.base_url_api}/files/{file_id}"
        headers = {
            "X-Dataverse-key": self.native_api.api_token,
        }

        self.__throttle()
        response = requests.delete(endpoint, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to delete file: {response.text}")

        # Update dataset info cache
        files = self.dataset_info.get('data', {}).get('latestVersion', {}).get('files', [])
        self.dataset_info['data']['latestVersion']['files'] = [
            f for f in files if f.get('dataFile', {}).get('id') != file_id
        ]

        api_logger.info(f"File \"{local_file_path}\" as \"{remote_file_path}\" deleted from dataset {self.dataset_doi}.")
        return response.json()

    def sync_dataset(self, description: str, download_missing: bool = False, prune_remote: bool = False):
        """Sync the local dataset directory with the remote dataset.
        
        | download_missing | prune_remote | Action |
        |------------------|--------------|--------|
        | False            | False        | Do nothing |
        | False            | True         | Delete remote files not in local |
        | True             | False        | Download missing files from remote |
        | True             | True         | Download missing files from remote |
        """
        if self.dataset_info is None:
            self.__throttle()
            self.dataset_info = self.native_api.get_dataset(self.dataset_doi).json()

        local_files = {
            os.path.relpath(os.path.join(dp, f), DATASET_DOWNLOAD_DIR): {
                "filename": f,
                "directoryLabel": os.path.relpath(dp, DATASET_DOWNLOAD_DIR),
                "md5": '' # Lazy loading
            }
            for dp, dn, filenames in os.walk(DATASET_DOWNLOAD_DIR)
            for f in filenames
        }

        remote_files = {
            f"{file_info.get('directoryLabel', '')}/{file_info.get('dataFile', {}).get('filename', '')}": {
                "filename": file_info.get('dataFile', {}).get('filename'),
                "directoryLabel": file_info.get('directoryLabel', ''),
                "md5": file_info.get('dataFile', {}).get('md5')
            }
            for file_info in self.dataset_info.get('data', {}).get('latestVersion', {}).get('files', [])
        }

        api_logger.debug(f"Local files: {json.dumps(local_files, indent=2)}")
        api_logger.debug(f"Remote files: {json.dumps(remote_files, indent=2)}")

        # 1. Local files not in remote
        for local_path, local_file in local_files.items():
            if local_path not in remote_files:
                local_file_path = os.path.join(DATASET_DOWNLOAD_DIR, local_path)
                remote_file_path = f"{local_file['directoryLabel']}/{local_file['filename']}"
                api_logger.debug(f"Uploading new file: \"{local_file_path}\" as \"{remote_file_path}\"")
                self.upload_file(local_file_path, description=description)

        # 2. Remote files not in local
        for remote_path, remote_file in remote_files.items():
            if remote_path not in local_files:
                local_file_path = os.path.join(DATASET_DOWNLOAD_DIR, remote_path)
                remote_file_path = f"{remote_file['directoryLabel']}/{remote_file['filename']}"
                if download_missing:
                    api_logger.debug(f"Downloading missing file: \"{local_file_path}\" as \"{remote_file_path}\"")
                    self.download_file(local_file_path)
                elif prune_remote:
                    api_logger.debug(f"Deleting remote file not in local: \"{local_file_path}\" as \"{remote_file_path}\"")
                    self.delete_file(local_file_path)
                else:
                    api_logger.debug(f"Skipping remote file not in local: \"{local_file_path}\" as \"{remote_file_path}\"")

        # 3. Files present in both but different content
        for local_path, local_file in local_files.items():
            if local_path in remote_files:
                remote_file = remote_files[local_path]
                local_file['md5'] = hashlib.md5(open(os.path.join(DATASET_DOWNLOAD_DIR, local_path), 'rb').read()).hexdigest()
                if local_file['md5'] != remote_file['md5']:
                    local_file_path = os.path.join(DATASET_DOWNLOAD_DIR, local_path)
                    remote_file_path = f"{remote_file['directoryLabel']}/{remote_file['filename']}"
                    api_logger.debug(f"Replacing file with different content: \"{local_file_path}\" as \"{remote_file_path}\"")
                    self.replace_file(local_file_path, description=description)

        # 4. Files present in both and same content
        # No action needed, they are already in sync
