import os
from dotenv import load_dotenv

load_dotenv()

# LLM Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Email Config (SendGrid)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "OnboardIQ by KONVERGE.AI")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Team Emails
HR_EMAIL = os.getenv("HR_EMAIL", "mohini@konverge.ai")
IT_EMAIL = os.getenv("IT_EMAIL", "sagar@konverge.ai")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@konverge.ai")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./onboardiq.db")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# RAG Config
RAG_DOCUMENTS_PATH = os.getenv("RAG_DOCUMENTS_PATH", "./documents")
RAG_PERSIST_DIR = os.getenv("RAG_PERSIST_DIR", "./chroma_db")
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
