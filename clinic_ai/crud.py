# crud.py  (API-SAFE VERSION – NO input(), FASTAPI READY)

from db import appointments_col, slots_col, patient_col, doctors_col

# ---------------- PATIENT ----------------
def get_or_create_patient(
    patient_id: int,
    name: str | None = None,
    dob: str | None = None,
    sex: str | None = None
):
    patient = patient_col.find_one({"patient_id": patient_id})
    if patient:
        return

    if not all([name, dob, sex]):
        raise ValueError("Patient details required for new patient")

    patient_col.insert_one({
        "patient_id": patient_id,
        "name": name.strip(),
        "dob": dob.strip(),
        "sex": sex.strip().upper()
    })


# ---------------- NORMALIZERS ----------------
def normalize_time(t: str) -> str:
    t = t.strip()
    if ":" not in t:
        return f"{t.zfill(2)}:00"
    return t


def normalize_date(d: str) -> str:
    return d.strip()


# ---------------- DOCTORS ----------------
def list_doctors():
    return list(doctors_col.find({}, {"_id": 0}))


def get_doctor_by_id(doctor_id: int):
    return doctors_col.find_one({"doctor_id": doctor_id})


# ---------------- BOOK ----------------
def book_appointment(
    patient_id: int,
    date: str,
    time: str,
    doctor_id: int,
    patient_name: str,
    patient_dob: str,
    patient_sex: str
):
    get_or_create_patient(
        patient_id,
        name=patient_name,
        dob=patient_dob,
        sex=patient_sex
    )

    date = normalize_date(date)
    time = normalize_time(time)

    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        return "Invalid doctor selected"

    if time not in doctor.get("available_time", []):
        return "Doctor not available at selected time"

    slot = slots_col.find_one({
        "appointment_date": date,
        "appointment_time": time,
        "is_available": True
    })

    if not slot:
        return "Slot not available"

    last = appointments_col.find_one(sort=[("appointment_id", -1)])
    appointment_id = 5001 if not last else last["appointment_id"] + 1

    appointments_col.insert_one({
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "doctor_name": doctor["docname"],
        "appointment_date": date,
        "appointment_time": time,
        "slot_id": slot["slot_id"],
        "status": "Scheduled"
    })

    slots_col.update_one(
        {"slot_id": slot["slot_id"]},
        {"$set": {"is_available": False}}
    )

    return f"Appointment booked successfully (ID: {appointment_id})"


# ---------------- VIEW ----------------
def view_appointments(patient_id: int):
    appts = list(
        appointments_col.find(
            {"patient_id": patient_id},
            {"_id": 0}
        )
    )

    if not appts:
        return "No appointments found"

    return appts


# ---------------- CANCEL ----------------
def cancel_appointment(appointment_id: int):
    appt = appointments_col.find_one({
        "appointment_id": appointment_id,
        "status": "Scheduled"
    })

    if not appt:
        return "Appointment not found"

    appointments_col.update_one(
        {"appointment_id": appointment_id},
        {"$set": {"status": "Cancelled"}}
    )

    slots_col.update_one(
        {"slot_id": appt["slot_id"]},
        {"$set": {"is_available": True}}
    )

    return "Appointment cancelled successfully"
