
from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY, GROQ_MODEL


@lru_cache(maxsize=1)
def get_llm():

    llm = ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.2,
        max_retries=2
    )

    return llm
