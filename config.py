import os
from dotenv import load_dotenv

load_dotenv()

# Google AI configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")

# Suno API configuration
SUNO_API_TOKEN = os.getenv("SUNO_API_TOKEN")
CREATE_TASK_URL = os.getenv("SUNO_CREATE_TASK_URL", "https://apibox.erweima.ai/api/v1/generate")
STATUS_URL = os.getenv("SUNO_STATUS_URL", "https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}")
STYLE_PROMPT = os.getenv("SUNO_STYLE_PROMPT", "Israeli Pop, High BPM, Drums, Beat, Techno")
CALLBACK_URL = os.getenv("SUNO_CALLBACK_URL", "")
DEFAULT_TITLE = os.getenv("SUNO_TITLE", "ORT ISRAEL")
