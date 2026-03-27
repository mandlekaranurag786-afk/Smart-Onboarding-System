from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY, GROQ_MODEL

def get_llm(temperature=0.0):
    """Get LLM instance for agents"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured in .env")
    
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=temperature
    )
