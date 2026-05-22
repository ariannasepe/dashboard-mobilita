import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import SHARED_CSS, render_header, render_sidebar

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

# ── HEADER ────────────────────────────────────────────────────────────────────
render_header("Mappa interattiva", "Classificazione e saldo netto dei comuni italiani")

# ── MAPPE KEPLER.GL ───────────────────────────────────────────────────────────
KEPLER_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_kepler_html(filename: str) -> str | None:
    """Carica il contenuto HTML di una mappa Kepler dal percorso della pagina."""
    path = os.path.join(KEPLER_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

tab_kepler1, tab_kepler2 = st.tabs(["Classificazione comuni", "Saldo netto"])

with tab_kepler1:
    html1 = _load_kepler_html("mappa.gl.html")
    if html1:
        components.html(html1, height=650, scrolling=False)
    else:
        st.warning(
            "File `mappa.gl.html` non trovato. "
            "Assicurati che sia nella stessa cartella di `5_mappa.py`."
        )

with tab_kepler2:
    html2 = _load_kepler_html("mappa_saldo.gl.html")
    if html2:
        components.html(html2, height=650, scrolling=False)
    else:
        st.warning(
            "File `mappa_saldo.gl.html` non trovato. "
            "Assicurati che sia nella stessa cartella di `5_mappa.py`."
        )