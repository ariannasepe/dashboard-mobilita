import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import SHARED_CSS, render_header, render_sidebar

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

render_header("Mappa interattiva", "Distribuzione territoriale dei comuni italiani")

tab_kepler1, tab_kepler2 = st.tabs(["Classificazione comuni", "Saldo netto"])

with tab_kepler1:
    components.iframe("https://timely-melba-1159fe.netlify.app/mappa.gl.html", height=650, scrolling=False)

with tab_kepler2:
    components.iframe("https://incandescent-pony-29622c.netlify.app/mappa_saldo.gl.html", height=650, scrolling=False)
