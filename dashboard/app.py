import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import SHARED_CSS, get_logo_b64, get_logo_tag

st.set_page_config(
    page_title="Analisi dei flussi di mobilità territoriale e attrattività culturale in Italia · Italia",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_src = get_logo_b64()
    if logo_src:
        st.markdown(get_logo_tag(width=100, href="https://sblconsultancy.it/"), unsafe_allow_html=True)
    st.markdown("## Analisi dei flussi di mobilità territoriale e attrattività culturale in Italia")
    st.markdown("---")
    st.markdown('<span class="nav-title">Sezioni</span>', unsafe_allow_html=True)
    st.page_link("app.py",                        label="Home")
    st.page_link("pages/1_panoramica.py",         label="Panoramica nazionale")
    st.page_link("pages/2_territoriale.py",       label="Analisi territoriale")
    st.page_link("pages/3_cultura_mobilita.py",   label="Cultura & Mobilità")
    st.page_link("pages/4_scheda_comune.py",      label="Scheda comune")
    st.page_link("pages/5_mappa.py",              label="Mappa interattiva")

# ── HERO ──────────────────────────────────────────────────────────────────────
logo_src = get_logo_b64()
logo_tag = f'<a href="https://sblconsultancy.it/" target="_blank" rel="noopener noreferrer"><img src="{logo_src}" style="width:100px;height:100px;object-fit:contain;flex-shrink:0;align-self:flex-start;margin-top:3.5rem;border-radius:50%;background:transparent;mix-blend-mode:lighten;" /></a>' if logo_src else ""

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #25465D 0%, #1a6a9a 60%, #4FC3F7 100%);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(37,70,93,0.18);
    display: flex;
    align-items: center;
    gap: 2rem;
">
    <div style="
        position: absolute; top: 0; right: 0;
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
        border-radius: 50%;
    "></div>
    {logo_tag}
    <div>
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:rgba(255,255,255,0.7); margin-bottom:0.8rem;">
            SISTEMA DI ANALISI TERRITORIALE · ITALIA
        </div>
        <h1 style="
            font-family:'Plus Jakarta Sans', sans-serif;
            font-size: 2.6rem;
            color: #ffffff;
            margin: 0 0 0.6rem 0;
            line-height: 1.1;
            font-weight: 800;
        ">Analisi dei flussi di mobilità territoriale<br><span style="font-weight:300;">e attrattività culturale in Italia</span></h1>
        <p style="color:rgba(255,255,255,0.75); font-size:0.9rem; font-weight:400; max-width:580px; line-height:1.7; margin:0.8rem 0 1.5rem 0;">
            Un'analisi multi-scala dei flussi di pendolarismo in relazione alla distribuzione 
            dei poli culturali sul territorio italiano. Ogni comune viene classificato come 
            attrattore, emettitore o equilibrato sulla base dei flussi ISTAT 2021.
        </p>
        <div style="display:flex; gap:2rem; flex-wrap:wrap;">
            <div style="text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#ffffff;">7.904</div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.65); letter-spacing:1px; text-transform:uppercase;">Comuni</div>
            </div>
            <div style="width:1px; background:rgba(255,255,255,0.2);"></div>
            <div style="text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#ffffff;">19,5M</div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.65); letter-spacing:1px; text-transform:uppercase;">Pendolari</div>
            </div>
            <div style="width:1px; background:rgba(255,255,255,0.2);"></div>
            <div style="text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#ffffff;">47.585</div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.65); letter-spacing:1px; text-transform:uppercase;">Poli culturali</div>
            </div>
            <div style="width:1px; background:rgba(255,255,255,0.2);"></div>
            <div style="text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#ffffff;">4</div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.65); letter-spacing:1px; text-transform:uppercase;">KPI territoriali</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CARDS SEZIONI ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">NAVIGA LA DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Seleziona una sezione</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
pages = [
    (c1, "Panoramica nazionale",  "#25465D", "Classificazione attrattori/emettitori, KPI sintetici, distribuzioni", "pages/1_panoramica.py"),
    (c2, "Analisi territoriale",  "#1a6a9a", "Esplora per regione, provincia e scala urbana", "pages/2_territoriale.py"),
    (c3, "Cultura & Mobilità",    "#00649C", "Relazione tra poli culturali e centralità dei flussi", "pages/3_cultura_mobilita.py"),
    (c4, "Scheda comune",         "#4FC3F7", "Approfondimento su singolo comune con tutti gli indicatori", "pages/4_scheda_comune.py"),
    (c5, "Mappa interattiva",     "#10a870", "Distribuzione geografica dei comuni attrattori ed emettitori", "pages/5_mappa.py"),

]
for col, title, color, desc, page in pages:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="min-height:140px; border-left-color:{color};">
            <div style="font-size:1rem; font-weight:700; color:{color}; margin-bottom:0.4rem;">{title}</div>
            <div style="font-size:0.75rem; color:#34465A; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(page, label="Vai alla sezione", use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with st.expander("Nota metodologica"):
    st.markdown("""
    ### Classificazione dei comuni
    
    Un comune è classificato come:
    - **Attrattore** → saldo netto positivo 
    - **Emettitore** → saldo netto negativo
    - **Equilibrato** → saldo netto pari a zero

    All'interno della dashboard il colore identifica la classificazione del comune: blu per gli attrattori, verde per gli emettitori, grigio per gli equilibrati.

    ### I 4 KPI territoriali
    - **Saldo netto mobilità per territorio**: differenza tra flussi in entrata e in uscita per ciascun comune, misura del peso attrattivo o emissivo del territorio.
    - **Indice di attrattività**: rapporto tra entrate e popolazione residente, normalizza il saldo rispetto alla dimensione demografica del comune.
    - **Intensità dei flussi verso territori culturali**: quota di flussi in uscita diretti verso comuni con almeno 1 polo culturale, misura quanto un territorio è orientato culturalmente nei suoi spostamenti.
    - **Numero di poli culturali in territori ad alta centralità**: conteggio dei poli culturali (musei, teatri, biblioteche, siti archeologici, monumenti, gallerie) presenti nei comuni classificati come attrattori.

    ### Fonti dati
    | Fonte | Descrizione | Anno |
    |---|---|---|
    | Matrice pendolarismo ISTAT | Flussi origine-destinazione per lavoro e studio | 2021 |
    | Confini amministrativi ISTAT | Geometrie comunali, provinciali e regionali | 2021 |
    | OpenStreetMap / Overpass API | Poli culturali sul territorio nazionale | 2026 |
    | OpenStreetMap / Overpass API | Caselli autostradali sul territorio nazionale | 2026 |
    | OpenStreetMap / Overpass API | Stazioni ferroviarie sul territorio nazionale | 2026 |
    | Rete ANAS | Archi stradali e km di rete stradale statale | 2015 |
    | TGM ANAS | Traffico Giornaliero Medio per postazione | 2015 |

    ### Elaborazione
    I dati sono stati elaborati in Python.
    La dashboard è realizzata con **Streamlit** e i grafici con **Plotly**.
    """)
        
