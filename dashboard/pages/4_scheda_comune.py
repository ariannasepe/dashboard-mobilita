import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import carica_dati, COLORI, PLOTLY_LAYOUT, SHARED_CSS, render_header, render_sidebar


st.markdown(SHARED_CSS + """
<style>
.comune-header {
    background: linear-gradient(135deg, #25465D 0%, #1a6a9a 60%, #4FC3F7 100%);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
    box-shadow: 0 6px 20px rgba(37,70,93,0.15);
}
.comune-header h2 {
    font-size: 2rem; font-weight: 800;
    color: #ffffff; margin: 0 0 0.3rem 0;
}
.comune-header .regione {
    font-size: 0.75rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,0.65); margin-bottom: 0.8rem;
}
.badge { display:inline-block; padding:3px 14px; border-radius:20px; font-size:0.75rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
.stat-row { display:flex; gap:2rem; margin-top:1rem; flex-wrap:wrap; }
.stat-item .stat-val { font-size:1.6rem; font-weight:800; color:#ffffff; }
.stat-item .stat-lbl { font-size:0.65rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:rgba(255,255,255,0.65); }
.metric-card { background:#ffffff; border:1px solid #b3dff5; border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.6rem; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
.metric-card .m-label { font-size:0.65rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#666; margin-bottom:0.3rem; }
.metric-card .m-value { font-size:1.4rem; font-weight:800; color:#25465D; }
.metric-card .m-sub { font-size:0.7rem; color:#34465A; margin-top:0.15rem; }
.percentile-bar { background:#e0f2fe; border-radius:4px; height:6px; margin-top:0.4rem; overflow:hidden; }
.percentile-fill { height:100%; border-radius:4px; transition:width 0.3s; }
</style>
""", unsafe_allow_html=True)
render_sidebar()

df = carica_dati()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="nav-title">Ricerca comune</span>', unsafe_allow_html=True)
    comune_sel = st.selectbox(
        "Digita il nome del comune",
        options=[""] + sorted(df["COMUNE"].unique()),
        index=0,
        placeholder="es. Milano, Firenze..."
    )
    if comune_sel:
        st.markdown("---")
        st.markdown('<span style="font-size:0.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#b3dff5;">Confronta con</span>', unsafe_allow_html=True)
        confronto_sel = st.selectbox(
            "Comune di confronto (opzionale)",
            options=[""] + sorted([c for c in df["COMUNE"].unique() if c != comune_sel]),
            index=0,
            key="confronto_sel"
        )
    else:
        confronto_sel = ""

# ── HEADER ────────────────────────────────────────────────────────────────────
render_header("Scheda comune", "Profilo territoriale dettagliato")

