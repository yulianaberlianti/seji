"""Methodology page — explain SEJI framework, AHP, and data sources."""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


def show():
    st.markdown("""
    <div class="hero-banner" style="padding:1.5rem 2rem;">
        <span class="badge">ℹ️ METODOLOGI</span>
        <h2 class="hero-title" style="font-size:1.6rem;">Kerangka Metodologi SEJI</h2>
        <p class="hero-subtitle">Framework analisis spasial berbasis penginderaan jauh, GIS, dan MCDA</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📐 Kerangka SEJI", "📡 Sumber Data", "🧮 Formula & AHP"])

    # ── Tab 1: Framework ─────────────────────────────────────────
    with tab1:
        st.markdown("### Alur Metodologi")

        # Flow diagram with plotly
        steps = [
            ("1. Pengumpulan\nData", "#F5A623", 0.1),
            ("2. Pra-Proses\n& Koreksi", "#FF6B00", 0.28),
            ("3. Ekstraksi\nParameter", "#00B4A6", 0.46),
            ("4. Normalisasi\n(0–1)", "#39D353", 0.64),
            ("5. MCDA/AHP\nPembobotan", "#8338EC", 0.82),
        ]

        fig = go.Figure()
        for i, (label, color, x) in enumerate(steps):
            fig.add_shape(type="circle",
                xref="paper", yref="paper",
                x0=x-0.07, y0=0.25, x1=x+0.07, y1=0.75,
                fillcolor=color + "30", line=dict(color=color, width=2),
            )
            fig.add_annotation(x=x, y=0.5, xref="paper", yref="paper",
                text=label, showarrow=False,
                font=dict(color="white", size=10, family="Sora"),
                align="center",
            )
            if i < len(steps) - 1:
                next_x = steps[i+1][2]
                fig.add_annotation(
                    x=(x + next_x) / 2, y=0.5, xref="paper", yref="paper",
                    text="→", showarrow=False,
                    font=dict(color="#F5A623", size=20),
                )

        # Final SEJI box
        fig.add_shape(type="rect",
            xref="paper", yref="paper",
            x0=0.87, y0=0.3, x1=1.0, y1=0.7,
            fillcolor="rgba(245,166,35,0.15)",
            line=dict(color="#F5A623", width=2),
        )
        fig.add_annotation(x=0.935, y=0.5, xref="paper", yref="paper",
            text="6. SEJI\nScore", showarrow=False,
            font=dict(color="#F5A623", size=11, family="Sora"),
        )

        fig.update_layout(
            paper_bgcolor="rgba(17,34,64,0.8)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=180,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Concept explanation
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="info-card">
                <h4>🎯 Konsep Utama</h4>
                <p>SEJI mengidentifikasi wilayah dengan <strong>potensi surya tinggi + akses listrik rendah + kerentanan sosial tinggi</strong>. 
                Tiga kriteria ini membentuk "sweet spot" intervensi PLTS yang paling berdampak.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="info-card">
                <h4>🛰️ Remote Sensing</h4>
                <p>Data satelit multi-sumber (NASA POWER, VIIRS, MODIS, WorldPop) memberikan coverage nasional 
                dengan resolusi spasial konsisten untuk analisis skala provinsi hingga desa.</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="info-card">
                <h4>☁️ Cloud Computing</h4>
                <p>Proses komputasi menggunakan Google Earth Engine (GEE) untuk pemrosesan data geospatial 
                skala nasional secara efisien tanpa memerlukan infrastruktur lokal yang besar.</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2: Data Sources ──────────────────────────────────────
    with tab2:
        st.markdown("### Sumber Data & Parameter")
        sources = [
            ("☀️ Global Solar Radiation", "NASA POWER / Global Solar Atlas", "±1 km", "4–5.5 kWh/m²/day",
             "Potensi energi surya (GHI)", "#FFD166"),
            ("🌃 Nighttime Light", "VIIRS Day-Night Band (DNB)", "500 m", "Digital Number 0–255",
             "Proksi akses listrik; daerah gelap = akses rendah", "#A0C4FF"),
            ("👥 Kepadatan Penduduk", "WorldPop", "100 m", "jiwa/km²",
             "Estimasi kebutuhan energi dan jangkauan manfaat", "#BDB2FF"),
            ("💸 Tingkat Kemiskinan", "BPS Indonesia", "Administratif", "%",
             "Kerentanan sosial ekonomi masyarakat", "#FF9F43"),
            ("🔌 Jaringan Listrik", "OpenStreetMap / PLN", "Vektor", "Polyline",
             "Akses infrastruktur transmisi dan distribusi", "#06D6A0"),
            ("🗺️ Batas Administrasi", "BIG / GADM", "Vektor", "Polygon",
             "Unit analisis (provinsi, kabupaten/kota)", "#8338EC"),
            ("☁️ Tutupan Awan", "MODIS Cloud Fraction (MOD06)", "1 km", "Fraction 0–1",
             "Variabilitas radiasi matahari akibat awan", "#FF6B6B"),
        ]

        for icon_name, source, res, unit, func, color in sources:
            st.markdown(f"""
            <div style='background:#112240; border-left:4px solid {color};
                        border-radius:8px; padding:1rem; margin:0.5rem 0;
                        display:flex; align-items:flex-start; gap:1rem;'>
                <div style='font-size:1.5rem;'>{icon_name.split()[0]}</div>
                <div style='flex:1;'>
                    <div style='font-weight:700; color:#E8F4F8;'>{icon_name}</div>
                    <div style='font-size:0.8rem; color:#8892A4;'>
                        📡 <em>{source}</em> · 
                        📐 Resolusi: <strong style='color:{color};'>{res}</strong> · 
                        📏 Unit: {unit}
                    </div>
                    <div style='font-size:0.85rem; color:#C0CDD8; margin-top:4px;'>{func}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 3: Formula & AHP ─────────────────────────────────────
    with tab3:
        st.markdown("### Formula SEJI")
        st.markdown("""
        <div style='background:#112240; border:1px solid rgba(245,166,35,0.3);
                    border-radius:10px; padding:1.5rem; text-align:center; margin:1rem 0;'>
            <div style='font-family:Space Mono; font-size:1rem; color:#F5A623; line-height:2;'>
                SEJI = w₁·Solar_norm + w₂·(1−EnergyAccess_norm) + w₃·Poverty_norm<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ w₄·Population_norm + w₅·Remoteness_norm
            </div>
            <hr style='border-color:rgba(245,166,35,0.2); margin:1rem 0;'>
            <div style='font-family:Space Mono; font-size:0.85rem; color:#8892A4;'>
                X_norm = (X − X_min) / (X_max − X_min) ∈ [0, 1]
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AHP Pairwise matrix visualization
        st.markdown("### Matriks Perbandingan Berpasangan AHP")
        params = ["Solar", "E.Access", "Poverty", "Pop.", "Remote."]
        # Simplified AHP matrix (1 = equal, higher = more important)
        matrix = np.array([
            [1,   1,   3/2, 3,   3],
            [1,   1,   3/2, 3,   3],
            [2/3, 2/3, 1,   2,   2],
            [1/3, 1/3, 1/2, 1,   1],
            [1/3, 1/3, 1/2, 1,   1],
        ])

        fig_ahp = go.Figure(go.Heatmap(
            z=matrix,
            x=params, y=params,
            colorscale=[[0, "#0D1B2A"], [0.5, "#112240"], [1, "#F5A623"]],
            text=[[f"{v:.2f}" for v in row] for row in matrix],
            texttemplate="%{text}",
            textfont=dict(size=12, color="white"),
        ))
        fig_ahp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8F4F8", family="Sora"),
            height=300,
            title=dict(text="AHP Pairwise Comparison Matrix", font=dict(color="#F5A623")),
            xaxis=dict(title="Kriteria"), yaxis=dict(title="Kriteria"),
        )
        st.plotly_chart(fig_ahp, use_container_width=True)

        col_r, col_s = st.columns(2)
        with col_r:
            st.markdown("""
            <div class="info-card">
                <h4>📏 Skala Saaty</h4>
                <p>
                1 = Sama pentingnya<br>
                3 = Sedikit lebih penting<br>
                5 = Lebih penting<br>
                7 = Sangat lebih penting<br>
                9 = Mutlak lebih penting
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_s:
            st.markdown("""
            <div class="info-card">
                <h4>✅ Klasifikasi SEJI Score</h4>
                <p>
                <span style='color:#FF4560;'>■</span> <strong>Critical</strong> : &gt; 75<br>
                <span style='color:#F5A623;'>■</span> <strong>High</strong>     : 55 – 75<br>
                <span style='color:#00B4A6;'>■</span> <strong>Moderate</strong>: 33 – 55<br>
                <span style='color:#39D353;'>■</span> <strong>Low</strong>      : &lt; 33
                </p>
            </div>
            """, unsafe_allow_html=True)

        # References
        st.markdown("### 📚 Referensi")
        refs = [
            ("IRENA, 2023", "Renewable Power Generation Costs in 2022"),
            ("ESDM, 2022", "Rencana Umum Energi Nasional (RUEN)"),
            ("Bappenas, 2021", "Laporan Percepatan Pembangunan Daerah Tertinggal"),
            ("Sovacool et al., 2017", "Energy Justice and Energy Transitions"),
            ("Kumar et al., 2020", "GIS-based multi-criteria approach for solar energy"),
        ]
        for author, title in refs:
            st.markdown(f"- **{author}** — *{title}*")
