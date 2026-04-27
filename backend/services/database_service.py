from datetime import datetime, timezone
from uuid import uuid4

import certifi

from config.config import MONGO_DB_NAME, MONGO_URI

_memory_doubt_sessions = []
_memory_users = []
_memory_lectures = []

try:
    from pymongo import MongoClient

    if MONGO_URI:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,
            tls=True,
            tlsCAFile=certifi.where(),
        )
        client.admin.command("ping")
        db = client[MONGO_DB_NAME]
        doubt_sessions_collection = db["doubt_sessions"]
        users_collection = db["users"]
        lectures_collection = db["lectures"]
        users_collection.create_index("email", unique=True)
        print("MongoDB connected successfully")
    else:
        client = None
        db = None
        doubt_sessions_collection = None
        users_collection = None
        lectures_collection = None
        print("MongoDB URI not configured; using in-memory storage")
except Exception as e:
    client = None
    db = None
    doubt_sessions_collection = None
    users_collection = None
    lectures_collection = None
    print(f"MongoDB not available; using in-memory storage: {e}")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _clean_session(session):
    if not session:
        return None
    session = dict(session)
    session.pop("_id", None)
    return session


def _clean_record(record):
    if not record:
        return None
    record = dict(record)
    record.pop("_id", None)
    return record


def _public_user(user):
    user = _clean_record(user)
    if not user:
        return None
    user.pop("password_hash", None)
    return user


def find_user_by_email(email):
    normalized_email = email.lower().strip()
    if users_collection is not None:
        return _clean_record(users_collection.find_one({"email": normalized_email}))

    return next((user for user in _memory_users if user["email"] == normalized_email), None)


def create_user(name, email, password_hash):
    normalized_email = email.lower().strip()
    user = {
        "id": str(uuid4()),
        "name": name.strip(),
        "email": normalized_email,
        "password_hash": password_hash,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }

    if users_collection is not None:
        users_collection.insert_one(user)
        return _public_user(user)

    if find_user_by_email(normalized_email):
        raise ValueError("Account already exists")

    _memory_users.append(user)
    return _public_user(user)


def get_public_user(email):
    return _public_user(find_user_by_email(email))


def save_lecture_record(record):
    lecture = {
        "id": str(uuid4()),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        **record,
    }

    if lectures_collection is not None:
        lectures_collection.insert_one(lecture)
        return _clean_record(lecture)

    _memory_lectures.insert(0, lecture)
    return lecture


def list_lecture_records(user_email=None):
    if lectures_collection is not None:
        query = {"user_email": user_email} if user_email else {}
        lectures = lectures_collection.find(query).sort("created_at", -1)
        return [_clean_record(lecture) for lecture in lectures]

    lectures = _memory_lectures
    if user_email:
        lectures = [lecture for lecture in lectures if lecture.get("user_email") == user_email]
    return sorted(lectures, key=lambda lecture: lecture["created_at"], reverse=True)


def list_doubt_sessions(user_email=None):
    if doubt_sessions_collection is not None:
        query = {"user_email": user_email} if user_email else {}
        sessions = doubt_sessions_collection.find(query).sort("updated_at", -1)
        return [_clean_session(session) for session in sessions]

    sessions = _memory_doubt_sessions
    if user_email:
        sessions = [session for session in sessions if session.get("user_email") == user_email]
    return sorted(sessions, key=lambda session: session["updated_at"], reverse=True)


def create_doubt_session(title="New Doubt Session", user_email=None):
    session = {
        "id": str(uuid4()),
        "user_email": user_email,
        "title": title or "New Doubt Session",
        "last_message": "Session started",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "messages": [
            {
                "id": str(uuid4()),
                "sender": "mentor",
                "text": "Hello! I'm Shikshak. Ask me any doubt and I will help you understand it step by step.",
                "timestamp": _now_iso(),
            }
        ],
    }

    if doubt_sessions_collection is not None:
        doubt_sessions_collection.insert_one(session)
        return _clean_session(session)

    _memory_doubt_sessions.insert(0, session)
    return session


def get_doubt_session(session_id):
    if doubt_sessions_collection is not None:
        return _clean_session(doubt_sessions_collection.find_one({"id": session_id}))

    return next((session for session in _memory_doubt_sessions if session["id"] == session_id), None)


def add_doubt_messages(session_id, user_message, mentor_message):
    updated_at = _now_iso()
    messages = [
        {
            "id": str(uuid4()),
            "sender": "user",
            "text": user_message,
            "timestamp": updated_at,
        },
        {
            "id": str(uuid4()),
            "sender": "mentor",
            "text": mentor_message,
            "timestamp": _now_iso(),
        },
    ]

    if doubt_sessions_collection is not None:
        doubt_sessions_collection.update_one(
            {"id": session_id},
            {
                "$push": {"messages": {"$each": messages}},
                "$set": {
                    "last_message": user_message,
                    "updated_at": updated_at,
                },
            },
        )
        return get_doubt_session(session_id)

    session = get_doubt_session(session_id)
    if not session:
        return None

    session["messages"].extend(messages)
    session["last_message"] = user_message
    session["updated_at"] = updated_at
    return session
