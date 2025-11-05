import os
import pickle
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ==========================================================
#                   KONFIGURASI GOOGLE API
# ==========================================================
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = "token.pkl"
CREDENTIALS_PATH = "credentials.json"  # pastikan file ini kamu download dari Google Cloud Console


# ==========================================================
#                   AUTENTIKASI GOOGLE
# ==========================================================
def get_calendar_service():
    """
    Autentikasi dan buat service Google Calendar API.
    - Gunakan token.pkl agar tidak login ulang setiap kali.
    - Jika token kedaluwarsa, otomatis refresh.
    """
    creds = None

    # Muat token lama jika tersedia
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # Jika belum ada atau token sudah tidak valid, login ulang
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Simpan token biar login sekali aja
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    # Buat service Calendar API
    service = build("calendar", "v3", credentials=creds)
    return service


# ==========================================================
#                FUNGSI UNTUK MENAMBAHKAN EVENT
# ==========================================================
def add_event_to_calendar(task_name, start_time, duration_minutes=60, description=""):
    """
    Tambahkan event ke Google Calendar.
    - task_name: nama kegiatan
    - start_time: string ISO (misal '2025-11-04T20:00:00')
    - duration_minutes: lama acara
    - description: catatan tambahan
    """
    service = get_calendar_service()
    start_datetime = datetime.fromisoformat(start_time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)

    event = {
        "summary": task_name,
        "description": description or "Dibuat otomatis oleh Smart Scheduler",
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Jakarta",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Jakarta",
        },
    }

    event_result = service.events().insert(calendarId="primary", body=event).execute()
    return event_result


# ==========================================================
#                   UJI COBA LANGSUNG
# ==========================================================
if __name__ == "__main__":
    print("🔑 Menguji koneksi ke Google Calendar...")
    event = add_event_to_calendar(
        task_name="Tes Smart Scheduler",
        start_time="2025-11-05T20:00:00",
        duration_minutes=45,
        description="Ini adalah event uji coba dari Smart Scheduler"
    )
    print("✅ Event berhasil dibuat:")
    print(f"📅 {event.get('summary')} - {event.get('htmlLink')}")
