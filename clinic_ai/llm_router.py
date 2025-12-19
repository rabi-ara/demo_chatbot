# llm_router.py
# FASTAPI-SAFE, DETERMINISTIC, PRODUCTION-READY

from db import intent_col
from embeddings import embed_text, cosine_similarity

# --------------------------------
# Keyword Guards (HIGH PRIORITY)
# --------------------------------
BOOK_KEYWORDS = [
    "book",
    "book appointment",
    "schedule appointment",
    "schedule",
]

VIEW_KEYWORDS = [
    "view",
    "view appointment",
    "view my appointment",
    "my appointments",
    "show appointment",
]

CANCEL_KEYWORDS = [
    "cancel",
    "cancel appointment",
    "cancel my appointment",
    "delete appointment",
]

INTENT_THRESHOLD = 0.80


# --------------------------------
# Keyword Guard (Fast Path)
# --------------------------------
def keyword_guard(user_text: str) -> str | None:
    text = user_text.lower().strip()

    if any(k in text for k in BOOK_KEYWORDS):
        return "BOOK"

    if any(k in text for k in VIEW_KEYWORDS):
        return "VIEW"

    if any(k in text for k in CANCEL_KEYWORDS):
        return "CANCEL"

    return None


# --------------------------------
# Intent Detection (Keyword → Vector)
# --------------------------------
def detect_intent(user_text: str) -> str | None:
    # 1️⃣ Hard keyword match (NO embeddings cost)
    intent = keyword_guard(user_text)
    if intent:
        return intent

    # 2️⃣ Embedding-based similarity
    try:
        user_vec = embed_text(user_text)
    except Exception:
        return None

    best_intent = None
    best_score = 0.0

    for doc in intent_col.find({}, {"_id": 0}):
        score = cosine_similarity(user_vec, doc["vector"])
        if score > best_score:
            best_score = score
            best_intent = doc["intent"]

    # 3️⃣ Threshold gate (safety)
    if best_score < INTENT_THRESHOLD:
        return None

    return best_intent
