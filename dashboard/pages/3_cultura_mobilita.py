import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import carica_dati, COLORI, PLOTLY_LAYOUT, SHARED_CSS, render_header, render_sidebar

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

df = carica_dati()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="nav-title">Filtri · Cultura & Mobilità</span>', unsafe_allow_html=True)
    soglia_poli = st.select_slider(
        "Soglia 'territorio culturale'",
        options=[1, 2, 5, 10, 20, 50], value=5,
        help="Numero minimo di poli per definire un territorio culturale"
    )
    regione_filtro = st.selectbox("Regione (opzionale)", ["Tutte"] + sorted(df["nome_regione"].dropna().unique()))
    min_uscite = st.slider("Uscite minime (pendolari)", 0, 5000, 100, step=100)

dff = df.copy()
if regione_filtro != "Tutte":
    dff = dff[dff["nome_regione"] == regione_filtro]
dff = dff[dff["uscite"] >= min_uscite]

n_culturali = (dff["n_poli_totali"] >= soglia_poli).sum()
flussi_verso = dff["flussi_verso_cultura"].sum()
pct_flussi   = flussi_verso / dff["uscite"].sum() * 100 if dff["uscite"].sum() > 0 else 0

# ── HEADER ────────────────────────────────────────────────────────────────────
render_header("Cultura & Mobilità", "Relazione tra flussi di pendolarismo e poli culturali")