if not comune_sel:
    st.markdown("""
    <div style="background:#ffffff;border:1px solid #b3dff5;border-radius:14px;
                padding:3rem;text-align:center;color:#34465A;
                box-shadow:0 4px 16px rgba(0,0,0,0.07);">
        <div style="font-size:1.2rem;font-weight:700;color:#25465D;margin-bottom:0.5rem;">
            Cerca un comune dalla sidebar
        </div>
        <div style="font-size:0.85rem;color:#34465A;">
            Digita il nome di qualsiasi comune italiano per visualizzare il profilo completo
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

row = df[df["COMUNE"] == comune_sel].iloc[0]

def pct_rank(series, val):
    return round((series < val).sum() / len(series) * 100, 1)

pct_attr = pct_rank(df["indice_attrattivita"], row["indice_attrattivita"])
pct_poli = pct_rank(df["n_poli_totali"], row["n_poli_totali"])
pct_int  = pct_rank(df["intensita_culturale"], row["intensita_culturale"])
pct_pop  = pct_rank(df["POP21"], row["POP21"])

cls = row["classificazione"]
badge_style = {
    "attrattore":  "background:#dbe4ff;color:#051186;",
    "emettitore":  "background:#d4edda;color:#00880D;",
    "equilibrato": "background:#e0f2fe;color:#0369a1;"
}.get(cls, "")

# ── HEADER COMUNE ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="comune-header">
    <div class="regione">{row['nome_regione']} · Cod. {row['Procom']}</div>
    <h2>{comune_sel}</h2>
    <span class="badge" style="{badge_style}">{cls.upper()}</span>
    <div class="stat-row">
        <div class="stat-item">
            <div class="stat-val">{int(row['POP21']):,}</div>
            <div class="stat-lbl">Abitanti 2021</div>
        </div>
        <div class="stat-item">
            <div class="stat-val">{int(row['FAM21']):,}</div>
            <div class="stat-lbl">Famiglie</div>
        </div>
        <div class="stat-item">
            <div class="stat-val">{int(row['entrate']):,}</div>
            <div class="stat-lbl">Entrate</div>
        </div>
        <div class="stat-item">
            <div class="stat-val">{int(row['uscite']):,}</div>
            <div class="stat-lbl">Uscite</div>
        </div>
        <div class="stat-item">
            <div class="stat-val">{int(row['saldo_netto']):+,}</div>
            <div class="stat-lbl">Saldo netto</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── COLONNE PRINCIPALI ────────────────────────────────────────────────────────
col_left, col_mid, col_right = st.columns([1.2, 1.5, 1.5])

with col_left:
    st.markdown('<div class="section-label">INDICATORI KPI</div>', unsafe_allow_html=True)

    def metric_card(label, value, sub, pct, color):
        return f"""
        <div class="metric-card">
            <div class="m-label">{label}</div>
            <div class="m-value" style="color:{color};">{value}</div>
            <div class="m-sub">{sub}</div>
            <div class="percentile-bar">
                <div class="percentile-fill" style="width:{pct}%;background:{color};"></div>
            </div>
            <div style="font-size:0.65rem;color:#666;margin-top:0.2rem;">Percentile nazionale: {pct:.0f}°</div>
        </div>"""

    st.markdown(
        metric_card("Indice di attrattività",
            f"{row['indice_attrattivita']:.4f}",
            "entrate / popolazione", pct_attr, "#25465D") +
        metric_card("Poli culturali",
            f"{int(row['n_poli_totali'])}",
            "nel territorio comunale", pct_poli, "#00649C") +
        metric_card("Intensità culturale",
            f"{row['intensita_culturale']:.4f}",
            "quota flussi verso cultura", pct_int, "#10a870") +
        metric_card("Popolazione",
            f"{int(row['POP21']):,}",
            "residenti al 2021", pct_pop, "#7B5EA7"),
        unsafe_allow_html=True
    )

    has_reti = "km_rete_anas" in df.columns
    if has_reti:
        st.markdown('<div class="section-label" style="margin-top:1rem">INFRASTRUTTURE</div>', unsafe_allow_html=True)
        infra = [
            ("Km rete ANAS",         f"{row.get('km_rete_anas',0):.1f} km"),
            ("TGM medio",            f"{int(row.get('tgm_medio',0)):,} veic/gg"),
            ("Stazioni ferroviarie", f"{int(row.get('n_stazioni_totali',0))}"),
        ]
        rows_html = ""
        for i, (lbl, val) in enumerate(infra):
            border = "border-bottom:1px solid #b3dff5;" if i < len(infra) - 1 else ""
            rows_html += f"""
            <div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                        {border}font-size:0.8rem;">
                <span style="color:#34465A;">{lbl}</span>
                <span style="color:#25465D;font-weight:700;">{val}</span>
            </div>"""
        st.markdown(f'<div style="background:#ffffff;border:1px solid #b3dff5;border-radius:10px;padding:0.6rem 0.9rem;box-shadow:0 2px 6px rgba(0,0,0,0.04);">{rows_html}</div>', unsafe_allow_html=True)

with col_mid:
    st.markdown('<div class="section-label">FLUSSI DI MOBILITÀ</div>', unsafe_allow_html=True)

    max_abs    = max(abs(df["saldo_netto"].min()), df["saldo_netto"].max())
    saldo_color = "#051186" if row["saldo_netto"] > 0 else "#00880D"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=row["saldo_netto"],
        delta={"reference": 0, "valueformat": ",",
               "increasing.color": "#051186", "decreasing.color": "#00880D"},
        number={"valueformat": ",", "font": {"color": "#1a3a4f", "size": 28, "family": "Plus Jakarta Sans"}},
        gauge={
            "axis": {"range": [-max_abs, max_abs], "tickcolor": "#1a3a4f",
                     "tickfont": {"color": "#1a3a4f", "size": 9}},
            "bar": {"color": saldo_color},
            "bgcolor": "#d6eaf6",
            "bordercolor": "#a8cfe0",
            "steps": [
                {"range": [-max_abs, 0], "color": "#fce8e6"},
                {"range": [0, max_abs],  "color": "#e8f4fb"}
            ],
            "threshold": {"line": {"color": "#4FC3F7", "width": 2}, "value": 0}
        },
        title={"text": "Saldo netto pendolarismo",
               "font": {"color": "#1a3a4f", "size": 11, "family": "Plus Jakarta Sans"}}
    ))
    fig_gauge.update_layout(
        paper_bgcolor="#f4faff", plot_bgcolor="#f4faff",
        font=dict(family="Plus Jakarta Sans", color="#1a3a4f"), height=230,
        margin=dict(t=30, b=10, l=20, r=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "absolute", "relative"],
        x=["Entrate", "Uscite", "Saldo netto"],
        y=[row["entrate"], -row["uscite"], row["saldo_netto"]],
        connector={"line": {"color": "#b3dff5"}},
        increasing={"marker": {"color": "#051186"}},
        decreasing={"marker": {"color": "#00880D"}},
        totals={"marker": {"color": saldo_color}},
        textposition="none"
    ))
    layout_wf = copy.deepcopy(PLOTLY_LAYOUT)
    layout_wf.update(showlegend=False, height=240, margin=dict(t=30, b=40, l=50, r=20))
    fig_wf.update_layout(**layout_wf)
    st.plotly_chart(fig_wf, use_container_width=True)

with col_right:
    st.markdown('<div class="section-label">DOTAZIONE CULTURALE</div>', unsafe_allow_html=True)

    tipologie = {
        "Musei":      row["n_musei"],
        "Biblioteche":row["n_biblioteche"],
        "Siti arch.": row["n_siti_arch"],
        "Monumenti":  row["n_monumenti"],
        "Teatri":     row["n_teatri"],
        "Gallerie":   row["n_gallerie"],
    }
    tot = sum(tipologie.values())

    if tot > 0:
        colors_t = ["#25465D","#4FC3F7","#00649C","#10a870","#7B5EA7","#E85933"]
        fig_pie = go.Figure(go.Pie(
            labels=list(tipologie.keys()),
            values=list(tipologie.values()),
            marker_colors=colors_t,
            hole=0.55,
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} poli (%{percent})<extra></extra>"
        ))
        fig_pie.update_layout(
            paper_bgcolor="#f4faff", plot_bgcolor="#f4faff",
            font=dict(family="Plus Jakarta Sans", color="#1a3a4f"),
            showlegend=True, height=270,
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08, font=dict(size=10, color="#1a3a4f")),
            margin=dict(t=10, b=40, l=0, r=0),
            annotations=[dict(
                text=f"<b>{tot}</b><br>totale",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=13, color="#1a3a4f")
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.markdown("""
        <div style="background:#f0f6fc;border:1px solid #b3dff5;border-radius:10px;
                    padding:2rem;text-align:center;color:#34465A;height:250px;
                    display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">○</div>
            <div>Nessun polo culturale rilevato</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:0.5rem">CONNETTIVITÀ CULTURALE</div>', unsafe_allow_html=True)
    connettivita = [
        ("Flussi verso cultura",   f"{int(row['flussi_verso_cultura']):,}"),
        ("Destinazioni culturali", f"{int(row['n_destinazioni_culturali'])}"),
        ("Intensità culturale",    f"{row['intensita_culturale']:.4f}"),
    ]
    conn_html = ""
    for i, (lbl, val) in enumerate(connettivita):
        border = "border-bottom:1px solid #b3dff5;" if i < len(connettivita) - 1 else ""
        conn_html += f"""
        <div style="display:flex;justify-content:space-between;padding:0.5rem 0;
                    {border}font-size:0.82rem;">
            <span style="color:#34465A;">{lbl}</span>
            <span style="color:#25465D;font-weight:700;">{val}</span>
        </div>"""
    st.markdown(f'<div style="background:#ffffff;border:1px solid #b3dff5;border-radius:10px;padding:0.6rem 0.9rem;box-shadow:0 2px 6px rgba(0,0,0,0.04);">{conn_html}</div>', unsafe_allow_html=True)



# ── CONFRONTO CON ALTRO COMUNE ────────────────────────────────────────────────
if confronto_sel:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">CONFRONTO</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{comune_sel} vs {confronto_sel}</div>', unsafe_allow_html=True)

    row2  = df[df["COMUNE"] == confronto_sel].iloc[0]
    dims  = ["indice_attrattivita","intensita_culturale","n_poli_totali","entrate","uscite"]
    labels_r = ["Ind. attrattività","Int. culturale","Poli culturali","Entrate","Uscite"]

    def norm(col, val):
        mx = df[col].max()
        return val / mx if mx > 0 else 0

    vals1 = [norm(d, row[d])  for d in dims]
    vals2 = [norm(d, row2[d]) for d in dims]

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatterpolar(
        r=vals1 + [vals1[0]], theta=labels_r + [labels_r[0]],
        fill="toself", name=comune_sel,
        line_color="#25465D", fillcolor="rgba(37,70,93,0.12)"
    ))
    fig_comp.add_trace(go.Scatterpolar(
        r=vals2 + [vals2[0]], theta=labels_r + [labels_r[0]],
        fill="toself", name=confronto_sel,
        line_color="#4FC3F7", fillcolor="rgba(79,195,247,0.12)"
    ))
    fig_comp.update_layout(
        polar=dict(
            bgcolor="#eaf4fc",
            radialaxis=dict(visible=True, range=[0, 1],
                            gridcolor="#a8cfe0", tickfont=dict(color="#1a3a4f", size=11)),
            angularaxis=dict(gridcolor="#a8cfe0", tickfont=dict(color="#1a3a4f", size=12))
        ),
        paper_bgcolor="#f4faff", plot_bgcolor="#f4faff",
        font=dict(family="Plus Jakarta Sans", color="#1a3a4f"),
        showlegend=True, height=380,
        margin=dict(t=30, b=30, l=60, r=60)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    comp_df = pd.DataFrame({
        "Indicatore": ["Classificazione","Saldo netto","Ind. attrattività",
                       "N. poli culturali","Intensità culturale","Popolazione",
                       "Entrate","Uscite","Flussi verso cultura"],
        comune_sel: [
            row["classificazione"].upper(),
            f"{int(row['saldo_netto']):+,}",
            f"{row['indice_attrattivita']:.4f}",
            f"{int(row['n_poli_totali'])}",
            f"{row['intensita_culturale']:.4f}",
            f"{int(row['POP21']):,}",
            f"{int(row['entrate']):,}",
            f"{int(row['uscite']):,}",
            f"{int(row['flussi_verso_cultura']):,}",
        ],
        confronto_sel: [
            row2["classificazione"].upper(),
            f"{int(row2['saldo_netto']):+,}",
            f"{row2['indice_attrattivita']:.4f}",
            f"{int(row2['n_poli_totali'])}",
            f"{row2['intensita_culturale']:.4f}",
            f"{int(row2['POP21']):,}",
            f"{int(row2['entrate']):,}",
            f"{int(row2['uscite']):,}",
            f"{int(row2['flussi_verso_cultura']):,}",
        ]
    })
    st.dataframe(comp_df.set_index("Indicatore"), use_container_width=True)

# ── POSIZIONE NEL CONTESTO REGIONALE ─────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">POSIZIONE NEL CONTESTO REGIONALE</div>', unsafe_allow_html=True)

df_reg        = df[df["nome_regione"] == row["nome_regione"]].copy()
df_reg_sorted = df_reg.sort_values("saldo_netto", ascending=False).reset_index(drop=True)
pos = df_reg_sorted[df_reg_sorted["COMUNE"] == comune_sel].index[0] + 1

st.markdown(f"""
<div style="background:#ffffff;border:1px solid #b3dff5;border-radius:10px;
            padding:1rem 1.4rem;font-size:0.82rem;color:#34465A;line-height:2;
            box-shadow:0 2px 8px rgba(0,0,0,0.05);">
    <b style="color:#25465D;">{comune_sel}</b> si posiziona al 
    <b style="color:#4FC3F7;">rank {pos}</b> su 
    <b style="color:#25465D;">{len(df_reg)}</b> comuni in {row['nome_regione']} 
    per saldo netto di mobilità.
</div>
""", unsafe_allow_html=True)

top10_reg = df_reg_sorted.head(10)[["COMUNE","saldo_netto","indice_attrattivita","n_poli_totali","classificazione"]]
top10_reg.index = range(1, len(top10_reg) + 1)
top10_reg.columns = ["Comune","Saldo netto","Ind. attrattività","Poli culturali","Classificazione"]

def highlight_comune(row_s):
    if row_s["Comune"] == comune_sel:
        return ["background-color: #dbe4ff; color: #051186"] * len(row_s)
    return [""] * len(row_s)

st.dataframe(top10_reg.style.apply(highlight_comune, axis=1), use_container_width=True)