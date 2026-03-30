"""Interactive SEJI Calculator — user inputs parameters to compute custom SEJI score."""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def show():
    df = get_indonesia_3t_data()

    st.markdown("""
    <div class="hero-banner" style="padding:1.5rem 2rem;">
        <span class="badge">⚙️ KALKULATOR</span>
        <h2 class="hero-title" style="font-size:1.6rem;">SEJI Score Calculator</h2>
        <p class="hero-subtitle">Masukkan parameter wilayah untuk menghitung SEJI Score dan melihat posisi relatifnya</p>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_result = st.columns([2, 3])

    with col_input:
        st.markdown("### 📥 Input Parameter Wilayah")

        location_name = st.text_input("Nama Wilayah/Desa", value="Desa Saya")

        st.markdown("---")
        st.markdown("**☀️ Potensi Energi Surya**")
        solar_kwh = st.slider(
            "Radiasi Matahari (kWh/m²/hari)",
            3.0, 7.0, 5.0, 0.1,
            help="Data dari NASA POWER atau Global Solar Atlas"
        )
        cloud_frac = st.slider(
            "Cloud Fraction (0=cerah, 1=mendung)", 0.0, 1.0, 0.3, 0.05,
            help="Dari MODIS Cloud Fraction"
        )

        st.markdown("**⚡ Akses Energi**")
        elec_access = st.slider(
            "Rasio Akses Listrik (%)", 0, 100, 45, 1,
            help="Persentase rumah tangga berakses listrik"
        )
        ntl = st.slider(
            "Nighttime Light Index (0–1)", 0.0, 1.0, 0.2, 0.05,
            help="Dari VIIRS Day-Night Band; 0=gelap, 1=terang"
        )

        st.markdown("**💸 Sosial Ekonomi**")
        poverty = st.slider(
            "Tingkat Kemiskinan (%)", 0.0, 50.0, 25.0, 0.5,
            help="Data BPS"
        )
        pop_density = st.number_input(
            "Kepadatan Penduduk (jiwa/km²)", 1, 20000, 50, 10,
            help="Data WorldPop"
        )
        remoteness = st.slider(
            "Indeks Keterpencilan (0–1)", 0.0, 1.0, 0.7, 0.05,
            help="0=dekat kota, 1=sangat terpencil"
        )

        st.markdown("---")
        st.markdown("**🏋️ Bobot AHP**")
        w_solar  = st.number_input("w₁ Solar",   0.0, 1.0, 0.30, 0.05)
        w_access = st.number_input("w₂ Access",  0.0, 1.0, 0.30, 0.05)
        w_pov    = st.number_input("w₃ Poverty", 0.0, 1.0, 0.20, 0.05)
        w_pop    = st.number_input("w₄ Pop.",    0.0, 1.0, 0.10, 0.05)
        w_remote = st.number_input("w₅ Remote.", 0.0, 1.0, 0.10, 0.05)
        total_w  = w_solar + w_access + w_pov + w_pop + w_remote

        if abs(total_w - 1.0) > 0.01:
            st.error(f"⚠️ Total bobot = {total_w:.2f} — harus 1.00")
        else:
            st.success(f"✅ Total bobot = {total_w:.2f}")

    with col_result:
        # ── SEJI Computation ─────────────────────────────────────
        # Use dataset min/max for normalization
        solar_min, solar_max = df["solar_kwh"].min(), df["solar_kwh"].max()
        access_min, access_max = df["electricity_access"].min(), df["electricity_access"].max()
        pov_min, pov_max = df["poverty_rate"].min(), df["poverty_rate"].max()
        pop_min, pop_max = df["pop_density"].min(), df["pop_density"].max()
        rem_min, rem_max = df["remoteness"].min(), df["remoteness"].max()

        def norm_val(val, vmin, vmax, invert=False):
            n = (val - vmin) / (vmax - vmin + 1e-9)
            n = max(0, min(1, n))
            return 1 - n if invert else n

        solar_n  = norm_val(solar_kwh, solar_min, solar_max)
        access_n = norm_val(elec_access / 100, access_min, access_max, invert=True)
        pov_n    = norm_val(poverty, pov_min, pov_max)
        pop_n    = norm_val(pop_density, pop_min, pop_max)
        remote_n = norm_val(remoteness, rem_min, rem_max)

        seji = (w_solar * solar_n + w_access * access_n +
                w_pov * pov_n + w_pop * pop_n + w_remote * remote_n) * 100

        seji = round(seji, 1)
        priority = "Critical" if seji > 75 else "High" if seji > 55 else "Moderate" if seji > 33 else "Low"
        pcolor = PRIORITY_COLORS[priority]

        # ── Score Display ─────────────────────────────────────────
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #112240, #1a2f4a);
                    border: 2px solid {pcolor}60; border-radius:16px; padding:2rem;
                    text-align:center; margin-bottom:1.5rem;'>
            <div style='font-size:0.85rem; color:#8892A4; font-family:Space Mono; letter-spacing:2px;'>
                SOLAR ENERGY JUSTICE INDEX
            </div>
            <div style='font-size:5rem; font-weight:800; color:{pcolor};
                        line-height:1; margin:0.5rem 0; font-family:Sora;'>
                {seji}
            </div>
            <div style='font-size:1.1rem; color:#E8F4F8; margin-bottom:0.5rem;'>
                {location_name}
            </div>
            <div style='display:inline-block; background:{pcolor}20; border:1px solid {pcolor};
                        color:{pcolor}; padding:4px 16px; border-radius:20px; font-weight:700;
                        font-size:0.9rem;'>
                {priority.upper()} PRIORITY
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Component breakdown gauge
        components = {
            "Solar Potential": (solar_n * 100, "#FFD166"),
            "Energy Access (inv.)": (access_n * 100, "#FF6B6B"),
            "Poverty": (pov_n * 100, "#FF9F43"),
            "Population Need": (pop_n * 100, "#A29BFE"),
            "Remoteness": (remote_n * 100, "#00CEC9"),
        }

        fig = go.Figure()
        for comp_name, (val, color) in components.items():
            fig.add_trace(go.Bar(
                name=comp_name, x=[val], y=[comp_name],
                orientation="h",
                marker_color=color,
                text=f"{val:.1f}",
                textposition="inside",
                textfont=dict(color="white", size=11, family="Space Mono"),
            ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,34,64,0.6)",
            font=dict(color="#E8F4F8", family="Sora"),
            height=280,
            showlegend=False,
            xaxis=dict(range=[0, 105], gridcolor="rgba(255,255,255,0.05)",
                       title="Normalized Score (0–100)"),
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=10, r=10, t=30, b=40),
            title=dict(text="Komponen Score (sebelum pembobotan)", font=dict(color="#F5A623", size=13)),
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Ranking Comparison ────────────────────────────────────
        st.markdown("### 📍 Posisi Relatif di Antara Provinsi Indonesia")

        # Add user's location to df for comparison
        user_row = {
            "province": f"⭐ {location_name}", "seji_score": seji,
            "priority": priority, "is_3t": remoteness > 0.5,
        }
        compare_df = df[["province", "seji_score", "priority"]].copy()
        user_series = {"province": f"⭐ {location_name}", "seji_score": seji, "priority": priority}
        compare_df = compare_df._append(user_series, ignore_index=True)
        compare_df = compare_df.sort_values("seji_score", ascending=False).reset_index(drop=True)

        user_rank = compare_df[compare_df["province"] == f"⭐ {location_name}"].index[0] + 1
        total_locs = len(compare_df)

        st.markdown(f"""
        <div style='background:#112240; border:1px solid rgba(245,166,35,0.3);
                    border-radius:10px; padding:1rem; text-align:center;'>
            <span style='color:#8892A4; font-size:0.9rem;'>Peringkat Wilayah Anda</span><br>
            <span style='font-size:2.5rem; font-weight:800; color:#F5A623;'>#{user_rank}</span>
            <span style='color:#8892A4;'> dari {total_locs} wilayah</span>
        </div>
        """, unsafe_allow_html=True)

        # Show around user's position
        start = max(0, user_rank - 4)
        end   = min(total_locs, user_rank + 3)
        nearby = compare_df.iloc[start:end].copy()
        nearby.index = range(start + 1, end + 1)
        nearby.index.name = "Rank"
        st.dataframe(
            nearby.rename(columns={"province": "Provinsi/Wilayah",
                                   "seji_score": "SEJI Score", "priority": "Prioritas"}),
            use_container_width=True,
        )

        # ── Recommendation ────────────────────────────────────────
        rec_map = {
            "Critical": ("🚨 Intervensi Segera", "Wilayah ini memiliki SEJI Score tertinggi. Diperlukan instalasi PLTS off-grid segera sebagai solusi energi mandiri. Potensi surya tinggi dengan akses listrik sangat rendah menjadikannya kandidat ideal program PLTS komunal."),
            "High":     ("⚡ Prioritas Tinggi",   "Wilayah ini masuk kategori prioritas tinggi. Perlu perencanaan PLTS terdesentralisasi dalam jangka pendek (1–2 tahun). Pertimbangkan microgrid solar hybrid untuk menjangkau lebih banyak rumah tangga."),
            "Moderate": ("📋 Perencanaan Jangka Menengah", "SEJI Score moderat menunjukkan peluang pengembangan. Wilayah ini bisa menjadi target program PLTS atap bersubsidi atau kemitraan dengan swasta dalam skema KPBU."),
            "Low":      ("✅ Kondisi Relatif Baik",  "Wilayah ini memiliki akses energi yang relatif baik. Fokus pada optimasi efisiensi energi dan peningkatan penetrasi PLTS rooftop sebagai pelengkap jaringan PLN yang sudah ada."),
        }
        rec_title, rec_body = rec_map[priority]
        st.markdown(f"""
        <div style='background: rgba({",".join(str(int(pcolor.lstrip("#")[i:i+2], 16)) for i in (0,2,4))},0.1);
                    border: 1px solid {pcolor}50; border-radius:10px; padding:1.2rem; margin-top:1rem;'>
            <div style='color:{pcolor}; font-weight:700; margin-bottom:0.5rem;'>{rec_title}</div>
            <div style='color:#E8F4F8; font-size:0.9rem; line-height:1.6;'>{rec_body}</div>
        </div>
        """, unsafe_allow_html=True)
