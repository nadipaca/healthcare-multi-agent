from google.cloud import documentai_v1 as documentai
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us")
PROCESSOR_ID = os.getenv("GCP_DOC_AI_PROCESSOR_ID")

def extract_text_from_file(file_path: str) -> str:
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    with open(file_path, "rb") as f:
        content = f.read()

    raw_document = documentai.RawDocument(content=content, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    return result.document.text or ""
