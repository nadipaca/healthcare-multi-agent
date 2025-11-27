from google.cloud import documentai_v1 as documentai
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us")
PROCESSOR_ID = os.getenv("GCP_DOC_AI_PROCESSOR_ID")

def extract_text_from_file(file_path: str, content_type: str = None) -> str:
    """
    Extract text from file using Google Cloud Document AI
    
    Args:
        file_path: Path to the file
        content_type: MIME type of the file (e.g., 'application/pdf', 'image/jpeg')
    
    Returns:
        Extracted text or empty string if extraction fails
    """
    # Check if GCP is properly configured
    if not PROJECT_ID or not PROCESSOR_ID:
        print("WARNING: GCP Document AI not configured. Skipping OCR.")
        print(f"PROJECT_ID: {PROJECT_ID}, PROCESSOR_ID: {PROCESSOR_ID}")
        return ""
    
    try:
        # Auto-detect MIME type if not provided
        if not content_type:
            if file_path.lower().endswith('.pdf'):
                mime_type = "application/pdf"
            elif file_path.lower().endswith(('.jpg', '.jpeg')):
                mime_type = "image/jpeg"
            elif file_path.lower().endswith('.png'):
                mime_type = "image/png"
            elif file_path.lower().endswith('.heic'):
                mime_type = "image/heic"
            else:
                mime_type = "application/pdf"  # default
        else:
            mime_type = content_type
        
        client = documentai.DocumentProcessorServiceClient()
        name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

        with open(file_path, "rb") as f:
            content = f.read()

        raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        
        extracted_text = result.document.text or ""
        print(f"OCR Success: Extracted {len(extracted_text)} characters from {file_path}")
        return extracted_text
        
    except Exception as e:
        print(f"ERROR: OCR extraction failed for {file_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""
