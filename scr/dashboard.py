"""Dashboard — overview statistics and key insights. v2.0"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS, ISLAND_COLORS


def _apply_filter(df):
    pf = st.session_state.get("province_filter", "Semua Provinsi")
    if pf != "Semua Provinsi":
        return df[df["province"] == pf]
    return df


def show():
    cc  = st.session_state.get("cc", {})
    raw = get_indonesia_3t_data()
    df  = _apply_filter(raw)

    # ── Hero ─────────────────────────────────────────────────────
    pf = st.session_state.get("province_filter", "Semua Provinsi")
    scope = pf if pf != "Semua Provinsi" else "Seluruh Indonesia"
    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <span class="badge">WEBGIS</span>
            <span class="badge">INDONESIA 3T</span>
            <span class="badge">OPEN DATA</span>
        </div>
        <h1 class="hero-title">Solar Energy Justice Index</h1>
        <p class="hero-subtitle">Pemetaan Keadilan Energi Surya — {scope}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Metrics ───────────────────────────────────────────────
    total    = len(df)
    t3c      = int(df["is_3t"].sum())
    critical = int((df["priority"] == "Critical").sum())
    high_p   = int((df["priority"] == "High").sum())
    avg_sol  = df["solar_kwh"].mean()
    avg_acc  = df["electricity_access"].mean() * 100
    avg_pov  = df["poverty_rate"].mean()

    cols = st.columns(6)
    metrics = [
        ("Total Wilayah",      f"{total}",          "provinsi",             "Jumlah wilayah dalam tampilan ini"),
        ("Wilayah 3T",         f"{t3c}",            f"{t3c/max(total,1)*100:.0f}% dari total", "Tertinggal, Terdepan, Terluar"),
        ("Prioritas Kritis",   f"{critical}",        "perlu intervensi",    "SEJI Score > 75"),
        ("Rata-rata Radiasi",  f"{avg_sol:.1f}",    "kWh/m²/hari",         "Data NASA POWER, rata-rata tahunan 2020–2024"),
        ("Akses Listrik Avg",  f"{avg_acc:.0f}%",   "nasional",            "Rasio elektrifikasi per provinsi (BPS 2023)"),
        ("Kemiskinan Avg",     f"{avg_pov:.1f}%",   "tingkat kemiskinan",  "Data BPS 2023"),
    ]
    for col, (label, val, delta, tip) in zip(cols, metrics):
        with col:
            st.metric(label, val, delta, help=tip)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top 10 + Donut ────────────────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("### 🔴 Top 10 Prioritas SEJI")
        top10 = raw.head(10)  # always show national top 10
        colors = [PRIORITY_COLORS.get(str(p), "#888") for p in top10["priority"]]
        fig = go.Figure(go.Bar(
            x=top10["seji_score"], y=top10["province"], orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.08)", width=1)),
            text=[f"  {s:.1f}" for s in top10["seji_score"]],
            textposition="inside",
            textfont=dict(color="white", size=11, family="Space Mono"),
            customdata=top10[["solar_kwh", "electricity_access", "poverty_rate"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>SEJI: %{x:.1f}<br>"
                "☀️ Solar: %{customdata[0]:.2f} kWh/m²<br>"
                "⚡ Akses: %{customdata[1]:.1%}<br>"
                "💸 Miskin: %{customdata[2]:.1f}%<extra></extra>"
            ),
        ))
        fig.update_layout(
            paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
            plot_bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
            font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
            xaxis=dict(range=[0,105], gridcolor=cc.get("grid","rgba(255,255,255,0.06)"),
                       title="SEJI Score (0–100)", tickfont=dict(size=10)),
            yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
            margin=dict(l=5,r=5,t=5,b=35), height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("### 📊 Distribusi Prioritas")
        pc = raw["priority"].value_counts().reindex(["Critical","High","Moderate","Low"]).dropna()
        fig2 = go.Figure(go.Pie(
            labels=pc.index, values=pc.values, hole=0.58,
            marker=dict(colors=[PRIORITY_COLORS[k] for k in pc.index],
                        line=dict(color="#0B1623", width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, family="Plus Jakarta Sans"),
            hovertemplate="<b>%{label}</b><br>%{value} provinsi (%{percent})<extra></extra>",
        ))
        fig2.add_annotation(
            text=f"<b>{len(raw)}</b><br><span style='font-size:11px'>Provinsi</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color="#F5A623", family="Plus Jakarta Sans"),
        )
        fig2.update_layout(
            paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
            font=dict(color=cc.get("text","#C8D8E8")),
            margin=dict(l=5,r=5,t=5,b=5), showlegend=False, height=360,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Island Summary ────────────────────────────────────────────
    st.markdown("### 🌏 Ringkasan Per Kepulauan")
    isl = raw.groupby("island").agg(
        provinces=("province","count"),
        avg_seji=("seji_score","mean"),
        avg_solar=("solar_kwh","mean"),
        avg_access=("electricity_access","mean"),
        t3_count=("is_3t","sum"),
        critical_n=("priority", lambda x:(x=="Critical").sum()),
    ).reset_index().sort_values("avg_seji", ascending=False)

    cols2 = st.columns(len(isl))
    for i, (_, row) in enumerate(isl.iterrows()):
        c = ISLAND_COLORS.get(row["island"], "#888")
        with cols2[i]:
            st.markdown(f"""
            <div style='background:var(--bg-card);border:1px solid {c}38;
                        border-top:3px solid {c};border-radius:12px;
                        padding:0.85rem;text-align:center;'>
                <div style='font-size:0.62rem;color:{c};font-weight:700;
                            letter-spacing:1px;font-family:Space Mono;'>{row['island'].upper()}</div>
                <div style='font-size:1.65rem;font-weight:800;color:#F5A623;margin:3px 0;'>
                    {row['avg_seji']:.0f}</div>
                <div style='font-size:0.6rem;color:var(--text-muted);margin-bottom:6px;'>SEJI avg</div>
                <div style='font-size:0.68rem;color:var(--text-secondary);line-height:1.7;'>
                    ☀️ {row['avg_solar']:.1f} kWh/m²<br>
                    ⚡ {row['avg_access']*100:.0f}% akses<br>
                    🏷️ {int(row['t3_count'])}/{int(row['provinces'])} 3T
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Scatter: Solar vs Access ──────────────────────────────────
    st.markdown("### ☀️ Radiasi Matahari vs Akses Energi")
    st.caption("Ukuran marker = tingkat kemiskinan · Bentuk berlian = wilayah 3T · Zona kiri-bawah = prioritas tertinggi")

    fig3 = px.scatter(
        raw, x="solar_kwh", y="electricity_access",
        color="priority", color_discrete_map=PRIORITY_COLORS,
        size="poverty_rate", size_max=28,
        hover_name="province",
        hover_data={
            "solar_kwh":":.2f", "electricity_access":":.1%",
            "poverty_rate":":.1f", "seji_score":":.1f", "is_3t": True
        },
        symbol="is_3t", symbol_map={True:"diamond", False:"circle"},
        labels={
            "solar_kwh":"Radiasi Matahari (kWh/m²/hari)",
            "electricity_access":"Rasio Akses Listrik",
            "priority":"Prioritas",
        },
    )
    fig3.add_hline(y=0.7, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                   annotation_text="Threshold 70% akses",
                   annotation_font=dict(color=cc.get("text","#C8D8E8"), size=10))
    fig3.add_vline(x=4.9, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                   annotation_text="4.9 kWh/m²",
                   annotation_font=dict(color=cc.get("text","#C8D8E8"), size=10))
    # Label the quadrant
    fig3.add_annotation(x=5.4, y=0.35, text="🎯 PRIORITAS UTAMA<br>(Surya Tinggi + Akses Rendah)",
                         showarrow=False, font=dict(color="#FF4560", size=10),
                         bgcolor="rgba(255,69,96,0.1)", bordercolor="#FF4560",
                         borderwidth=1, borderpad=4)
    fig3.update_layout(
        paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
        plot_bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
        font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
        height=420,
        xaxis=dict(gridcolor=cc.get("grid","rgba(255,255,255,0.06)")),
        yaxis=dict(gridcolor=cc.get("grid","rgba(255,255,255,0.06)"), tickformat=".0%"),
        legend=dict(bgcolor=cc.get("legend","rgba(7,17,32,0.88)"),
                    bordercolor="rgba(245,166,35,0.3)", borderwidth=1),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Insight Box ───────────────────────────────────────────────
    top1 = raw.iloc[0]
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(232,130,12,0.08),rgba(245,166,35,0.03));
                border:1px solid rgba(245,166,35,0.28);border-radius:14px;padding:1.4rem;'>
        <span class="badge">💡 KEY INSIGHT</span>
        <p style='color:var(--text-primary);margin-top:0.8rem;line-height:1.85;font-size:0.92rem;'>
            <strong style='color:#F5A623;'>{top1["province"]}</strong> menempati peringkat SEJI tertinggi
            (<strong style='color:#FF4560;'>{top1["seji_score"]}</strong>/100) —
            kombinasi radiasi surya <strong>{top1["solar_kwh"]:.1f} kWh/m²/hari</strong>,
            akses listrik hanya <strong>{top1["electricity_access"]*100:.0f}%</strong>,
            dan kemiskinan <strong>{top1["poverty_rate"]:.1f}%</strong>.
            Wilayah ini adalah kandidat utama instalasi PLTS off-grid terdesentralisasi.
        </p>
    </div>
    """, unsafe_allow_html=True)
