import os
from dotenv import load_dotenv

load_dotenv()

# LLM Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Email Config
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM_ADDRESS")

# Team Emails
HR_EMAIL = os.getenv("HR_EMAIL", "mohini@konverge.ai")
IT_EMAIL = os.getenv("IT_EMAIL", "sagar@konverge.ai")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@konverge.ai")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./onboardiq.db")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
