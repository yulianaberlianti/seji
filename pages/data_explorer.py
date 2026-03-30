"""Data Explorer — full table, filters, download."""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def show():
    df = get_indonesia_3t_data()

    st.markdown("""
    <div class="hero-banner" style="padding:1.5rem 2rem;">
        <span class="badge">📋 DATA</span>
        <h2 class="hero-title" style="font-size:1.6rem;">Data Explorer</h2>
        <p class="hero-subtitle">Filter, eksplorasi, dan unduh dataset SEJI seluruh provinsi Indonesia</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ─────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        islands = ["Semua"] + sorted(df["island"].unique().tolist())
        sel_island = st.selectbox("Kepulauan", islands)
    with col2:
        priorities = ["Semua"] + ["Critical", "High", "Moderate", "Low"]
        sel_priority = st.selectbox("Prioritas SEJI", priorities)
    with col3:
        sel_3t = st.selectbox("Status 3T", ["Semua", "3T Only", "Non-3T Only"])
    with col4:
        seji_range = st.slider("Range SEJI Score", 0.0, 100.0, (0.0, 100.0), 1.0)

    # Apply filters
    filtered = df.copy()
    if sel_island != "Semua":
        filtered = filtered[filtered["island"] == sel_island]
    if sel_priority != "Semua":
        filtered = filtered[filtered["priority"] == sel_priority]
    if sel_3t == "3T Only":
        filtered = filtered[filtered["is_3t"]]
    elif sel_3t == "Non-3T Only":
        filtered = filtered[~filtered["is_3t"]]
    filtered = filtered[(filtered["seji_score"] >= seji_range[0]) &
                        (filtered["seji_score"] <= seji_range[1])]

    st.markdown(f"**{len(filtered)} provinsi** ditemukan")

    # ── Summary Stats ────────────────────────────────────────────
    if len(filtered) > 0:
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Rata-rata SEJI", f"{filtered['seji_score'].mean():.1f}")
        with col_s2:
            st.metric("Rata-rata Solar", f"{filtered['solar_kwh'].mean():.2f} kWh/m²")
        with col_s3:
            st.metric("Rata-rata Akses Listrik", f"{filtered['electricity_access'].mean()*100:.1f}%")
        with col_s4:
            st.metric("Rata-rata Kemiskinan", f"{filtered['poverty_rate'].mean():.1f}%")

    # ── Main Data Table ──────────────────────────────────────────
    display_cols = {
        "province": "Provinsi",
        "island": "Kepulauan",
        "is_3t": "3T Region",
        "seji_score": "SEJI Score",
        "priority": "Prioritas",
        "solar_kwh": "Solar (kWh/m²)",
        "electricity_access": "Akses Listrik",
        "poverty_rate": "Kemiskinan (%)",
        "pop_density": "Pop. Density",
        "remoteness": "Keterpencilan",
    }

    display_df = filtered[list(display_cols.keys())].rename(columns=display_cols).copy()
    display_df["Akses Listrik"] = (display_df["Akses Listrik"] * 100).round(1).astype(str) + "%"
    display_df["Pop. Density"] = display_df["Pop. Density"].apply(lambda x: f"{x:,.0f}")
    display_df["3T Region"] = display_df["3T Region"].map({True: "✅ Ya", False: "❌ Tidak"})

    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        column_config={
            "SEJI Score": st.column_config.ProgressColumn(
                "SEJI Score", min_value=0, max_value=100, format="%.1f"
            ),
            "Prioritas": st.column_config.TextColumn("Prioritas"),
        }
    )

    # ── Download ─────────────────────────────────────────────────
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv = filtered.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name="seji_indonesia_data.csv",
            mime="text/csv",
        )
    with col_dl2:
        json_str = filtered.to_json(orient="records", indent=2)
        st.download_button(
            "⬇️ Download JSON",
            data=json_str,
            file_name="seji_indonesia_data.json",
            mime="application/json",
        )

    # ── Scatter Matrix ───────────────────────────────────────────
    st.markdown("### 📊 Scatter Matrix — Semua Parameter")
    if len(filtered) >= 3:
        dims = ["seji_score", "solar_kwh", "electricity_access", "poverty_rate", "remoteness"]
        fig = px.scatter_matrix(
            filtered,
            dimensions=dims,
            color="priority",
            color_discrete_map=PRIORITY_COLORS,
            hover_name="province",
            labels={
                "seji_score": "SEJI",
                "solar_kwh": "Solar",
                "electricity_access": "E.Access",
                "poverty_rate": "Poverty",
                "remoteness": "Remote",
            },
        )
        fig.update_traces(diagonal_visible=False, marker=dict(size=5, opacity=0.7))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8F4F8", family="Sora"),
            height=550,
            legend=dict(bgcolor="rgba(17,34,64,0.8)"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tambah lebih banyak data untuk melihat scatter matrix.")
