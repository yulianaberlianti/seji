"""Methodology page. v2.0"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show():
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">ℹ️ METODOLOGI</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Kerangka Metodologi SEJI</h2>
        <p class="hero-subtitle">Framework analisis spasial — Remote Sensing · GIS · MCDA/AHP</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📐 Kerangka SEJI","📡 Sumber Data","🧮 Formula & AHP"])

    with tab1:
        st.markdown("### Alur Metodologi (6 Tahap)")
        steps = [
            ("1\nPengumpulan\nData","#F5A623"),
            ("2\nPra-Proses\n& Koreksi","#FF8C00"),
            ("3\nEkstraksi\nParameter","#00C4B4"),
            ("4\nNormalisasi\n(0–1)","#39D353"),
            ("5\nMCDA/AHP\nPembobotan","#8338EC"),
            ("6\nSEJI\nScore","#FF4560"),
        ]
        cols = st.columns(len(steps))
        for col, (label, color) in zip(cols, steps):
            with col:
                parts = label.split("\n")
                num   = parts[0]
                title = "\n".join(parts[1:])
                st.markdown(f"""
                <div style='background:var(--bg-card);border:2px solid {color}55;
                            border-radius:12px;padding:0.9rem;text-align:center;
                            border-top:3px solid {color};'>
                    <div style='font-size:1.4rem;font-weight:800;color:{color};
                                font-family:Space Mono;'>{num}</div>
                    <div style='font-size:0.72rem;color:var(--text-secondary);
                                margin-top:4px;line-height:1.4;'>{title}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="info-card"><h4>🎯 Konsep Utama</h4>
            <p>SEJI mengidentifikasi wilayah dengan <b>potensi surya tinggi + akses listrik rendah
            + kerentanan sosial tinggi</b>. Tiga kriteria membentuk "sweet spot" intervensi PLTS yang paling berdampak.</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="info-card"><h4>🛰️ Remote Sensing</h4>
            <p>Data multi-sumber (NASA POWER, VIIRS DNB, MODIS, WorldPop) memberikan coverage nasional
            dengan resolusi spasial konsisten. Komputasi via Google Earth Engine (GEE).</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="info-card"><h4>⚖️ Energy Justice</h4>
            <p>Berdasarkan framework Sovacool et al. (2017): transisi energi harus mengurangi
            ketimpangan sosial-geografis, bukan hanya mengurangi emisi karbon.</p>
            </div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### Sumber Data & Parameter")
        sources = [
            ("☀️ Global Solar Radiation","NASA POWER / Global Solar Atlas","±1 km","kWh/m²/day","Potensi energi surya (GHI)","#FFD166"),
            ("🌃 Nighttime Light","VIIRS Day-Night Band (DNB)","500 m","DN 0–255","Proksi akses listrik; gelap = akses rendah","#A0C4FF"),
            ("👥 Kepadatan Penduduk","WorldPop","100 m","jiwa/km²","Estimasi kebutuhan dan jangkauan manfaat","#BDB2FF"),
            ("💸 Tingkat Kemiskinan","BPS Indonesia","Administratif","%","Kerentanan sosial ekonomi masyarakat","#FF9F43"),
            ("🔌 Jaringan Listrik","OpenStreetMap / PLN","Vektor","Polyline","Akses infrastruktur distribusi","#06D6A0"),
            ("🗺️ Batas Administrasi","BIG / GADM","Vektor","Polygon","Unit analisis provinsi & kabupaten","#8338EC"),
            ("☁️ Tutupan Awan","MODIS MOD06 Cloud Fraction","1 km","Fraction 0–1","Variabilitas radiasi akibat awan","#FF6B6B"),
        ]
        for icon, src, res, unit, fn, col in sources:
            st.markdown(f"""
            <div style='background:var(--bg-card);border-left:4px solid {col};
                        border-radius:10px;padding:0.95rem 1.2rem;margin:0.45rem 0;
                        display:flex;align-items:flex-start;gap:14px;'>
                <div style='font-size:1.4rem;flex-shrink:0;'>{icon.split()[0]}</div>
                <div style='flex:1;'>
                    <div style='font-weight:700;color:var(--text-primary);font-size:0.92rem;'>{icon}</div>
                    <div style='font-size:0.76rem;color:var(--text-muted);margin:2px 0;'>
                        📡 <em>{src}</em> &nbsp;·&nbsp;
                        📐 Resolusi: <strong style='color:{col};'>{res}</strong> &nbsp;·&nbsp;
                        📏 {unit}
                    </div>
                    <div style='font-size:0.84rem;color:var(--text-secondary);'>{fn}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### Formula SEJI")
        st.markdown("""
        <div style='background:var(--bg-card);border:1px solid rgba(245,166,35,0.3);
                    border-radius:12px;padding:1.6rem;text-align:center;margin:1rem 0;'>
            <div style='font-family:Space Mono;font-size:0.95rem;color:#F5A623;line-height:2.2;'>
                SEJI = w₁·Solar<sub>norm</sub> + w₂·(1−EnergyAccess<sub>norm</sub>) + w₃·Poverty<sub>norm</sub><br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ w₄·Population<sub>norm</sub> + w₅·Remoteness<sub>norm</sub>
            </div>
            <hr style='border-color:rgba(245,166,35,0.2);margin:1rem 0;'>
            <div style='font-family:Space Mono;font-size:0.82rem;color:var(--text-muted);'>
                X<sub>norm</sub> = (X − X<sub>min</sub>) / (X<sub>max</sub> − X<sub>min</sub>) ∈ [0, 1]
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Bobot AHP Transparan")
        params   = ["Solar (w=0.30)","E.Access (w=0.30)","Poverty (w=0.20)","Pop. (w=0.10)","Remote. (w=0.10)"]
        matrix   = np.array([
            [1,   1,   1.5, 3,   3],
            [1,   1,   1.5, 3,   3],
            [0.67,0.67,1,   2,   2],
            [0.33,0.33,0.5, 1,   1],
            [0.33,0.33,0.5, 1,   1],
        ])
        fig = go.Figure(go.Heatmap(
            z=matrix, x=params, y=params,
            colorscale=[[0,"#0B1623"],[0.5,"#1A3050"],[1,"#F5A623"]],
            text=[[f"{v:.2f}" for v in row] for row in matrix],
            texttemplate="%{text}", textfont=dict(size=11,color="white"),
        ))
        fig.update_layout(
            paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
            font=dict(color=cc.get("text","#C8D8E8"),family="Plus Jakarta Sans"),
            height=290,
            title=dict(text="AHP Pairwise Comparison Matrix (CR=0.08)", font=dict(color="#F5A623")),
        )
        st.plotly_chart(fig, use_container_width=True)

        cr1, cr2 = st.columns(2)
        with cr1:
            st.markdown("""<div class="info-card"><h4>📏 Skala Saaty</h4>
            <p>1 = Sama pentingnya<br>3 = Sedikit lebih penting<br>5 = Lebih penting<br>
            7 = Sangat lebih penting<br>9 = Mutlak lebih penting</p></div>""", unsafe_allow_html=True)
        with cr2:
            st.markdown("""<div class="info-card"><h4>✅ Klasifikasi SEJI</h4>
            <p><span style='color:#FF4560;'>■</span> <b>Critical</b> : &gt;75<br>
            <span style='color:#F5A623;'>■</span> <b>High</b> : 55–75<br>
            <span style='color:#00C4B4;'>■</span> <b>Moderate</b> : 33–55<br>
            <span style='color:#39D353;'>■</span> <b>Low</b> : &lt;33</p></div>""", unsafe_allow_html=True)

        st.markdown("### 📚 Referensi")
        refs = [
            ("IRENA, 2023","Renewable Power Generation Costs in 2022"),
            ("ESDM, 2022","Rencana Umum Energi Nasional (RUEN)"),
            ("Bappenas, 2021","Laporan Percepatan Pembangunan Daerah Tertinggal"),
            ("Sovacool et al., 2017","Energy Justice: A Conceptual Review. Energy Research & Social Science"),
            ("Kumar et al., 2020","GIS-based multi-criteria approach for solar energy potential analysis"),
        ]
        for author, title in refs:
            st.markdown(f"- **{author}** — *{title}*")
