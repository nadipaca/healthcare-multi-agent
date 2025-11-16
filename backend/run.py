import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Verify API key is loaded
if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in environment variables!")
    print(f"Looking for .env file at: {env_path}")
else:
    print(f"✓ GOOGLE_API_KEY loaded successfully")

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)