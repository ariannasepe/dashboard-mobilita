import pandas as pd
import streamlit as st

REGIONI = {
    1: "Piemonte", 2: "Valle d'Aosta", 3: "Lombardia",
    4: "Trentino-Alto Adige", 5: "Veneto", 6: "Friuli-Venezia Giulia",
    7: "Liguria", 8: "Emilia-Romagna", 9: "Toscana", 10: "Umbria",
    11: "Marche", 12: "Lazio", 13: "Abruzzo", 14: "Molise",
    15: "Campania", 16: "Puglia", 17: "Basilicata", 18: "Calabria",
    19: "Sicilia", 20: "Sardegna"
}

RIPARTIZIONI = {
    1: "Nord-Ovest", 2: "Nord-Ovest", 3: "Nord-Ovest", 7: "Nord-Ovest",
    4: "Nord-Est", 5: "Nord-Est", 6: "Nord-Est", 8: "Nord-Est",
    9: "Centro", 10: "Centro", 11: "Centro", 12: "Centro",
    13: "Sud", 14: "Sud", 15: "Sud", 16: "Sud", 17: "Sud", 18: "Sud",
    19: "Isole", 20: "Isole"
}

# ── TEMA CROMATICO ────────────────────────────────────────────────────────────
COLORI = {
    "attrattore":  "#051186",
    "emettitore":  "#00880D",
    "equilibrato": "#C1C1C1"
}

CHART_BG    = "#f4faff"
CHART_INNER = "#eaf4fc"
GRID_COLOR  = "#d6eaf6"
AXIS_COLOR  = "#a8cfe0"
TEXT_COLOR  = "#1a3a4f"
ACCENT      = "#4FC3F7"
CHART_FONT  = "Plus Jakarta Sans"

PLOTLY_LAYOUT = dict(
    plot_bgcolor  = CHART_INNER,
    paper_bgcolor = CHART_BG,
    font          = dict(family=CHART_FONT, color=TEXT_COLOR, size=13),
    xaxis         = dict(
        showgrid=False, zeroline=False, showline=True,
        linecolor=AXIS_COLOR, linewidth=1,
        tickfont=dict(size=12, color=TEXT_COLOR),
        title_font=dict(size=12, color=TEXT_COLOR),
    ),
    yaxis         = dict(
        showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
        zeroline=False, showline=False,
        tickfont=dict(size=12, color=TEXT_COLOR),
        title_font=dict(size=12, color=TEXT_COLOR),
    ),
    legend        = dict(
        orientation="h", yanchor="bottom", y=1.04,
        xanchor="left", x=0,
        font=dict(size=12, color=TEXT_COLOR),
        bgcolor="rgba(244,250,255,0.9)",
        bordercolor=AXIS_COLOR, borderwidth=1,
    ),
    hoverlabel    = dict(
        bgcolor="#1a3a4f", font_color="white",
        font_family=CHART_FONT, font_size=12, bordercolor="#1a3a4f"
    ),
    margin        = dict(t=30, b=40, l=55, r=20),
)

# ── CSS CONDIVISO ─────────────────────────────────────────────────────────────
SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
    --c-bg:         #4FC3F7;
    --c-surface:    #ffffff;
    --c-border:     #b3dff5;
    --c-text:       #222222;
    --c-muted:      #34465A;
    --c-attrattore: #2E86AB;
    --c-emettitore: #E85933;
    --c-equilibrato:#B0BEC5;
    --c-gold:       #25465D;
    --c-accent:     #4FC3F7;
    --c-blue:       #25465D;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
    background-color: var(--c-bg) !important;
    color: var(--c-text) !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
    background-color: #4FC3F7 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(175deg, #0d2d44 0%, #25465D 40%, #1a6a9a 80%, #4FC3F7 100%) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.2);
}
section[data-testid="stSidebar"] * {
    color: #e8f4fb !important;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
    margin: 1rem 0;
}
section[data-testid="stSidebar"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: #b3dff5 !important;
}

/* Sidebar slider */
section[data-testid="stSidebar"] div[data-testid="stSlider"] div[role="slider"] {
    background-color: #4FC3F7 !important;
    border-color: #4FC3F7 !important;
}

/* Sidebar multiselect */
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] > div > div {
    background-color: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: rgba(79,195,247,0.3) !important;
    border-radius: 6px !important;
}

