import streamlit as st
import json
import os
from datetime import datetime
# Impor Task dan SmartScheduler secara spesifik
from scheduler import SmartScheduler, Task 
from google_auth import add_event_to_calendar

# --- Inisialisasi SmartScheduler ---
# Tentukan path file dengan benar menggunakan constants.py
# (Ini praktik yang lebih baik, tapi untuk sekarang kita hardcode)
TASK_FILE = "data/task.json"
COMPLETED_FILE = "data/completed.json"

scheduler = SmartScheduler(storage_path=TASK_FILE)

# --- Judul dan Deskripsi ---
st.title("Kalender Tugas Mahasiswa")
st.write("""
Aplikasi ini membantu kamu menentukan prioritas tugas berdasarkan:
         
1️⃣ Tidak penting & Tidak mendesak  
2️⃣ Mendesak tapi Tidak penting  
3️⃣ Penting tapi Tidak mendesak  
4️⃣ Penting & Mendesak
""")

# --- Form input task baru ---
st.subheader("➕ Tambahkan Tugas Baru")

with st.form("add_task_form"):
    title = st.text_input("Judul Tugas")
    description = st.text_area("Deskripsi Tugas")
    
    # Ambil tanggal dan waktu
    col1, col2 = st.columns(2)
    deadline_date = col1.date_input("Tenggat Tanggal")
    deadline_time = col2.time_input("Tenggat Waktu")
    
    # Ambil nilai urgency/importance
    urgency_input = st.selectbox("Tingkat Mendesak", ["Tidak Mendesak", "Mendesak"])
    importance_input = st.selectbox("Tingkat Penting", ["Tidak Penting", "Penting"])
    
    submit_btn = st.form_submit_button("Tambah Tugas")

    if submit_btn:
        # --- PERBAIKAN ERROR 1 & 2 ---
        
        # 1. Gabungkan tanggal dan waktu
        deadline = datetime.combine(deadline_date, deadline_time)
        
        # 2. Petakan string ke integer (sesuai logika Task class)
        # "Tidak Penting" -> 1, "Penting" -> 2
        importance_val = 2 if importance_input == "Penting" else 1
        # "Tidak Mendesak" -> 1, "Mendesak" -> 2
        urgency_val = 2 if urgency_input == "Mendesak" else 1

        # 3. Buat objek Task
        try:
            new_task = Task(
                name=title,
                description=description,
                deadline=deadline.isoformat(), # Kirim sebagai string ISO
                importance=importance_val,
                urgency=urgency_val
            )
            
            # 4. Masukkan OBJEK Task ke scheduler
            scheduler.add_task(new_task)
            st.success(f"Tugas '{title}' berhasil ditambahkan ✅")
            
            # --- Tambahkan ke Google Calendar otomatis ---
            try:
                # Gunakan deadline yang sudah dalam format datetime
                start_time_iso = deadline.isoformat()
                
                # Perbaiki pemanggilan fungsi google_auth
                # Kita kirim start_time dan durasi (default 60 menit)
                add_event_to_calendar(
                    task_name=title,
                    start_time=start_time_iso,
                    duration_minutes=60, # Asumsi durasi 1 jam
                    description=description
                )
                st.info("Tugas juga sudah disinkronkan ke Google Calendar 📅")
            except Exception as e:
                st.warning(f"Gagal menambahkan ke Google Calendar: {e}")

            st.rerun() # Muat ulang halaman agar daftar update

        except Exception as e:
            st.error(f"Terjadi kesalahan saat menambah tugas: {e}")


# --- Menampilkan daftar tugas (Pending) ---
st.subheader("📋 Daftar Tugas (Belum Selesai)")

# list_tasks() mengembalikan daftar dictionary dari heap
pending_tasks = scheduler.list_tasks()

if not pending_tasks:
    st.write("Belum ada tugas yang ditambahkan.")
else:
    for task in pending_tasks:
        # --- PERBAIKAN ERROR 3 (KeyError) ---
        # Gunakan 'name' bukan 'title'
        # Hapus 'completed' karena ini semua PASTI belum selesai
        
        with st.expander(f"🗓️ {task['name']} - ({task['quadrant']})"):
            st.write(f"**Deskripsi:** {task['description']}")
            st.write(f"**Deadline:** {datetime.fromisoformat(task['deadline']).strftime('%d %B %Y, %H:%M')}")
            st.write(f"**Prioritas:** {task['priority']}")

            # Tombol tandai selesai
            if st.button(f"Tandai '{task['name']}' Selesai", key=task['name']):
                scheduler.mark_task_completed(task['name'], COMPLETED_FILE)
                st.success(f"Tugas '{task['name']}' dipindahkan ke Selesai!")
                st.rerun()

# --- Menampilkan daftar tugas (Selesai) ---
st.subheader("✅ Daftar Tugas (Sudah Selesai)")
try:
    with open(COMPLETED_FILE, "r") as f:
        completed_tasks = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    completed_tasks = []

if not completed_tasks:
    st.write("Belum ada tugas yang selesai.")
else:
    for task in completed_tasks:
        st.write(f"~~{task['name']}~~ (Selesai pada: {task.get('completed_at', 'N/A')})")


# --- Statistik ringkas ---
st.subheader("📊 Statistik Ringkas")
st.write(f"✅ Tugas selesai: {len(completed_tasks)}")
st.write(f"🕒 Tugas belum selesai: {len(pending_tasks)}")