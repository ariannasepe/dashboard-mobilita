import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import carica_dati, COLORI, REGIONI, RIPARTIZIONI, PLOTLY_LAYOUT, SHARED_CSS, render_header, render_sidebar

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

df = carica_dati()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="nav-title">Filtri · Panoramica</span>', unsafe_allow_html=True)
    ripartizione_sel = st.selectbox("Ripartizione geografica",
        ["Tutta Italia", "Nord-Ovest", "Nord-Est", "Centro", "Sud", "Isole"])
    classificazione_sel = st.multiselect("Classificazione",
        ["attrattore", "emettitore", "equilibrato"],
        default=["attrattore", "emettitore", "equilibrato"])
    min_pop = st.slider("Popolazione minima", 0, 100_000, 0, step=1000, format="%d ab.")
    st.markdown("---")

# ── FILTRO ────────────────────────────────────────────────────────────────────
dff = df.copy()
if ripartizione_sel != "Tutta Italia":
    dff = dff[dff["ripartizione"] == ripartizione_sel]
if classificazione_sel:
    dff = dff[dff["classificazione"].isin(classificazione_sel)]
dff = dff[dff["POP21"] >= min_pop]

# ── HEADER ────────────────────────────────────────────────────────────────────
render_header("Panoramica nazionale", "Classificazione territoriale dei comuni italiani", ripartizione_sel)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if dff.empty:
    st.warning("⚠️ Nessun comune corrisponde ai filtri selezionati. Modifica i criteri nella sidebar.")
    st.stop()

# ── KPI — calcolo una sola volta ──────────────────────────────────────────────
n_attr  = (dff["classificazione"] == "attrattore").sum()
n_emit  = (dff["classificazione"] == "emettitore").sum()
n_equi  = (dff["classificazione"] == "equilibrato").sum()
n_tot   = max(len(dff), 1)
pct_attr = n_attr / n_tot * 100
pct_emit = n_emit / n_tot * 100
pct_equi = n_equi / n_tot * 100

k1, k2, k3, k4, k5, k6 = st.columns(6)
cards = [
    (k1, "#051186", "Comuni attrattori",  f"{n_attr:,}",  f"{pct_attr:.1f}% del totale"),
    (k2, "#00880D", "Comuni emettitori",  f"{n_emit:,}",  f"{pct_emit:.1f}% del totale"),
    (k3, "#C1C1C1", "Comuni equilibrati", f"{n_equi:,}",  f"{pct_equi:.1f}% del totale"),
    (k4, "#00649C", "Pendolari totali",   f"{dff['entrate'].sum()/1e6:.1f}M", "flussi in entrata aggregati"),
    (k5, "#4FC3F7", "Ind. attrattività",  f"{dff['indice_attrattivita'].mean():.3f}",
     f"max {dff['indice_attrattivita'].max():.2f}"),
    (k6, "#10a870", "Poli culturali",     f"{dff['n_poli_totali'].sum():,}",
     f"in {(dff['n_poli_totali']>0).sum():,} comuni"),
]
for col, color, label, value, sub in cards:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}; min-height:130px; height:130px;">
            <div class="top-bar" style="background:{color};"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color}; font-size:1.6rem;">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── RIGA 1: DONUT + SALDO DISTRIBUZIONE + SCATTER ────────────────────────────
c1, c2, c3 = st.columns([1.2, 1.5, 2])

with c1:
    st.markdown('<div class="section-label">COMPOSIZIONE</div>', unsafe_allow_html=True)
    counts = dff["classificazione"].value_counts()
    fig_donut = go.Figure()
    fig_donut.add_trace(go.Pie(
        labels=counts.index.tolist(),
        values=counts.values.tolist(),
        hole=0.6,
        marker=dict(
            colors=[COLORI.get(l, "#888") for l in counts.index],
            line=dict(color="#f4faff", width=2)
        ),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value:,} comuni (%{percent})<extra></extra>"
    ))
    layout_donut = copy.deepcopy(PLOTLY_LAYOUT)
    layout_donut.update(
        showlegend=True,
        legend=dict(orientation="h", x=0, y=-0.15, font=dict(size=10, color="#1a3a4f")),
        height=260,
        margin=dict(t=20, b=50, l=10, r=10),
        annotations=[dict(
            text=f"<b>{n_tot:,}</b><br><span style='font-size:10px'>comuni</span>",
            x=0.5, y=0.5, font=dict(size=12, color="#1a3a4f"),
            showarrow=False
        )]
    )
    fig_donut.update_layout(**layout_donut)
    st.plotly_chart(fig_donut, use_container_width=True)

