# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── System deps (minimal) ─────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps (cached layer) ────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── App code ──────────────────────────────────────────────────────────────────
COPY . .

# ── Streamlit config ──────────────────────────────────────────────────────────
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# ── Run ───────────────────────────────────────────────────────────────────────
CMD ["streamlit", "run", "streamlit_app.py"]
