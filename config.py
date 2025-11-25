import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET = os.getenv("S3_BUCKET")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PORT = int(os.getenv("PORT", 5000))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static_uploads")