with c2:
    st.markdown('<div class="section-label">DISTRIBUZIONE SALDO NETTO</div>', unsafe_allow_html=True)
    
    import numpy as np
    
    # Trasformazione log simmetrica: sign(x) * log10(|x| + 1)
    dff_hist = dff.copy()
    dff_hist["saldo_netto_log"] = np.sign(dff_hist["saldo_netto"]) * np.log10(np.abs(dff_hist["saldo_netto"]) + 1)
    
    fig_hist = px.histogram(
        dff_hist, x="saldo_netto_log", color="classificazione",
        color_discrete_map=COLORI, nbins=80,
        labels={"saldo_netto_log": "Saldo netto (log simmetrico)", "count": "N. comuni"},
        height=260
    )
    layout2 = copy.deepcopy(PLOTLY_LAYOUT)
    layout2.update(showlegend=False, bargap=0.05, margin=dict(t=10, b=40, l=40, r=50))
    fig_hist.update_layout(**layout2)
    
    # Linea a zero (pareggio)
    fig_hist.add_vline(x=0, line_dash="dash", line_color="#051186", line_width=1.5,
                       annotation_text="pareggio", annotation_position="top right",
                       annotation_font=dict(size=9, color="#051186"))
    
    # Linea media (trasformata)
    media_saldo_log = dff_hist["saldo_netto_log"].mean()
    media_saldo_raw = dff["saldo_netto"].mean()
    fig_hist.add_vline(x=media_saldo_log, line_dash="dot", line_color="#00880D", line_width=1.2,
                       annotation_text=f"media {media_saldo_raw:+.0f}",
                       annotation_position="top left",
                       annotation_font=dict(size=9, color="#00880D"))
    
    # Tick personalizzati: mostra valori reali sull'asse X
    tick_vals_raw = [-100000, -10000, -1000, -100, 0, 100, 1000, 10000, 100000]
    tick_vals_log = [np.sign(v) * np.log10(abs(v) + 1) for v in tick_vals_raw]
    tick_labels   = ["-100k", "-10k", "-1k", "-100", "0", "100", "1k", "10k", "100k"]
    
    fig_hist.update_xaxes(
        tickvals=tick_vals_log,
        ticktext=tick_labels,
        title_text="Saldo netto"
    )

    fig_hist.add_annotation(
    x=0.60, y=0.97, xref="paper", yref="paper",
    text="<b style='color:#051186'>■</b> attrattore &nbsp; <b style='color:#00880D'>■</b> emettitore",
    showarrow=False,
    font=dict(size=9, color="#1a3a4f"),
    align="left",
    bgcolor="rgba(255,255,255,0.7)",
    borderpad=4,
    xanchor="left", yanchor="top"
)
    
    st.plotly_chart(fig_hist, use_container_width=True)
    
