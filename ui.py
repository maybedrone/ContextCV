"""UI helpers: inject custom CSS for ContextCV."""
from pathlib import Path
import streamlit as st

_CSS_PATH = Path(__file__).parent / ".streamlit" / "style.css"


def inject_css():
    try:
        css = _CSS_PATH.read_text()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS not found — styling not applied")  # temporary debug
