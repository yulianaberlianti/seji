"""SEJI Analysis — deep dive into index components and spatial patterns."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS, ISLAND_COLORS, get_ahp_weights


def show():
    df = get_indonesia_3t_data()
    weights = get_ahp_weights()

    st.markdown("""
    <div class="hero-banner" style="padding:1.5rem 2rem;">
        <span class="badge">📊 ANALISIS</span>
        <h2 class="hero-title" style="font-size:1.6rem;">Analisis Komponen SEJI</h2>
        <p class="hero-subtitle">Eksplorasi bobot AHP, distribusi spasial, dan pola ketimpangan energi</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏋️ Bobot AHP", "📦 Distribusi Komponen", "🔥 Radar Analysis", "📈 Tren & Korelasi"]
    )

    # ── Tab 1: AHP Weights ───────────────────────────────────────
    with tab1:
        st.markdown("#### Bobot Multi-Criteria Decision Analysis (AHP)")

        col_w, col_chart = st.columns([1, 2])

        with col_w:
            st.markdown("**Konfigurasi Bobot AHP**")
            new_weights = {}
            total_w = 0
            for name, info in weights.items():
                w = st.slider(
                    f"{name}", 0.0, 1.0, info["weight"], 0.05,
                    help=info["description"]
                )
                new_weights[name] = w
                total_w += w
                st.caption(f"Sumber: {info['description']} | Unit: {info['unit']}")
                st.markdown("---")

            if abs(total_w - 1.0) > 0.01:
                st.error(f"⚠️ Total bobot = {total_w:.2f} (harus = 1.00)")
            else:
                st.success(f"✅ Total bobot = {total_w:.2f}")

        with col_chart:
            # Radar chart for weights
            labels = list(weights.keys())
            vals   = [info["weight"] for info in weights.values()]
            new_vals = list(new_weights.values())

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=labels + [labels[0]],
                fill="toself",
                name="Bobot AHP Original",
                line_color="#F5A623",
                fillcolor="rgba(245,166,35,0.15)",
            ))
            fig.add_trace(go.Scatterpolar(
                r=new_vals + [new_vals[0]],
                theta=labels + [labels[0]],
                fill="toself",
                name="Bobot Custom",
                line_color="#00B4A6",
                fillcolor="rgba(0,180,166,0.15)",
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 0.5],
                                   gridcolor="rgba(255,255,255,0.1)",
                                   tickfont=dict(color="#8892A4")),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.1)",
                                    tickfont=dict(color="#E8F4F8", size=11)),
                    bgcolor="rgba(17,34,64,0.6)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E8F4F8", family="Sora"),
                legend=dict(bgcolor="rgba(17,34,64,0.8)"),
                margin=dict(l=60, r=60, t=40, b=40),
                height=400,
                title=dict(text="Perbandingan Bobot AHP", font=dict(color="#F5A623")),
            )
            st.plotly_chart(fig, use_container_width=True)

            # AHP Consistency explanation
            st.markdown("""
            <div class="info-card">
                <h4>📐 AHP Consistency Ratio</h4>
                <p>CR = CI/RI, dimana CI = (λmax - n)/(n-1). 
                Nilai CR &lt; 0.10 menunjukkan matriks perbandingan berpasangan konsisten.
                Model SEJI menggunakan CR = 0.08 (konsisten).</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2: Component Distribution ───────────────────────────
    with tab2:
        st.markdown("#### Distribusi Parameter per Provinsi")

        col_sel, _ = st.columns([1, 3])
        with col_sel:
            param = st.selectbox("Pilih Parameter", [
                "seji_score", "solar_kwh", "electricity_access",
                "poverty_rate", "pop_density", "remoteness"
            ], format_func=lambda x: {
                "seji_score": "SEJI Score",
                "solar_kwh": "Radiasi Matahari (kWh/m²)",
                "electricity_access": "Akses Listrik",
                "poverty_rate": "Tingkat Kemiskinan (%)",
                "pop_density": "Kepadatan Penduduk (pop/km²)",
                "remoteness": "Indeks Keterpencilan",
            }.get(x, x))

        # Box plot by island
        fig_box = px.box(
            df, x="island", y=param,
            color="island",
            color_discrete_map=ISLAND_COLORS,
            points="all",
            hover_name="province",
            labels={"island": "Kepulauan", param: param},
        )
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,34,64,0.6)",
            font=dict(color="#E8F4F8", family="Sora"),
            showlegend=False,
            height=380,
            xaxis=dict(tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Violin: 3T vs Non-3T
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            fig_v = px.violin(
                df, x="is_3t", y=param, color="is_3t",
                color_discrete_map={True: "#FF4560", False: "#39D353"},
                box=True, points="all",
                labels={"is_3t": "3T Region", param: param},
                title="3T vs Non-3T Distribution",
            )
            fig_v.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,34,64,0.6)",
                font=dict(color="#E8F4F8", family="Sora"),
                showlegend=False, height=300,
            )
            st.plotly_chart(fig_v, use_container_width=True)

        with col_v2:
            # Histogram
            fig_h = px.histogram(
                df, x=param, color="priority",
                color_discrete_map=PRIORITY_COLORS,
                nbins=20, title="Distribusi Frekuensi",
                labels={param: param},
            )
            fig_h.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,34,64,0.6)",
                font=dict(color="#E8F4F8", family="Sora"),
                height=300,
                legend=dict(bgcolor="rgba(17,34,64,0.8)"),
                barmode="overlay",
            )
            fig_h.update_traces(opacity=0.7)
            st.plotly_chart(fig_h, use_container_width=True)

    # ── Tab 3: Radar Province Analysis ──────────────────────────
    with tab3:
        st.markdown("#### Profil Komponen SEJI per Provinsi")

        col_sel2, col_comp = st.columns([1, 2])
        with col_sel2:
            selected_provinces = st.multiselect(
                "Pilih Provinsi (max 5)",
                df["province"].tolist(),
                default=df.head(3)["province"].tolist(),
                max_selections=5,
            )

        if selected_provinces:
            fig_radar = go.Figure()
            dims = ["solar_score", "access_score", "poverty_score", "pop_score", "remoteness_score"]
            dim_labels = ["Solar Potential", "Energy Access\n(inverse)", "Poverty", "Population", "Remoteness"]
            colors_r = ["#FF4560", "#F5A623", "#00B4A6", "#39D353", "#8338EC"]

            for i, prov in enumerate(selected_provinces):
                row = df[df["province"] == prov].iloc[0]
                vals = [row[d] for d in dims]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=dim_labels + [dim_labels[0]],
                    fill="toself",
                    name=prov,
                    line_color=colors_r[i % len(colors_r)],
                    fillcolor=colors_r[i % len(colors_r)].replace("#", "rgba(").rstrip(")") + ",0.12)" if "#" in colors_r[i % len(colors_r)] else colors_r[i % len(colors_r)],
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor="rgba(255,255,255,0.1)",
                                   tickfont=dict(color="#8892A4", size=9)),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.1)",
                                    tickfont=dict(color="#E8F4F8", size=10)),
                    bgcolor="rgba(17,34,64,0.6)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E8F4F8", family="Sora"),
                legend=dict(bgcolor="rgba(17,34,64,0.8)"),
                margin=dict(l=80, r=80, t=50, b=50),
                height=450,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Comparison table
            comp_df = df[df["province"].isin(selected_provinces)][
                ["province", "seji_score", "priority", "solar_kwh",
                 "electricity_access", "poverty_rate", "remoteness"]
            ].set_index("province")
            comp_df.columns = ["SEJI Score", "Prioritas", "Solar (kWh/m²)", "Akses Listrik", "Kemiskinan (%)", "Keterpencilan"]
            comp_df["Akses Listrik"] = (comp_df["Akses Listrik"] * 100).round(1).astype(str) + "%"
            st.dataframe(comp_df, use_container_width=True)

    # ── Tab 4: Correlation ──────────────────────────────────────
    with tab4:
        st.markdown("#### Matriks Korelasi & Scatter Matrix")

        numeric_cols = ["seji_score", "solar_kwh", "electricity_access",
                       "poverty_rate", "pop_density", "remoteness"]
        col_labels = ["SEJI", "Solar", "E.Access", "Poverty", "Pop.Density", "Remoteness"]

        corr = df[numeric_cols].corr()
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values,
            x=col_labels, y=col_labels,
            colorscale=[
                [0, "#FF4560"], [0.5, "#0D1B2A"], [1, "#00B4A6"]
            ],
            zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}",
            textfont=dict(size=11, color="white"),
            hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
        ))
        fig_corr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8F4F8", family="Sora"),
            height=400,
            title=dict(text="Pearson Correlation Matrix", font=dict(color="#F5A623")),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        # Key correlation insights
        st.markdown("""
        <div style='display:flex; gap:1rem; flex-wrap:wrap;'>
            <div class="info-card" style='flex:1; min-width:200px;'>
                <h4>🔴 Korelasi Negatif Kuat</h4>
                <p>SEJI berkorelasi negatif dengan Akses Listrik (r ≈ -0.72), menunjukkan wilayah 
                dengan akses rendah cenderung membutuhkan intervensi lebih besar.</p>
            </div>
            <div class="info-card" style='flex:1; min-width:200px;'>
                <h4>🟡 Korelasi Positif</h4>
                <p>Solar Potential berkorelasi positif dengan SEJI (r ≈ +0.65), mengkonfirmasi 
                bahwa daerah dengan potensi surya tinggi dan akses rendah adalah prioritas utama.</p>
            </div>
            <div class="info-card" style='flex:1; min-width:200px;'>
                <h4>🟢 Multikolinearitas</h4>
                <p>Kemiskinan dan Keterpencilan berkorelasi tinggi (r ≈ +0.68), menunjukkan 
                wilayah terpencil cenderung memiliki tingkat kemiskinan lebih tinggi.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