with c3:
    st.markdown('<div class="section-label">ATTRATTIVITÀ VS POPOLAZIONE</div>', unsafe_allow_html=True)
    df_sc = dff[dff["POP21"] > 500].copy()
    # size minimo visibile anche per comuni senza poli
    df_sc["_size"] = df_sc["n_poli_totali"].clip(lower=1)
    fig_sc = px.scatter(
        df_sc, x="POP21", y="indice_attrattivita",
        color="classificazione", color_discrete_map=COLORI,
        size="_size", size_max=25,
        hover_name="COMUNE",
        hover_data={
            "POP21": ":.0f",
            "indice_attrattivita": ":.3f",
            "saldo_netto": False,
            "n_poli_totali": False,
            "classificazione": False,
            "_size": False,
        },
        log_x=True,
        labels={"POP21": "Popolazione (scala log)", "indice_attrattivita": "Indice attrattività"},
        height=260
    )
    layout3 = copy.deepcopy(PLOTLY_LAYOUT)
    layout3.update(showlegend=False, margin=dict(t=10, b=40, l=50, r=30))
    fig_sc.update_layout(**layout3)
    # linea orizzontale a indice = 1 (pareggio)
    fig_sc.add_hline(y=1, line_dash="dash", line_color="#C1C1C1", line_width=1,
                     annotation_text="indice = 1", annotation_position="bottom right",
                     annotation_font=dict(size=9, color="#C1C1C1"))
    st.plotly_chart(fig_sc, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── RIGA 2: ANALISI REGIONALE ─────────────────────────────────────────────────
st.markdown('<div class="section-label">ANALISI PER REGIONE</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Struttura territoriale delle regioni italiane</div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def aggrega_regionale(data_hash: int, _dff: pd.DataFrame) -> pd.DataFrame:
    reg = _dff.groupby("nome_regione").agg(
        attrattori  =("classificazione", lambda x: (x == "attrattore").sum()),
        emettitori  =("classificazione", lambda x: (x == "emettitore").sum()),
        equilibrati =("classificazione", lambda x: (x == "equilibrato").sum()),
        tot_comuni  =("Procom", "count"),
        poli        =("n_poli_totali", "sum"),
        ind_attr    =("indice_attrattivita", "mean"),
        int_cult    =("intensita_culturale", "mean"),
        saldo_medio =("saldo_netto", "mean"),
        pop_tot     =("POP21", "sum"),
    ).reset_index()
    reg["pct_attrattori"] = (reg["attrattori"] / reg["tot_comuni"] * 100).round(1)
    return reg

reg = aggrega_regionale(len(dff), dff)

cr1, cr2 = st.columns(2)

with cr1:
    reg_s = reg.sort_values("tot_comuni", ascending=True)
    fig_grouped = go.Figure()
    fig_grouped.add_trace(go.Bar(
        y=reg_s["nome_regione"], x=reg_s["attrattori"],
        name="Attrattori", orientation="h", marker_color="#051186",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Attrattori: %{x:,}<extra></extra>"
    ))
    fig_grouped.add_trace(go.Bar(
        y=reg_s["nome_regione"], x=reg_s["emettitori"],
        name="Emettitori", orientation="h", marker_color="#00880D",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Emettitori: %{x:,}<extra></extra>"
    ))
    fig_grouped.add_trace(go.Bar(
        y=reg_s["nome_regione"], x=reg_s["equilibrati"],
        name="Equilibrati", orientation="h", marker_color="#C1C1C1",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Equilibrati: %{x:,}<extra></extra>"
    ))
    layout_s = copy.deepcopy(PLOTLY_LAYOUT)
    layout_s.update(
        barmode="group", height=650,
        bargap=0.15, bargroupgap=0.05,
        margin=dict(t=50, b=30, l=150, r=20),
        legend=dict(orientation="h", y=1.04, x=0, font=dict(size=12, color="#1a3a4f")),
        xaxis_title="N. comuni",
    )
    fig_grouped.update_layout(**layout_s)
    st.plotly_chart(fig_grouped, use_container_width=True)

with cr2:
    fig_bubble = px.scatter(
        reg, x="pct_attrattori", y="poli",
        size="tot_comuni", color="ind_attr",
        hover_name="nome_regione",
        color_continuous_scale=["#b3dff5", "#051186"],
        size_max=40,
        custom_data=["saldo_medio", "tot_comuni", "equilibrati"],
        labels={
            "pct_attrattori": "% Comuni attrattori",
            "poli": "N. Poli culturali",
            "ind_attr": "Ind. attr. medio",
            "tot_comuni": "N. Comuni"
        },
        height=650
    )
    fig_bubble.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "% attrattori: %{x:.1f}%<br>"
            "Poli culturali: %{y:,}<br>"
            "Saldo medio: %{customdata[0]:+.0f}<br>"
            "Tot. comuni: %{customdata[1]:,}<br>"
            "Equilibrati: %{customdata[2]:,}<extra></extra>"
        )
    )
    layout_b = copy.deepcopy(PLOTLY_LAYOUT)
    layout_b.update(margin=dict(t=10, b=40, l=50, r=10))
    fig_bubble.update_layout(**layout_b)
    fig_bubble.update_coloraxes(colorbar=dict(
        tickfont=dict(color="#1a3a4f"),
        title=dict(font=dict(color="#1a3a4f"), text="Ind. attr.")
    ))
    st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── RIGA 3: TOP COMUNI ────────────────────────────────────────────────────────
