import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "DevOpsMind AI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "devopsmind.db")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing. Please configure .env")