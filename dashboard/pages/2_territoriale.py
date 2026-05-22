import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import carica_dati, COLORI, REGIONI, PLOTLY_LAYOUT, SHARED_CSS, render_header, render_sidebar


st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

df = carica_dati()

CITTA_METRO = {
    "015": "Milano", "058": "Roma", "063": "Napoli", "001": "Torino",
    "007": "Genova", "037": "Bologna", "048": "Firenze", "072": "Bari",
    "087": "Catania", "082": "Palermo", "027": "Venezia", "023": "Verona"
}

# Codici Procom esatti dei capoluoghi metropolitani
CAPOLUOGHI = {
    "015146": "Milano", "058091": "Roma",    "063049": "Napoli",  "001272": "Torino",
    "007024": "Genova", "037006": "Bologna", "048017": "Firenze", "072006": "Bari",
    "087015": "Catania","082053": "Palermo", "027042": "Venezia", "023036": "Verona"
}

df["cod_prov"]    = df["Procom"].str[:3]
df["citta_metro"] = df["cod_prov"].map(CITTA_METRO)
df["e_capoluogo"] = df["Procom"].isin(CAPOLUOGHI.keys())

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="nav-title">Filtri · Territoriale</span>', unsafe_allow_html=True)
    scala = st.radio("Scala di analisi", ["Regionale", "Città metropolitane", "Confronto ripartizioni"])
    if scala == "Regionale":
        regione_sel = st.selectbox("Seleziona regione",
            sorted(df["nome_regione"].dropna().unique()))
    elif scala == "Città metropolitane":
        metro_sel = st.multiselect("Città metropolitane",
            list(CITTA_METRO.values()),
            default=["Milano", "Roma", "Napoli", "Torino", "Firenze"])

# ── HEADER ────────────────────────────────────────────────────────────────────
render_header("Analisi territoriale multi-scala", "Struttura dei flussi per scala geografica")