st.markdown('<div class="section-label">CLASSIFICHE</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Top comuni per indicatore</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Saldo netto assoluto",
    "Indice attrattività",
    "Maggiori emettitori",
    "Intensità culturale",
])

def fmt_table(data: pd.DataFrame, cols: list, rename: list) -> pd.DataFrame:
    t = data[cols].copy().reset_index(drop=True)
    t.index += 1
    t.columns = rename
    return t

col_cfg_saldo = {
    "Saldo netto": st.column_config.NumberColumn(format="%+d"),
    "Entrate":     st.column_config.NumberColumn(format="%d"),
    "Uscite":      st.column_config.NumberColumn(format="%d"),
    "Popolazione": st.column_config.NumberColumn(format="%d"),
}

with tab1:
    top = (dff[dff["classificazione"] == "attrattore"]
           .sort_values("saldo_netto", ascending=False).head(20))
    st.dataframe(
        fmt_table(top,
            ["COMUNE", "nome_regione", "POP21", "saldo_netto", "entrate", "uscite", "n_poli_totali"],
            ["Comune", "Regione", "Popolazione", "Saldo netto", "Entrate", "Uscite", "Poli culturali"]),
        column_config=col_cfg_saldo,
        use_container_width=True, height=450
    )

with tab2:
    top2 = (dff[dff["classificazione"] == "attrattore"]
            .sort_values("indice_attrattivita", ascending=False).head(20))
    st.dataframe(
        fmt_table(top2,
            ["COMUNE", "nome_regione", "indice_attrattivita", "entrate", "POP21", "saldo_netto", "n_poli_totali"],
            ["Comune", "Regione", "Ind. attrattività", "Entrate", "Popolazione", "Saldo netto", "Poli culturali"]),
        column_config={
            "Ind. attrattività": st.column_config.NumberColumn(format="%.4f"),
            **col_cfg_saldo,
        },
        use_container_width=True, height=450
    )

with tab3:
    top3 = (dff[dff["classificazione"] == "emettitore"]
            .sort_values("saldo_netto").head(20))
    st.dataframe(
        fmt_table(top3,
            ["COMUNE", "nome_regione", "POP21", "saldo_netto", "entrate", "uscite", "n_poli_totali"],
            ["Comune", "Regione", "Popolazione", "Saldo netto", "Entrate", "Uscite", "Poli culturali"]),
        column_config=col_cfg_saldo,
        use_container_width=True, height=450
    )

with tab4:
    top4 = (dff[dff["uscite"] >= 200]
            .sort_values("intensita_culturale", ascending=False).head(20))
    st.dataframe(
        fmt_table(top4,
            ["COMUNE", "nome_regione", "intensita_culturale", "flussi_verso_cultura",
             "n_destinazioni_culturali", "n_poli_totali", "classificazione"],
            ["Comune", "Regione", "Intensità culturale", "Flussi verso cultura",
             "Destinazioni culturali", "Poli culturali", "Classificazione"]),
        column_config={
            "Intensità culturale": st.column_config.NumberColumn(format="%.4f"),
        },
        use_container_width=True, height=450
    )
