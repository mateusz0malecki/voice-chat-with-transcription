from google.cloud import storage
from functools import lru_cache
from settings import get_settings

app_settings = get_settings()

STORAGE_CREDENTIALS_FILE = app_settings.storage_credentials_file
BUCKET_NAME = app_settings.bucket_name


class StorageClient:
    """
    Class creates a client that connects to Cloud Storage Bucket and uploads new files.
    """
    def __init__(self, credentials_file, bucket_name):
        self._credentials_file = credentials_file
        self._bucket_name = bucket_name
        self._client = storage.Client.from_service_account_json(self._credentials_file)
        self._bucket = self._client.get_bucket(self._bucket_name)

    def upload(self, blob_name, path_to_file):
        blob = self._bucket.blob(blob_name)
        blob.upload_from_filename(path_to_file)

    def get_blob_uri(self, blob_name):
        blob = self._bucket.blob(blob_name)
        link = blob.path_helper(self._bucket_name, blob_name)
        gs_link = "gs://" + link
        return gs_link


@lru_cache
def get_client():
    return StorageClient(STORAGE_CREDENTIALS_FILE, BUCKET_NAME)
