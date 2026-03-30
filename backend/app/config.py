import os
from dotenv import load_dotenv

load_dotenv()


def _resolve_sqlite_url(raw_database_url: str, base_dir: str) -> str:
    """
    Resolve relative SQLite URLs against the backend directory.
    """
    if not raw_database_url.startswith("sqlite:///"):
        return raw_database_url

    sqlite_path = raw_database_url.replace("sqlite:///", "", 1)
    if os.path.isabs(sqlite_path):
        return raw_database_url

    resolved_path = os.path.abspath(os.path.join(base_dir, sqlite_path))
    return f"sqlite:///{resolved_path}"

# LLM Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Email Config (Mailgun)
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "OnboardIQ by KONVERGE.AI")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Team Emails
HR_EMAIL = os.getenv("HR_EMAIL", "mohini@konverge.ai")
IT_EMAIL = os.getenv("IT_EMAIL", "sagar@konverge.ai")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@konverge.ai")

# Database
# Use absolute path for SQLite to avoid creating multiple DBs in different directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = _resolve_sqlite_url(
    os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'onboardiq.db')}"),
    BASE_DIR
)

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# RAG Config
RAG_DOCUMENTS_PATH = os.getenv("RAG_DOCUMENTS_PATH", "./documents")
RAG_PERSIST_DIR = os.getenv("RAG_PERSIST_DIR", "./chroma_db")
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
