from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
from typing import Tuple
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "healthcare.db")

def _parse_gcs_uri(gcs_uri: str) -> Tuple[str, str]:
  """Split gs://bucket/path into (bucket, path)."""
  if not gcs_uri.startswith("gs://"):
    raise ValueError(f"Invalid GCS URI: {gcs_uri}")
  without_scheme = gcs_uri[len("gs://") :]
  parts = without_scheme.split("/", 1)
  if len(parts) != 2:
    raise ValueError(f"Invalid GCS URI: {gcs_uri}")
  return parts[0], parts[1]


def sync_gcs_with_db() -> None:
  """Remove DB rows whose GCS objects no longer exist.

  This keeps medical_documents and prescription_files consistent with the
  actual contents of the GCS bucket.
  """
  creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
  project_id = os.getenv("GCP_PROJECT_ID")
  if not creds_path:
    raise RuntimeError(
        "GOOGLE_APPLICATION_CREDENTIALS is not set; "
        "cannot create a Storage client for sync."
    )
  if not os.path.isabs(creds_path):
    creds_path = os.path.join(BASE_DIR, creds_path)

  # Build credentials from the service account JSON
  creds = service_account.Credentials.from_service_account_file(creds_path)

  # Create the storage client with explicit credentials
  client = storage.Client(project=project_id, credentials=creds)

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # medical_documents
  cursor.execute("PRAGMA table_info(medical_documents)")
  md_columns = [c[1] for c in cursor.fetchall()]
  has_md_gcs = "gcs_uri" in md_columns

  if has_md_gcs:
    cursor.execute(
        "SELECT document_id, gcs_uri FROM medical_documents WHERE gcs_uri IS NOT NULL"
    )
    rows = cursor.fetchall()
    for document_id, gcs_uri in rows:
      try:
        bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if not blob.exists():
          print(f"[SYNC] Removing medical_documents.document_id={document_id} (missing {gcs_uri})")
          cursor.execute(
              "DELETE FROM medical_documents WHERE document_id = ?",
              (document_id,),
          )
      except Exception as e:  # noqa: BLE001
        print(f"[SYNC] Error checking {gcs_uri}: {e}")

  # prescription_files
  cursor.execute("PRAGMA table_info(prescription_files)")
  pf_columns = [c[1] for c in cursor.fetchall()]
  has_pf_gcs = "gcs_uri" in pf_columns

  if has_pf_gcs:
    cursor.execute(
        "SELECT file_id, gcs_uri FROM prescription_files WHERE gcs_uri IS NOT NULL"
    )
    rows = cursor.fetchall()
    for file_id, gcs_uri in rows:
      try:
        bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if not blob.exists():
          print(f"[SYNC] Removing prescription_files.file_id={file_id} (missing {gcs_uri})")
          cursor.execute(
              "DELETE FROM prescription_files WHERE file_id = ?",
              (file_id,),
          )
      except Exception as e:  # noqa: BLE001
        print(f"[SYNC] Error checking {gcs_uri}: {e}")

  conn.commit()
  conn.close()


if __name__ == "__main__":
  sync_gcs_with_db()
