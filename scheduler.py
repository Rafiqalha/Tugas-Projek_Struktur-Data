import heapq
import json
import os
from datetime import datetime, timedelta

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
        self.importance = int(importance) 
        self.urgency = int(urgency)      
        self.deadline = datetime.fromisoformat(deadline)
        self.priority = self.calculate_priority()
        self.quadrant = self.determine_quadrant()

    def calculate_priority(self):
        """
        Hitung prioritas berdasarkan kuadran dan kondisi waktu.
        Jika tugas penting (Q3) makin dekat deadline, otomatis naik ke Q4.
        """
        base_priority = (self.urgency * 2) + self.importance

        time_left = (self.deadline - datetime.now()).total_seconds()

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

    def __lt__(self, other):
        """Agar bisa dibandingkan dalam heap (priority queue)."""
        return self.priority > other.priority 

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

        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.load_tasks()

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

    def delete_task(self, name):
        """Hapus task berdasarkan nama"""
        self.tasks = [t for t in self.tasks if t.name != name]
        heapq.heapify(self.tasks)
        self.save_tasks()

    def mark_task_completed(self, name, completed_file_path):
        """
        Pindahkan task dari heap (pending) ke file completed.json.
        """
        task_to_complete = None
        for t in self.tasks:
            if t.name == name:
                task_to_complete = t
                break
        
        if task_to_complete:
            self.tasks.remove(task_to_complete)
            heapq.heapify(self.tasks)
            self.save_tasks()
            try:
                with open(completed_file_path, "r") as f:
                    completed_list = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                completed_list = []

            task_dict = task_to_complete.to_dict()
            task_dict["completed_at"] = datetime.now().isoformat()
            completed_list.append(task_dict)
            
            with open(completed_file_path, "w") as f:
                json.dump(completed_list, f, indent=4)
        else:
            raise ValueError(f"Tugas dengan nama '{name}' tidak ditemukan.")

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

if __name__ == "__main__":
    scheduler = SmartScheduler()

    print("Daftar Tugas Berdasarkan Prioritas:")
    for t in scheduler.list_tasks():
        print(f"- {t['name']} | {t['quadrant']} | Prioritas: {t['priority']}")
