import streamlit as st
import json
import os
from datetime import datetime
from scheduler import SmartScheduler, Task 
from google_auth import add_event_to_calendar

TASK_FILE = "data/task.json"
COMPLETED_FILE = "data/completed.json"

scheduler = SmartScheduler(storage_path=TASK_FILE)

st.title("Kalender Tugas Mahasiswa")
st.write("""
Aplikasi ini membantu kamu menentukan prioritas tugas berdasarkan:
         
1. Tidak penting & Tidak mendesak  
2. Mendesak tapi Tidak penting  
3. Penting tapi Tidak mendesak  
4. Penting & Mendesak
""")

st.subheader("Tambahkan Tugas Baru")

with st.form("add_task_form"):
    title = st.text_input("Judul Tugas")
    description = st.text_area("Deskripsi Tugas")
    
    col1, col2 = st.columns(2)
    deadline_date = col1.date_input("Tenggat Tanggal")
    deadline_time = col2.time_input("Tenggat Waktu")
    
    urgency_input = st.selectbox("Tingkat Mendesak", ["Tidak Mendesak", "Mendesak"])
    importance_input = st.selectbox("Tingkat Penting", ["Tidak Penting", "Penting"])
    
    submit_btn = st.form_submit_button("Tambah Tugas")

    if submit_btn:
        
        deadline = datetime.combine(deadline_date, deadline_time)
        
        importance_val = 2 if importance_input == "Penting" else 1
        urgency_val = 2 if urgency_input == "Mendesak" else 1

        try:
            new_task = Task(
                name=title,
                description=description,
                deadline=deadline.isoformat(),
                importance=importance_val,
                urgency=urgency_val
            )
            
            scheduler.add_task(new_task)
            st.success(f"Tugas '{title}' berhasil ditambahkan :)")
            
            try:
                start_time_iso = deadline.isoformat()
                add_event_to_calendar(
                    task_name=title,
                    start_time=start_time_iso,
                    duration_minutes=60,
                    description=description
                )
                st.info("Tugas juga sudah disinkronkan ke Google Calendar 📅")
            except Exception as e:
                st.warning(f"Gagal menambahkan ke Google Calendar: {e}")

            st.rerun()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat menambah tugas: {e}")


st.subheader("Daftar Tugas (Belum Selesai)")

pending_tasks = scheduler.list_tasks()

if not pending_tasks:
    st.write("Belum ada tugas yang ditambahkan.")
else:
    for task in pending_tasks:
        with st.expander(f"{task['name']} - ({task['quadrant']})"):
            st.write(f"**Deskripsi:** {task['description']}")
            st.write(f"**Deadline:** {datetime.fromisoformat(task['deadline']).strftime('%d %B %Y, %H:%M')}")
            st.write(f"**Prioritas:** {task['priority']}")

            # Tombol tandai selesai
            if st.button(f"Tandai '{task['name']}' Selesai", key=task['name']):
                scheduler.mark_task_completed(task['name'], COMPLETED_FILE)
                st.success(f"Tugas '{task['name']}' dipindahkan ke Selesai!")
                st.rerun()

st.subheader("Daftar Tugas (Sudah Selesai)")
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
st.subheader("Statistik Ringkas")
st.write(f"Tugas selesai: {len(completed_tasks)}")
st.write(f"Tugas belum selesai: {len(pending_tasks)}")