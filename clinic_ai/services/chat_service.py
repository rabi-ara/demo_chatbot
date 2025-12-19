# services/chat_service.py
# STATE-AWARE VERSION (API READY, NO CLI, NO input())

from llm_router import detect_intent
from crud import (
    book_appointment,
    view_appointments,
    cancel_appointment,
    list_doctors,
)
from services.llm_service import chat_with_llm
from db import chat_history_col
from datetime import datetime

# --------------------------------
# In-memory session state (MVP)
# Later you can move this to Mongo
# --------------------------------
SESSION_STATE = {}


# --------------------------------
# Helpers
# --------------------------------
def save_message(session_id: str, role: str, message: str):
    chat_history_col.insert_one({
        "session_id": session_id,
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow()
    })


def get_state(session_id: str) -> dict:
    if session_id not in SESSION_STATE:
        SESSION_STATE[session_id] = {}
    return SESSION_STATE[session_id]


def clear_state(session_id: str):
    SESSION_STATE.pop(session_id, None)


# --------------------------------
# Main Chat Handler
# --------------------------------
def handle_message(session_id: str, user_input: str) -> dict:
    save_message(session_id, "user", user_input)

    state = get_state(session_id)

    # ----------------------------
    # STEP 1: Detect intent
    # ----------------------------
    intent = detect_intent(user_input)

    # ----------------------------
    # STEP 2: BOOK FLOW
    # ----------------------------
    if intent == "BOOK" or state.get("intent") == "BOOK":
        state["intent"] = "BOOK"

        if "patient_id" not in state:
            return reply_and_save(session_id, "Please provide patient id.", "BOOK")

        if "patient_name" not in state:
            return reply_and_save(session_id, "Please provide patient name.", "BOOK")

        if "patient_dob" not in state:
            return reply_and_save(session_id, "Please provide patient DOB (YYYY-MM-DD).", "BOOK")

        if "patient_sex" not in state:
            return reply_and_save(session_id, "Please provide patient sex (M/F).", "BOOK")

        if "date" not in state:
            return reply_and_save(session_id, "Please provide appointment date (YYYY-MM-DD).", "BOOK")

        if "doctor_id" not in state:
            doctors = list_doctors()
            doc_text = "\n".join(
                f"{d['doctor_id']} - {d['docname']} ({d['specialization']})"
                for d in doctors
            )
            return reply_and_save(
                session_id,
                f"Please select doctor id:\n{doc_text}",
                "BOOK"
            )

        if "time" not in state:
            return reply_and_save(session_id, "Please provide appointment time (HH:MM).", "BOOK")

        # All data collected → book
        result = book_appointment(
            patient_id=state["patient_id"],
            date=state["date"],
            time=state["time"],
            doctor_id=state["doctor_id"],
            patient_name=state["patient_name"],
            patient_dob=state["patient_dob"],
            patient_sex=state["patient_sex"],
        )

        clear_state(session_id)
        return reply_and_save(session_id, result, "BOOK")

    # ----------------------------
    # STEP 3: VIEW FLOW
    # ----------------------------
    if intent == "VIEW":
        state["intent"] = "VIEW"
        return reply_and_save(
            session_id,
            "Please provide patient id to view appointments.",
            "VIEW"
        )

    if state.get("intent") == "VIEW":
        result = view_appointments(int(user_input.strip()))
        clear_state(session_id)
        return reply_and_save(session_id, result, "VIEW")

    # ----------------------------
    # STEP 4: CANCEL FLOW
    # ----------------------------
    if intent == "CANCEL":
        state["intent"] = "CANCEL"
        return reply_and_save(
            session_id,
            "Please provide appointment id to cancel.",
            "CANCEL"
        )

    if state.get("intent") == "CANCEL":
        result = cancel_appointment(int(user_input.strip()))
        clear_state(session_id)
        return reply_and_save(session_id, result, "CANCEL")

    # ----------------------------
    # STEP 5: GENERAL CHAT
    # ----------------------------
    reply = chat_with_llm(user_input)
    save_message(session_id, "assistant", reply)

    return {
        "intent": "GENERAL",
        "reply": reply
    }


# --------------------------------
# Save + Return helper
# --------------------------------
def reply_and_save(session_id: str, reply: str, intent: str):
    save_message(session_id, "assistant", reply)
    return {
        "intent": intent,
        "reply": reply
    }