/* Sidebar buttons */
div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    color: #e8f4fb !important;
    border-radius: 8px;
    font-size: 0.84rem;
    font-weight: 500;
    padding: 0.55rem 1rem;
    margin-bottom: 5px;
    transition: all 0.18s ease;
    text-align: left;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18);
    border-color: rgba(255,255,255,0.35);
    color: #ffffff !important;
    transform: translateX(2px);
}

/* Header nativo nascosto ma collapse button visibile */
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    display: none !important;
}
[data-testid="collapsedControl"] { display: flex !important; }

[data-testid="stSidebarCollapseButton"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebarCollapseButton"]::after {
    content: '◀';
    display: block !important;
    font-size: 0.9rem !important;
    color: #b3dff5 !important;
}

/* Main header */
.main-header {
    background: #ffffff;
    padding: 1.2rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.6rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.main-header img {
    width: 70px; height: 70px;
    object-fit: contain; flex-shrink: 0;
}
.main-header h1 {
    color: #25465D !important;
    font-size: 1.6rem; font-weight: 800;
    margin: 0 0 0.2rem 0; letter-spacing: -0.02em;
}
.main-header p { color: #555 !important; margin: 0; font-size: 0.82rem; }

/* Section labels */
.section-label {
    font-size: 0.63rem; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: #4FC3F7; margin-bottom: 0.2rem;
}
.section-title {
    font-size: 1.4rem; font-weight: 700;
    color: #25465D !important;
    margin: 0 0 1rem 0; letter-spacing: -0.01em;
}

/* KPI card */
.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    border-left: 4px solid #25465D;
    box-shadow: 0 4px 16px rgba(0,0,0,0.10);
    position: relative; overflow: hidden;
    min-height: 110px;
}
.kpi-card:hover {
    box-shadow: 0 8px 24px rgba(37,70,93,0.18) !important;
    transform: translateY(-2px);
    transition: all 0.2s ease;
    cursor: pointer;
}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] {
    position: static !important;
    opacity: 1 !important;
    display: inline-block !important;
    width: 100% !important;
    text-align: center !important;
    padding: 0.4rem 0.8rem !important;
    margin-top: 0.5rem !important;
    border-radius: 8px !important;
    background: #25465D !important;
    color: #ffffff !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    letter-spacing: 0.03em !important;
    transition: background 0.18s ease !important;
}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"]:hover {
    background: #1a6a9a !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    position: static !important;
    display: flex !important;
    opacity: 1 !important;
    width: 100% !important;
    padding: 0.5rem 1rem !important;
    border-radius: 8px !important;
    color: #e8f4fb !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    margin-bottom: 4px !important;
    transition: all 0.18s ease !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.3) !important;
    color: #ffffff !important;
    transform: translateX(2px) !important;
}
section[data-testid="stSidebar"] nav[data-testid="stSidebarNav"] {
    display: none !important;
}
.kpi-card .top-bar {
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.kpi-card .kpi-label {
    font-size: 0.63rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: #666; margin-bottom: 0.4rem;
}
.kpi-card .kpi-value {
    font-size: 2rem; font-weight: 800;
    color: #25465D; line-height: 1; margin-bottom: 0.25rem;
}
.kpi-card .kpi-sub {
    font-size: 0.73rem; color: #34465A; font-weight: 400;
}

/* Divider */
.divider {
    height: 1px; background: #b3dff5; margin: 1.5rem 0;
}

/* Info table */
.info-table {
    background: #ffffff;
    border: 1px solid #b3dff5;
    border-radius: 12px;
    padding: 1.2rem;
    font-size: 0.82rem;
    line-height: 2;
    color: #222222;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.info-table b { color: #25465D; }

/* Badge classificazione */
.badge-attrattore  { background:#dbeafe; color:#2E86AB; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; letter-spacing:1px; }
.badge-emettitore  { background:#fee2e2; color:#E85933; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; letter-spacing:1px; }
.badge-equilibrato { background:#f1f5f9; color:#607d8b; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; letter-spacing:1px; }

/* Nav title sidebar */
.nav-title {
    font-size: 0.6rem; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: #b3dff5 !important; margin-bottom: 0.5rem; display: block;
}

/* Selectbox nel main */
div[data-testid="stMainBlockContainer"] div[data-testid="stSelectbox"] > div > div {
    background-color: #ffffff !important;
    color: #111 !important;
    border: 1.5px solid #b3dff5 !important;
    border-radius: 8px !important;
}
div[data-testid="stMainBlockContainer"] div[data-testid="stSelectbox"] svg {
    fill: #25465D !important;
}

/* Insight box */
.insight-box {
    background: #ffffff;
    border: 1px solid #b3dff5;
    border-left: 3px solid #25465D;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    line-height: 1.6;
    color: #222222;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* Dataframe */
[data-testid="stDataFrame"] { background: #f4faff; border-radius: 12px; overflow: hidden; }

/* Grafici Plotly */
[data-testid="stPlotlyChart"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 18px rgba(37,70,93,0.10) !important;
    background: #f4faff !important;
}
[data-testid="stPlotlyChart"] > div {
    border-radius: 14px !important;
}
.js-plotly-plot, .plotly, .plot-container {
    border-radius: 14px !important;
}
</style>
"""


LOGO_B64 = "data:image/png;base64,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"

# ── LOGO HELPER ───────────────────────────────────────────────────────────────
import base64, os

def get_logo_b64(filename="logo.png"):
    """Restituisce il logo come data URI base64 (hardcoded, nessun file necessario)."""
    return LOGO_B64

def get_logo_tag(width=100, href="YOUR_LINK_HERE", style=""):
    """Restituisce il logo come tag <a> cliccabile con immagine base64."""
    base_style = (
        "margin-bottom:0.5rem;"
        "border-radius:50%;"
        "background:transparent;"
        "mix-blend-mode:lighten;"
        "display:block;"
    )
    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" style="display:inline-block;">'
        f'<img src="{LOGO_B64}" width="{width}" style="{base_style}{style}" />'
        f'</a>'
    )

def render_header(title: str, subtitle: str = "", detail: str = ""):
    logo_src = get_logo_b64()
    logo_tag = get_logo_tag(width=70, href="YOUR_LINK_HERE", style="border-radius:50%;mix-blend-mode:multiply;") if logo_src else ""
    sub_html = ""
    if subtitle or detail:
        parts = [p for p in [subtitle, detail] if p]
        sub_html = f'<p style="color:#555;font-size:0.82rem;margin:0;">{" &nbsp;·&nbsp; ".join(parts)}</p>'
    st.markdown(f"""
    <div class="main-header">
        {logo_tag}
        <div style="flex:1;">
            <p style="font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
                      color:#4FC3F7;margin:0 0 0.2rem 0;">Analisi dei flussi di mobilità territoriale e attrattività culturale in Italia</p>
            <h1 style="color:#25465D !important;font-size:1.6rem;font-weight:800;
                       margin:0 0 0.25rem 0;letter-spacing:-0.02em;">{title}</h1>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data
def carica_dati():
    df = pd.read_csv(
        "comuni_kpi_finale_reti.csv",
        dtype={"Procom": str}
    )
    df["nome_regione"] = df["COD_REG"].map(REGIONI)
    df["ripartizione"] = df["COD_REG"].map(RIPARTIZIONI)
    df["COMUNE"]       = df["COMUNE"].fillna("N/D")
    for col in ["n_archi_anas","km_rete_anas","ha_rete_anas",
                "n_postazioni_tgm","tgm_medio","tgm_max","ha_tgm",
                "n_stazioni_totali","n_stazioni","n_fermate","ha_stazione"]:
        if col not in df.columns:
            df[col] = 0
    return df

def render_sidebar():
    with st.sidebar:
        logo_src = get_logo_b64()
        if logo_src:
            st.markdown(get_logo_tag(width=100, href="YOUR_LINK_HERE"), unsafe_allow_html=True)
        st.markdown("## Analisi dei flussi di mobilità territoriale e attrattività culturale in Italia")
        st.markdown("---")
        st.markdown('<span class="nav-title">Sezioni</span>', unsafe_allow_html=True)
        st.page_link("app.py",                        label="  Home")
        st.page_link("pages/1_panoramica.py",         label="  Panoramica nazionale")
        st.page_link("pages/2_territoriale.py",       label="  Analisi territoriale")
        st.page_link("pages/3_cultura_mobilita.py",   label="  Cultura & Mobilità")
        st.page_link("pages/4_scheda_comune.py",      label="  Scheda comune")
        st.page_link("pages/5_mappa.py",              label="  Mappa interattiva")