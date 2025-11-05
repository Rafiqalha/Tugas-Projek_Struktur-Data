import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

os.makedirs(DATA_DIR, exist_ok=True)

TASK_FILE = DATA_DIR / "task.json"
COMPLETED_FILE = DATA_DIR / "completed.json"

GOOGLE_CLIENT_SECRET = BASE_DIR / "credentials.json" 

GOOGLE_TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]

DEFAULT_CALENDAR_NAME = "Smart Scheduler"

DEADLINE_THRESHOLD = 6 * 3600  

QUADRANT_COLORS = {
    "Kuadran 1 (Tidak Penting & Tidak Mendesak)": "#A0A0A0",
    "Kuadran 2 (Tidak Penting tapi Mendesak)": "#F5A623",
    "Kuadran 3 (Penting tapi Tidak Mendesak)": "#4A90E2",
    "Kuadran 4 (Penting & Mendesak)": "#D0021B"
}
