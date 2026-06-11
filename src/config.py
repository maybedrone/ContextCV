"""Configuration: environment, models, and tools."""
import os
from dotenv import load_dotenv
load_dotenv()  

# ── OBSERVABILITY ─────────────────────────────────────────────────────────────
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = "job-application-assistant"

from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchResults

# ── API KEY ───────────────────────────────────────────────────────────────────
# Loaded from environment. Set with: export GROQ_API_KEY="your_key"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── MODELS ────────────────────────────────────────────────────────────────────
# Small fast model for routing; swap worker to 70b for higher-quality output.
supervisor_llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
worker_llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
# worker_llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

# ── TOOLS ─────────────────────────────────────────────────────────────────────
search = DuckDuckGoSearchResults()
tools = [search]
researcher_llm = worker_llm.bind_tools(tools)