# ════════════════════════════════════════════════════════════════════════════════
# SCALA REGIONALE
# ════════════════════════════════════════════════════════════════════════════════
if scala == "Regionale":
    dff = df[df["nome_regione"] == regione_sel].copy()

    n_attr = (dff['classificazione']=='attrattore').sum()
    n_emit = (dff['classificazione']=='emettitore').sum()
    n_equi = (dff['classificazione']=='equilibrato').sum()
    n_tot  = max(len(dff), 1)

    k1, k2, k3, k4, k5 = st.columns(5)
    metrics = [
        (k1, "#051186", "Attrattori",
         f"{n_attr}",
         f"{n_attr/n_tot*100:.0f}% dei comuni"),
        (k2, "#00880D", "Emettitori",
         f"{n_emit}",
         f"{n_emit/n_tot*100:.0f}% dei comuni"),
        (k3, "#C1C1C1", "Equilibrati",
         f"{n_equi}",
         f"{n_equi/n_tot*100:.0f}% dei comuni"),
        (k4, "#00649C", "Poli culturali",
         f"{dff['n_poli_totali'].sum():,}",
         f"in {(dff['n_poli_totali']>0).sum()} comuni"),
        (k5, "#4FC3F7", "Ind. attr. medio",
         f"{dff['indice_attrattivita'].mean():.3f}",
         f"max {dff['indice_attrattivita'].max():.3f}"),
    ]
    for col, color, label, val, sub in metrics:
        with col:
            st.markdown(f"""<div class="kpi-card" style="border-left-color:{color}; min-height:130px; height:130px;">
                <div class="top-bar" style="background:{color};"></div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}; font-size:1.6rem;">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])

    with c1:
        top30 = dff.nlargest(15, "saldo_netto")
        bot15 = dff.nsmallest(15, "saldo_netto")
        combined = pd.concat([top30, bot15]).sort_values("saldo_netto")
        fig_bar = px.bar(
            combined, x="saldo_netto", y="COMUNE",
            color="classificazione", color_discrete_map=COLORI,
            orientation="h", height=530,
            labels={"saldo_netto": "Saldo netto", "COMUNE": ""},
            hover_data={"entrate": True, "uscite": True, "n_poli_totali": True}
        )
        layout1 = copy.deepcopy(PLOTLY_LAYOUT)
        layout1.update(showlegend=False, margin=dict(t=10, b=30, l=10, r=20))
        fig_bar.update_layout(**layout1)
        fig_bar.add_vline(x=0, line_color="#051186", line_width=1)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_sc = px.scatter(
            dff[dff["POP21"] > 200],
            x="POP21", y="saldo_netto",
            color="classificazione", color_discrete_map=COLORI,
            size="n_poli_totali", size_max=30,
            hover_name="COMUNE",
            labels={"POP21": "Popolazione", "saldo_netto": "Saldo netto"},
            height=255
        )
        layout2 = copy.deepcopy(PLOTLY_LAYOUT)
        layout2.update(showlegend=False, margin=dict(t=10, b=40, l=50, r=10))
        fig_sc.update_layout(**layout2)
        fig_sc.add_hline(y=0, line_dash="dash", line_color="#051186", line_width=1)
        st.plotly_chart(fig_sc, use_container_width=True)

        tipologie = pd.DataFrame({
            "Tipologia": ["Musei", "Teatri", "Biblioteche", "Siti arch.", "Monumenti", "Gallerie"],
            "N.": [dff["n_musei"].sum(), dff["n_teatri"].sum(), dff["n_biblioteche"].sum(),
                   dff["n_siti_arch"].sum(), dff["n_monumenti"].sum(), dff["n_gallerie"].sum()]
        }).sort_values("N.", ascending=True)
        fig_tip = px.bar(tipologie, x="N.", y="Tipologia", orientation="h",
            color="N.", color_continuous_scale=["#b3dff5", "#051186"], height=255)
        layout3 = copy.deepcopy(PLOTLY_LAYOUT)
        layout3.update(showlegend=False, coloraxis_showscale=False, margin=dict(t=5, b=30, l=10, r=10))
        fig_tip.update_layout(**layout3)
        st.plotly_chart(fig_tip, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# SCALA CITTÀ METROPOLITANE
# ════════════════════════════════════════════════════════════════════════════════
elif scala == "Città metropolitane":
    if not metro_sel:
        st.info("Seleziona almeno una città metropolitana dalla sidebar.")
        st.stop()

    dff = df[df["citta_metro"].isin(metro_sel)].copy()

    metro_agg = dff.groupby("citta_metro").agg(
        n_comuni=("Procom", "count"),
        attrattori=("classificazione", lambda x: (x == "attrattore").sum()),
        emettitori=("classificazione", lambda x: (x == "emettitore").sum()),
        saldo_totale=("saldo_netto", "sum"),
        ind_attr_medio=("indice_attrattivita", "mean"),
        poli_totali=("n_poli_totali", "sum"),
        int_cult_media=("intensita_culturale", "mean"),
        pop_totale=("POP21", "sum"),
    ).reset_index()
    metro_agg["pct_attrattori"] = (metro_agg["attrattori"] / metro_agg["n_comuni"] * 100).round(1)

    from sklearn.preprocessing import MinMaxScaler
    dims = ["attrattori", "poli_totali", "ind_attr_medio", "int_cult_media", "saldo_totale"]
    labels_radar = ["Attrattori", "Poli culturali", "Ind. attrattività", "Intensità culturale", "Saldo netto"]

    try:
        scaler = MinMaxScaler()
        metro_norm = metro_agg.copy()
        metro_norm[dims] = scaler.fit_transform(metro_agg[dims])

        PALETTE = ["#051186","#4FC3F7","#00649C","#10a870","#00880D",
                   "#7B5EA7","#F2A65A","#3AAFA9","#D62828","#F7B731","#2E86AB","#A23B72"]
        fig_radar = go.Figure()
        for i, row in metro_norm.iterrows():
            vals = [row[d] for d in dims] + [row[dims[0]]]
            color = PALETTE[i % len(PALETTE)]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=labels_radar + [labels_radar[0]],
                fill="toself", name=row["citta_metro"],
                line_color=color, opacity=0.8
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#eaf4fc",
                radialaxis=dict(visible=True, range=[0, 1],
                                gridcolor="#a8cfe0", tickfont=dict(color="#1a3a4f", size=11)),
                angularaxis=dict(gridcolor="#a8cfe0", tickfont=dict(color="#1a3a4f", size=12))
            ),
            paper_bgcolor="#f4faff", plot_bgcolor="#f4faff",
            font=dict(family="Plus Jakarta Sans", color="#1a3a4f"),
            showlegend=True, height=450,
            margin=dict(t=30, b=30, l=60, r=60)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    except ImportError:
        st.info("Installa scikit-learn per il radar chart: pip install scikit-learn")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    PALETTE = ["#051186","#4FC3F7","#00649C","#10a870","#00880D",
               "#7B5EA7","#F2A65A","#3AAFA9","#D62828","#F7B731","#2E86AB","#A23B72"]

    with c1:

        # Costruiamo dati per città con ruolo capoluogo/attrattore/emettitore
        dff_ruolo = dff.copy()
        dff_ruolo["ruolo"] = dff_ruolo.apply(
            lambda r: "Capoluogo" if r["e_capoluogo"] else r["classificazione"].capitalize(), axis=1
        )
        metro_ruolo = dff_ruolo.groupby(["citta_metro", "ruolo"]).size().reset_index(name="n_comuni")
        # Ordiniamo per saldo totale decrescente
        ordine = metro_agg.sort_values("saldo_totale", ascending=False)["citta_metro"].tolist()
        metro_ruolo["citta_metro"] = pd.Categorical(metro_ruolo["citta_metro"], categories=ordine, ordered=True)
        metro_ruolo = metro_ruolo.sort_values("citta_metro")

        fig_grouped = px.bar(
            metro_ruolo,
            x="citta_metro", y="n_comuni",
            color="ruolo",
            barmode="stack",
            color_discrete_map={
                "Capoluogo":   "#c9a84c",
                "Attrattore":  "#051186",
                "Emettitore":  "#00880D",
                "Equilibrato": "#4FC3F7"
            },
            labels={"citta_metro": "", "n_comuni": "N. comuni", "ruolo": ""},
            height=340
        )
        layout_g = copy.deepcopy(PLOTLY_LAYOUT)
        layout_g.update(margin=dict(t=10, b=60, l=40, r=10))
        fig_grouped.update_layout(**layout_g)
        st.plotly_chart(fig_grouped, use_container_width=True)

    with c2:
        fig_m2 = px.scatter(
            metro_agg, x="saldo_totale", y="poli_totali",
            text="citta_metro", size="pop_totale", size_max=40,
            color="ind_attr_medio",
            color_continuous_scale=["#b3dff5", "#051186"],
            labels={"saldo_totale": "Saldo netto totale", "poli_totali": "N. poli culturali",
                    "ind_attr_medio": "Ind. attr. medio"},
            height=320
        )
        layout_m2 = copy.deepcopy(PLOTLY_LAYOUT)
        layout_m2.update(margin=dict(t=10, b=40, l=50, r=10))
        fig_m2.update_layout(**layout_m2)
        fig_m2.update_coloraxes(colorbar=dict(
            tickfont=dict(color="#1a3a4f"),
            title=dict(font=dict(color="#1a3a4f"), text="Ind. attr.")
        ))
        fig_m2.update_traces(textposition="top center", textfont=dict(size=10, color="#1a3a4f"))
        st.plotly_chart(fig_m2, use_container_width=True)

    metro_display = metro_agg[[
        "citta_metro", "n_comuni", "attrattori", "emettitori", "pct_attrattori",
        "poli_totali", "ind_attr_medio", "int_cult_media", "saldo_totale"
    ]].copy()
    metro_display.columns = [
        "Città", "N. comuni", "Attrattori", "Emettitori", "% attrattori",
        "Poli culturali", "Ind. attr. medio", "Int. culturale media", "Saldo netto totale"
    ]
    metro_display["Ind. attr. medio"] = metro_display["Ind. attr. medio"].round(3)
    metro_display["Int. culturale media"] = metro_display["Int. culturale media"].round(3)
    metro_display["% attrattori"] = metro_display["% attrattori"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(metro_display.set_index("Città"), use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# CONFRONTO RIPARTIZIONI
# ════════════════════════════════════════════════════════════════════════════════
elif scala == "Confronto ripartizioni":
    rip_agg = df.groupby("ripartizione").agg(
        n_comuni=("Procom", "count"),
        attrattori=("classificazione", lambda x: (x == "attrattore").sum()),
        emettitori=("classificazione", lambda x: (x == "emettitore").sum()),
        poli_totali=("n_poli_totali", "sum"),
        ind_attr_medio=("indice_attrattivita", "mean"),
        int_cult_media=("intensita_culturale", "mean"),
        saldo_medio=("saldo_netto", "mean"),
        pop_totale=("POP21", "sum"),
    ).reset_index()
    rip_agg["pct_attrattori"] = (rip_agg["attrattori"] / rip_agg["n_comuni"] * 100).round(1)

    c1, c2 = st.columns(2)
    with c1:
        fig_rip = go.Figure()
        for cls, color in COLORI.items():
            vals = rip_agg.apply(
                lambda r: (df[(df["ripartizione"] == r["ripartizione"]) &
                              (df["classificazione"] == cls)].shape[0]), axis=1)
            fig_rip.add_trace(go.Bar(
                x=rip_agg["ripartizione"], y=vals,
                name=cls.capitalize(), marker_color=color
            ))
        layout_r = copy.deepcopy(PLOTLY_LAYOUT)
        layout_r.update(barmode="stack", height=380, margin=dict(t=10, b=60, l=40, r=10))
        fig_rip.update_layout(**layout_r)
        st.plotly_chart(fig_rip, use_container_width=True)

    with c2:
        fig_rip2 = px.bar(
            rip_agg, x="ripartizione", y=["ind_attr_medio", "int_cult_media"],
            barmode="group", height=380,
            color_discrete_map={"ind_attr_medio": "#051186", "int_cult_media": "#4FC3F7"},
            labels={"ripartizione": "", "value": "Valore medio", "variable": "Indicatore"}
        )
        layout_r2 = copy.deepcopy(PLOTLY_LAYOUT)
        layout_r2.update(margin=dict(t=10, b=60, l=40, r=10))
        fig_rip2.update_layout(**layout_r2)
        newnames = {"ind_attr_medio": "Ind. attrattività", "int_cult_media": "Int. culturale"}
        fig_rip2.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))
        st.plotly_chart(fig_rip2, use_container_width=True)

    rip_display = rip_agg.copy()
    rip_display["ind_attr_medio"] = rip_display["ind_attr_medio"].round(3)
    rip_display["int_cult_media"] = rip_display["int_cult_media"].round(3)
    rip_display["saldo_medio"] = rip_display["saldo_medio"].round(0).astype(int)
    rip_display["pct_attrattori"] = rip_display["pct_attrattori"].apply(lambda x: f"{x:.1f}%")
    rip_display.columns = ["Ripartizione", "N. comuni", "Attrattori", "Emettitori",
                            "Poli culturali", "Ind. attr. medio", "Int. cult. media",
                            "Saldo medio", "Popolazione", "% attrattori"]
    st.dataframe(rip_display.set_index("Ripartizione"), use_container_width=True)