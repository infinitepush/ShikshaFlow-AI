import os
import secrets
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GENERATE_VIDEO = os.getenv("GENERATE_VIDEO", "false").lower() == "true"
MAX_VIDEO_SLIDES = int(os.getenv("MAX_VIDEO_SLIDES", "4"))
MAX_SLIDE_SECONDS = int(os.getenv("MAX_SLIDE_SECONDS", "8"))
GEMINI_MODELS = [
    model.strip()
    for model in os.getenv(
        "GEMINI_MODELS",
        "models/gemini-2.5-flash,models/gemini-2.5-flash-lite,models/gemini-2.0-flash,models/gemini-2.0-flash-lite,models/gemini-pro-latest",
    ).split(",")
    if model.strip()
]
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shikshaflow")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        os.getenv("FRONTEND_ORIGIN", "http://localhost:5173,http://localhost:5174"),
    ).split(",")
    if origin.strip()
]