# ── KPI ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
for col, color, label, val, sub in [
    (k1, "#25465D", "Territori culturali",  f"{n_culturali:,}",                  f"comuni con ≥{soglia_poli} poli"),
    (k2, "#4FC3F7", "Flussi verso cultura", f"{flussi_verso/1e6:.2f}M",           f"{pct_flussi:.1f}% del totale"),
    (k3, "#10a870", "Int. culturale media", f"{dff['intensita_culturale'].mean():.3f}", "quota flussi verso cultura"),
    (k4, "#7B5EA7", "Dest. culturali medie",f"{dff['n_destinazioni_culturali'].mean():.1f}", "comuni cult. distinti raggiunti"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card" style="border-left-color:{color};">
            <div class="top-bar" style="background:{color};"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color};">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── RIGA 1: SCATTER + BOX ─────────────────────────────────────────────────────
c1, c2 = st.columns([3, 2])

with c1:
    fig_main = px.scatter(
        dff, x="intensita_culturale", y="saldo_netto",
        color="classificazione", color_discrete_map=COLORI,
        size="n_poli_totali", size_max=35,
        hover_name="COMUNE",
        hover_data={
            "intensita_culturale": ":.3f", "saldo_netto": ":,",
            "n_poli_totali": True, "n_destinazioni_culturali": True,
            "indice_attrattivita": ":.3f", "classificazione": False, "nome_regione": True
        },
        labels={
            "intensita_culturale": "Intensità culturale (quota flussi → cultura)",
            "saldo_netto": "Saldo netto mobilità",
            "n_poli_totali": "N. poli culturali", "nome_regione": "Regione"
        },
        height=420
    )
    layout1 = copy.deepcopy(PLOTLY_LAYOUT)
    layout1.update(margin=dict(t=10, b=40, l=50, r=20))
    fig_main.update_layout(**layout1)
    fig_main.add_hline(y=0, line_dash="dash", line_color="#25465D", line_width=1, opacity=0.5)
    fig_main.add_vline(x=dff["intensita_culturale"].median(),
                       line_dash="dot", line_color="#4FC3F7", line_width=1, opacity=0.5)
    st.plotly_chart(fig_main, use_container_width=True)

with c2:
    fig_box = go.Figure()
    for cls in ["emettitore", "attrattore", "equilibrato"]:
        vals = dff[dff["classificazione"] == cls]["intensita_culturale"].dropna()
        fig_box.add_trace(go.Box(
            y=vals, name=cls,
            marker_color=COLORI.get(cls, "#888"),
            boxpoints=False,
            hovertemplate=(
    "<b>%{x}</b><br>"
    "Mediana: %{median:.3f}<extra></extra>"
    )
    layout_box = copy.deepcopy(PLOTLY_LAYOUT)
    layout_box.update(showlegend=False, height=200, margin=dict(t=40, b=30, l=40, r=40))
    fig_box.update_layout(**layout_box)
    fig_box.update_layout(yaxis_title="Intensità culturale", xaxis_title="")
    fig_box.update_xaxes(tickfont_color="#1a3a4f", title_font_color="#1a3a4f", title_font_size=12)
    fig_box.update_yaxes(tickfont_color="#1a3a4f", title_font_color="#1a3a4f", title_font_size=12)
    st.plotly_chart(fig_box, use_container_width=True)

    df_scatter2 = dff[dff["n_poli_totali"] > 0]
    fig_sc2 = px.scatter(
        df_scatter2, x="indice_attrattivita", y="n_poli_totali",
        color="classificazione", color_discrete_map=COLORI,
        hover_name="COMUNE", log_y=True,
        labels={"indice_attrattivita": "Indice attrattività", "n_poli_totali": "N. poli (log)"},
        height=200
    )
    layout_sc2 = copy.deepcopy(PLOTLY_LAYOUT)
    layout_sc2.update(showlegend=False, margin=dict(t=5, b=40, l=50, r=10))
    fig_sc2.update_layout(**layout_sc2)
    st.plotly_chart(fig_sc2, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── RIGA 2: SENSIBILITÀ SOGLIA ────────────────────────────────────────────────
st.markdown('<div class="section-label">SENSIBILITÀ ALLA SOGLIA CULTURALE</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Come cambia la quota di flussi verso cultura al variare della soglia</div>', unsafe_allow_html=True)

soglie = [1, 2, 5, 10, 20, 50, 100]
risultati = []
for s in soglie:
    n_c = (df["n_poli_totali"] >= s).sum()
    if s == 1:
        fl  = dff["flussi_verso_cultura"].sum()
        tot = dff["uscite"].sum()
    else:
        fl_ratio = n_c / max((df["n_poli_totali"] >= 1).sum(), 1)
        fl  = dff["flussi_verso_cultura"].sum() * fl_ratio
        tot = dff["uscite"].sum()
    risultati.append({
        "Soglia": f"≥{s}",
        "N. comuni culturali": n_c,
        "% flussi verso cultura": round(fl / tot * 100, 1) if tot > 0 else 0
    })

df_soglie = pd.DataFrame(risultati)
c1, c2 = st.columns(2)

with c1:
    fig_s1 = px.bar(df_soglie, x="Soglia", y="N. comuni culturali",
        color="N. comuni culturali",
        color_continuous_scale=["#b3dff5", "#25465D"],
        height=280, labels={"Soglia": "Soglia min. poli", "N. comuni culturali": "N. comuni"})
    layout_s1 = copy.deepcopy(PLOTLY_LAYOUT)
    layout_s1.update(coloraxis_showscale=False, margin=dict(t=10, b=40, l=50, r=10))
    fig_s1.update_layout(**layout_s1)
    st.plotly_chart(fig_s1, use_container_width=True)

with c2:
    fig_s2 = px.line(df_soglie, x="Soglia", y="% flussi verso cultura",
        markers=True, height=280,
        labels={"Soglia": "Soglia min. poli", "% flussi verso cultura": "% flussi verso cultura"})
    layout_s2 = copy.deepcopy(PLOTLY_LAYOUT)
    layout_s2.update(margin=dict(t=10, b=40, l=50, r=10))
    fig_s2.update_layout(**layout_s2)
    fig_s2.update_traces(line_color="#25465D", marker_color="#4FC3F7")
    st.plotly_chart(fig_s2, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── RIGA 3: QUADRANTI ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">PROFILI TERRITORIO</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Quattro quadranti della relazione cultura-mobilità</div>', unsafe_allow_html=True)

med_int  = dff["intensita_culturale"].median()
med_attr = dff["indice_attrattivita"].median()

def quadrante(row):
    if row["intensita_culturale"] >= med_int and row["indice_attrattivita"] >= med_attr:
        return "Alta attrattività + Alta int. culturale"
    elif row["intensita_culturale"] < med_int and row["indice_attrattivita"] >= med_attr:
        return "Alta attrattività + Bassa int. culturale"
    elif row["intensita_culturale"] >= med_int and row["indice_attrattivita"] < med_attr:
        return "Bassa attrattività + Alta int. culturale"
    else:
        return "Bassa attrattività + Bassa int. culturale"

dff = dff.copy()
dff["quadrante"] = dff.apply(quadrante, axis=1)

colori_q = {
    "Alta attrattività + Alta int. culturale":   "#10a870",
    "Alta attrattività + Bassa int. culturale":  "#25465D",
    "Bassa attrattività + Alta int. culturale":  "#4FC3F7",
    "Bassa attrattività + Bassa int. culturale": "#b3dff5"
}

fig_q = px.scatter(
    dff[dff["uscite"] >= 200],
    x="intensita_culturale", y="indice_attrattivita",
    color="quadrante", color_discrete_map=colori_q,
    size="n_poli_totali", size_max=30,
    hover_name="COMUNE",
    hover_data={"intensita_culturale": ":.3f", "indice_attrattivita": ":.3f",
                "n_poli_totali": True, "quadrante": False, "nome_regione": True},
    labels={"intensita_culturale": "Intensità culturale",
            "indice_attrattivita": "Indice attrattività"},
    height=460
)
layout_q = copy.deepcopy(PLOTLY_LAYOUT)
layout_q.update(margin=dict(t=10, b=80, l=50, r=20),
                legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=10, color="#1a3a4f")))
fig_q.update_layout(**layout_q)
fig_q.add_hline(y=med_attr, line_dash="dot", line_color="#b3dff5", line_width=1)
fig_q.add_vline(x=med_int,  line_dash="dot", line_color="#b3dff5", line_width=1)
st.plotly_chart(fig_q, use_container_width=True)

counts_q = dff.groupby("quadrante").agg(
    n_comuni=("Procom", "count"),
    poli_medi=("n_poli_totali", "mean"),
    ind_attr_medio=("indice_attrattivita", "mean")
).reset_index()
counts_q["poli_medi"] = counts_q["poli_medi"].round(1)
counts_q["ind_attr_medio"] = counts_q["ind_attr_medio"].round(3)
counts_q.columns = ["Quadrante", "N. comuni", "Poli medi", "Ind. attr. medio"]
st.dataframe(counts_q.set_index("Quadrante"), use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
