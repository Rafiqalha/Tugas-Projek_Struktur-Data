import os
from pathlib import Path

# ==========================================================
#               KONFIGURASI DASAR PROJECT
# ==========================================================

# Dapatkan direktori utama project secara dinamis
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder penyimpanan data
DATA_DIR = BASE_DIR / "data"

# Pastikan folder data ada
os.makedirs(DATA_DIR, exist_ok=True)

# ==========================================================
#                  FILE PENYIMPANAN TUGAS
# ==========================================================
TASK_FILE = DATA_DIR / "task.json"
COMPLETED_FILE = DATA_DIR / "completed.json"

# ==========================================================
#                  KONFIGURASI GOOGLE API
# ==========================================================
# File kredensial dari Google Cloud Console
GOOGLE_CLIENT_SECRET = BASE_DIR / "credentials.json"  # pastikan file ini ada

# Token hasil autentikasi (akan otomatis dibuat)
GOOGLE_TOKEN_FILE = BASE_DIR / "token.json"

# Scope akses Google Calendar
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]

# Nama kalender yang akan digunakan
DEFAULT_CALENDAR_NAME = "Smart Scheduler"

# ==========================================================
#               PENGATURAN APLIKASI TAMBAHAN
# ==========================================================
# Batas waktu maksimum sebelum tugas dianggap mendesak (detik)
DEADLINE_THRESHOLD = 6 * 3600  # 6 jam

# Warna default kuadran (bisa dipakai di UI)
QUADRANT_COLORS = {
    "Kuadran 1 (Tidak Penting & Tidak Mendesak)": "#A0A0A0",
    "Kuadran 2 (Tidak Penting tapi Mendesak)": "#F5A623",
    "Kuadran 3 (Penting tapi Tidak Mendesak)": "#4A90E2",
    "Kuadran 4 (Penting & Mendesak)": "#D0021B"
}
