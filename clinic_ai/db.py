# db.py

import os
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(MONGO_URI)
db = client["clinic_db"]

patient_col = db["patients"]
slots_col = db["slots"]
appointments_col = db["appointments"]
intent_col = db["intent_vectors"]
doctors_col = db["doctors"]
chat_history_col = db["chat_history"]
