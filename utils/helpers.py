import json
from datetime import datetime, timedelta
from pathlib import Path
from utils.constants import DEADLINE_THRESHOLD

def read_json(file_path: Path):
    """Membaca file JSON dan mengembalikan data (list atau dict)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_json(file_path: Path, data):
    """Menyimpan data (list/dict) ke file JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def format_datetime(dt: datetime) -> str:
    """Mengubah objek datetime menjadi string ISO standar."""
    return dt.isoformat(timespec="minutes")

def parse_datetime(dt_str: str) -> datetime:
    """Konversi string ISO ke objek datetime."""
    return datetime.fromisoformat(dt_str)

def time_remaining(deadline: datetime) -> str:
    """Hitung waktu tersisa sebelum deadline dalam format 'x jam y menit'."""
    now = datetime.now()
    delta = deadline - now

    if delta.total_seconds() < 0:
        return "Sudah lewat deadline"
    
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes = remainder // 60
    return f"{hours} jam {minutes} menit lagi"

def is_urgent(deadline: datetime) -> bool:
    """Menentukan apakah tugas sudah mendesak (kurang dari DEADLINE_THRESHOLD)."""
    return (deadline - datetime.now()).total_seconds() < DEADLINE_THRESHOLD

def determine_quadrant(importance: int, urgency: int) -> str:
    """Menentukan kuadran berdasarkan importance dan urgency."""
    if importance == 1 and urgency == 1:
        return "Kuadran 1 (Tidak Penting & Tidak Mendesak)"
    elif importance == 1 and urgency == 2:
        return "Kuadran 2 (Tidak Penting tapi Mendesak)"
    elif importance == 2 and urgency == 1:
        return "Kuadran 3 (Penting tapi Tidak Mendesak)"
    else:
        return "Kuadran 4 (Penting & Mendesak)"

def quadrant_color(quadrant: str) -> str:
    """Mengambil warna kuadran (akan diambil dari constants)."""
    from utils.constants import QUADRANT_COLORS
    return QUADRANT_COLORS.get(quadrant, "#CCCCCC")

def readable_date(dt_str: str) -> str:
    """Format tanggal ISO ke bentuk lebih ramah pembaca."""
    dt = parse_datetime(dt_str)
    return dt.strftime("%d %B %Y, %H:%M")
