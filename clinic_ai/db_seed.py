from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient("mongodb://localhost:27017/")
db = client["clinic_db"]
db["patients"].drop()
db["slots"].drop()
db["appointments"].drop()

patients = [
    {"patient_id": 101, "name": "John Doe", "dob": "1990-05-15", "sex": "M"},
    {"patient_id": 102, "name": "Jane Smith", "dob": "1985-08-20", "sex": "F"},
]
db["patients"].insert_many(patients)
print("✅ Patients added (IDs: 101, 102).")

slots = []
start_date = datetime.now().date()
times = ["09:00", "10:00", "11:00","12:00","13:00" ,"14:00", "15:00","16:00","17:00"]

slot_counter = 1
for i in range(3): # Next 3 days
    current_date = start_date + timedelta(days=i)
    date_str = current_date.strftime("%Y-%m-%d")
    
    for time in times:
        slots.append({
            "slot_id": slot_counter,
            "appointment_date": date_str,
            "appointment_time": time,
            "is_available": True
        })
        slot_counter += 1

db["slots"].insert_many(slots)
print(f"✅ Created {len(slots)} available slots for the next 3 days.")