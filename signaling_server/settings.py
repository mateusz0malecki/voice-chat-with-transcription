import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_JSON_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "scrapper-system-stt-sa.json")
