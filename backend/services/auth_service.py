from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from config.config import JWT_SECRET_KEY
from services.database_service import create_user, find_user_by_email, get_public_user

TOKEN_TTL_DAYS = 7


def _create_token(user):
    payload = {
        "sub": user["email"],
        "name": user["name"],
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_TTL_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def signup_user(name, email, password):
    if find_user_by_email(email):
        raise ValueError("Account already exists")

    user = create_user(name, email, generate_password_hash(password))
    token = _create_token(user)
    return user, token


def login_user(email, password):
    stored_user = find_user_by_email(email)

    if not stored_user or not check_password_hash(stored_user["password_hash"], password):
        raise ValueError("Invalid credentials")

    user = get_public_user(email)
    token = _create_token(user)
    return user, token


def verify_token(token):
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    user = get_public_user(payload["sub"])
    if not user:
        raise ValueError("User not found")
    return user
