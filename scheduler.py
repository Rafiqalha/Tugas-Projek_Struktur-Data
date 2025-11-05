import heapq
import json
import os
from datetime import datetime, timedelta


# ===========================================================
#                  TASK CLASS
# ===========================================================
class Task:
    """
    Representasi satu tugas dalam Smart Task Scheduler.
    Menggunakan logika Eisenhower Matrix dinamis:
    - Penting & Mendesak         → Kuadran 4
    - Penting & Tidak Mendesak   → Kuadran 3
    - Tidak Penting & Mendesak   → Kuadran 2
    - Tidak Penting & Tidak Mendesak → Kuadran 1
    """

    def __init__(self, name, importance, urgency, deadline, description="", **kwargs):
        self.name = name
        self.description = description
        self.importance = int(importance)  # 1 = tidak penting, 2 = penting
        self.urgency = int(urgency)        # 1 = tidak mendesak, 2 = mendesak
        self.deadline = datetime.fromisoformat(deadline)
        self.priority = self.calculate_priority()
        self.quadrant = self.determine_quadrant()

    # ==============================
    # FUNGSI INTI PRIORITAS & KUADRAN
    # ==============================
    def calculate_priority(self):
        """
        Hitung prioritas berdasarkan kuadran dan kondisi waktu.
        Jika tugas penting (Q3) makin dekat deadline, otomatis naik ke Q4.
        """
        base_priority = (self.urgency * 2) + self.importance

        # Hitung waktu tersisa (dalam detik)
        time_left = (self.deadline - datetime.now()).total_seconds()

        # Jika penting tapi belum mendesak, dan sisa waktu < 6 jam → ubah jadi mendesak
        if self.importance == 2 and self.urgency == 1 and time_left < 21600:
            self.urgency = 2
            base_priority = (self.urgency * 2) + self.importance

        return base_priority

    def determine_quadrant(self):
        """Tentukan kuadran berdasarkan importance dan urgency."""
        if self.importance == 1 and self.urgency == 1:
            return "Kuadran 1 (Tidak Penting & Tidak Mendesak)"
        elif self.importance == 1 and self.urgency == 2:
            return "Kuadran 2 (Tidak Penting tapi Mendesak)"
        elif self.importance == 2 and self.urgency == 1:
            return "Kuadran 3 (Penting tapi Tidak Mendesak)"
        else:
            return "Kuadran 4 (Penting & Mendesak)"

    # ==============================
    # FUNGSI PENDUKUNG
    # ==============================
    def __lt__(self, other):
        """Agar bisa dibandingkan dalam heap (priority queue)."""
        return self.priority > other.priority  # prioritas tinggi duluan

    def to_dict(self):
        """Konversi ke dictionary (untuk JSON)."""
        return {
            "name": self.name,
            "description": self.description,
            "importance": self.importance,
            "urgency": self.urgency,
            "deadline": self.deadline.isoformat(),
            "priority": self.priority,
            "quadrant": self.quadrant
        }


# ===========================================================
#                  SMART SCHEDULER CLASS
# ===========================================================
class SmartScheduler:
    """
    Manajemen kumpulan tugas menggunakan struktur data Heap (Priority Queue).
    - Tambah tugas
    - Ambil tugas prioritas tertinggi
    - Simpan/muat data JSON
    """

    def __init__(self, storage_path="data/tasks.json"):
        self.tasks = []
        self.storage_path = storage_path

        # Pastikan folder data ada
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.load_tasks()

    # ------------------------------
    # OPERASI DASAR
    # ------------------------------
    def add_task(self, task):
        """Menambahkan task ke heap"""
        if not isinstance(task, Task):
            raise TypeError("Parameter 'task' harus berupa objek Task.")
        heapq.heappush(self.tasks, task)
        self.save_tasks()

    def pop_task(self):
        """Mengambil task dengan prioritas tertinggi"""
        if self.tasks:
            task = heapq.heappop(self.tasks)
            self.save_tasks()
            return task
        return None

    def list_tasks(self):
        """Tampilkan semua task dalam urutan prioritas"""
        return [t.to_dict() for t in sorted(self.tasks, reverse=True)]

# ... (kode lain di class SmartScheduler) ...

    def delete_task(self, name):
        """Hapus task berdasarkan nama"""
        self.tasks = [t for t in self.tasks if t.name != name]
        heapq.heapify(self.tasks)
        self.save_tasks()

    # ---- TAMBAHKAN FUNGSI DI BAWAH INI ----
    def mark_task_completed(self, name, completed_file_path):
        """
        Pindahkan task dari heap (pending) ke file completed.json.
        """
        task_to_complete = None
        # 1. Cari task di heap
        for t in self.tasks:
            if t.name == name:
                task_to_complete = t
                break
        
        if task_to_complete:
            # 2. Hapus dari heap
            self.tasks.remove(task_to_complete)
            heapq.heapify(self.tasks)
            self.save_tasks() # Simpan heap (pending) yang sudah berkurang
            
            # 3. Muat data completed.json
            try:
                with open(completed_file_path, "r") as f:
                    completed_list = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                completed_list = []
            
            # 4. Tambahkan task ke daftar selesai
            task_dict = task_to_complete.to_dict()
            task_dict["completed_at"] = datetime.now().isoformat()
            completed_list.append(task_dict)
            
            # 5. Simpan kembali ke completed.json
            with open(completed_file_path, "w") as f:
                json.dump(completed_list, f, indent=4)
        else:
            raise ValueError(f"Tugas dengan nama '{name}' tidak ditemukan.")
    # ----------------------------------------

    # ------------------------------
    # SIMPAN & MUAT DATA
    # ------------------------------
    # ... (sisa kode save_tasks dan load_tasks) ...

    # ------------------------------
    # SIMPAN & MUAT DATA
    # ------------------------------
    def save_tasks(self):
        """Simpan ke file JSON"""
        with open(self.storage_path, "w") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=4)

    def load_tasks(self):
        """Muat dari file JSON"""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.tasks = [Task(**task) for task in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []


# ===========================================================
#                   CONTOH PENGGUNAAN (Opsional)
# ===========================================================
if __name__ == "__main__":
    scheduler = SmartScheduler()

    # Contoh tugas (aktifkan untuk tes)
    # task1 = Task("Main game", 1, 1, "2025-11-04T21:00:00")
    # task2 = Task("Belanja tanggal kembar", 1, 2, "2025-11-11T09:00:00")
    # task3 = Task("Ngerjain tugas", 2, 1, "2025-11-04T23:00:00")

    # scheduler.add_task(task1)
    # scheduler.add_task(task2)
    # scheduler.add_task(task3)

    print("📋 Daftar Tugas Berdasarkan Prioritas:")
    for t in scheduler.list_tasks():
        print(f"- {t['name']} | {t['quadrant']} | Prioritas: {t['priority']}")
