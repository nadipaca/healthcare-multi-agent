from google.cloud import storage
import os
from typing import Optional
from datetime import timedelta

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

_client: Optional[storage.Client] = None

def get_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client()
    return _client

def upload_file_to_gcs(local_path: str, dest_path: str, content_type: Optional[str] = None) -> str:
    client = get_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(dest_path)
    blob.upload_from_filename(local_path, content_type=content_type)
    return f"gs://{BUCKET_NAME}/{dest_path}"

def generate_signed_url(gcs_uri: str, expires_minutes: int = 10) -> str:
    client = get_client()
    parts = gcs_uri.replace("gs://", "", 1).split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1]
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expires_minutes),
        method="GET",
    )
    return url