"""Dashboard — overview statistics and key insights."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS, ISLAND_COLORS


def show():
    df = get_indonesia_3t_data()

    # ── Hero Banner ─────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <div>
            <span class="badge">WEBGIS</span>
            <span class="badge">INDONESIA 3T</span>
            <span class="badge">OPEN DATA</span>
        </div>
        <h1 class="hero-title">Solar Energy Justice Index</h1>
        <p class="hero-subtitle">Pemetaan Keadilan Energi Surya Berbasis Spasial — Wilayah Tertinggal, Terdepan & Terluar Indonesia</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Metrics ────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)
    total      = len(df)
    t3_count   = df["is_3t"].sum()
    critical   = (df["priority"] == "Critical").sum()
    high       = (df["priority"] == "High").sum()
    avg_solar  = df["solar_kwh"].mean()
    avg_access = df["electricity_access"].mean() * 100

    with col1:
        st.metric("Total Provinsi", f"{total}", "Indonesia")
    with col2:
        st.metric("Wilayah 3T", f"{t3_count}", f"{t3_count/total*100:.0f}% dari total")
    with col3:
        st.metric("Prioritas Kritis", f"{critical}", "perlu segera")
    with col4:
        st.metric("Rata-rata Radiasi", f"{avg_solar:.1f}", "kWh/m²/hari")
    with col5:
        st.metric("Akses Listrik Rata²", f"{avg_access:.0f}%", "nasional")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top 10 Priority Provinces ────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🔴 Top 10 Provinsi Prioritas SEJI")
        top10 = df.head(10).copy()
        top10["rank"] = range(1, 11)

        fig = go.Figure()
        colors = [PRIORITY_COLORS.get(str(p), "#888") for p in top10["priority"]]
        fig.add_trace(go.Bar(
            x=top10["seji_score"],
            y=top10["province"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.1)", width=1)
            ),
            text=[f"{s:.1f}" for s in top10["seji_score"]],
            textposition="inside",
            textfont=dict(color="white", size=12, family="Space Mono"),
            hovertemplate="<b>%{y}</b><br>SEJI Score: %{x:.1f}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,34,64,0.6)",
            font=dict(color="#E8F4F8", family="Sora"),
            xaxis=dict(range=[0, 105], gridcolor="rgba(255,255,255,0.05)",
                       title="SEJI Score", tickfont=dict(size=10)),
            yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
            margin=dict(l=10, r=10, t=10, b=40),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 📊 Distribusi Prioritas")
        priority_counts = df["priority"].value_counts()
        order = ["Critical", "High", "Moderate", "Low"]
        priority_counts = priority_counts.reindex(order).dropna()

        fig2 = go.Figure(go.Pie(
            labels=priority_counts.index,
            values=priority_counts.values,
            hole=0.6,
            marker=dict(colors=[PRIORITY_COLORS[k] for k in priority_counts.index],
                        line=dict(color="#0D1B2A", width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, family="Sora"),
            hovertemplate="<b>%{label}</b><br>%{value} provinsi (%{percent})<extra></extra>",
        ))
        fig2.add_annotation(
            text=f"<b>{total}</b><br>Provinsi",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#F5A623", family="Sora"),
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8F4F8"),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            height=380,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Island Summary Cards ─────────────────────────────────────
    st.markdown("### 🌏 Ringkasan Per Kepulauan")
    island_summary = df.groupby("island").agg(
        provinces=("province", "count"),
        avg_seji=("seji_score", "mean"),
        avg_solar=("solar_kwh", "mean"),
        avg_access=("electricity_access", "mean"),
        t3_count=("is_3t", "sum"),
        critical_count=("priority", lambda x: (x == "Critical").sum()),
    ).reset_index()
    island_summary = island_summary.sort_values("avg_seji", ascending=False)

    cols = st.columns(len(island_summary))
    for i, (_, row) in enumerate(island_summary.iterrows()):
        color = ISLAND_COLORS.get(row["island"], "#888")
        with cols[i]:
            st.markdown(f"""
            <div style='background: #112240; border: 1px solid {color}40;
                        border-top: 3px solid {color}; border-radius:10px;
                        padding: 0.8rem; text-align:center;'>
                <div style='font-size:0.7rem; color:{color}; font-weight:700;
                            letter-spacing:1px; font-family:Space Mono;'>{row['island'].upper()}</div>
                <div style='font-size:1.6rem; font-weight:800; color:#F5A623; margin:4px 0;'>
                    {row['avg_seji']:.0f}</div>
                <div style='font-size:0.65rem; color:#8892A4;'>SEJI avg</div>
                <hr style='border-color:rgba(255,255,255,0.1); margin:6px 0;'>
                <div style='font-size:0.7rem; color:#8892A4;'>
                    ⚡ {row['avg_solar']:.1f} kWh/m²<br>
                    🔋 {row['avg_access']*100:.0f}% akses<br>
                    🏷️ {int(row['t3_count'])}/{int(row['provinces'])} 3T
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Solar vs Energy Access Scatter ────────────────────────────
    st.markdown("### ☀️ Radiasi Matahari vs Akses Energi")
    fig3 = px.scatter(
        df,
        x="solar_kwh", y="electricity_access",
        color="priority",
        color_discrete_map=PRIORITY_COLORS,
        size="poverty_rate",
        hover_name="province",
        hover_data={"solar_kwh": ":.2f", "electricity_access": ":.2%",
                    "poverty_rate": ":.1f", "seji_score": ":.1f"},
        labels={
            "solar_kwh": "Radiasi Matahari (kWh/m²/hari)",
            "electricity_access": "Rasio Akses Listrik",
            "priority": "Prioritas SEJI",
        },
        symbol="is_3t",
        symbol_map={True: "diamond", False: "circle"},
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,34,64,0.6)",
        font=dict(color="#E8F4F8", family="Sora"),
        height=400,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=".0%"),
        legend=dict(bgcolor="rgba(17,34,64,0.8)", bordercolor="rgba(245,166,35,0.3)", borderwidth=1),
    )
    # Add quadrant lines
    fig3.add_hline(y=0.7, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                   annotation_text="Akses Listrik 70%", annotation_font_color="#8892A4")
    fig3.add_vline(x=4.9, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                   annotation_text="4.9 kWh/m²", annotation_font_color="#8892A4")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Key Insight Box ──────────────────────────────────────────
    top_prov = df.iloc[0]
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(255,107,0,0.1), rgba(245,166,35,0.05));
                border: 1px solid rgba(245,166,35,0.3); border-radius:12px; padding:1.5rem;'>
        <span class="badge">💡 KEY INSIGHT</span>
        <p style='color:#E8F4F8; margin-top:0.8rem; line-height:1.8;'>
            <strong style='color:#F5A623;'>{top_prov["province"]}</strong> menempati posisi tertinggi SEJI Score
            dengan nilai <strong style='color:#FF4560;'>{top_prov["seji_score"]}</strong>/100,
            menunjukkan kombinasi potensi surya tinggi ({top_prov["solar_kwh"]:.1f} kWh/m²/hari)
            dengan akses listrik rendah ({top_prov["electricity_access"]*100:.0f}%) dan
            tingkat kemiskinan {top_prov["poverty_rate"]:.1f}%.
            Wilayah ini menjadi prioritas utama intervensi pengembangan PLTS terdesentralisasi.
        </p>
    </div>
    """, unsafe_allow_html=True)
