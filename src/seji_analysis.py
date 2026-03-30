"""SEJI Analysis — AHP weights, distributions, radar, correlations. v2.0"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS, ISLAND_COLORS, get_ahp_weights


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})
    weights = get_ahp_weights()

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">📊 ANALISIS</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Analisis Komponen SEJI</h2>
        <p class="hero-subtitle">Eksplorasi bobot AHP, distribusi spasial, radar per provinsi, dan korelasi</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Bobot AHP", "📦 Distribusi", "🔥 Radar Provinsi", "📈 Korelasi"])

    # ── Tab 1: AHP ───────────────────────────────────────────────
    with tab1:
        st.markdown("#### Konfigurasi Bobot Multi-Criteria Decision Analysis (AHP)")
        c_sl, c_ch = st.columns([1, 2])
        nw = {}
        with c_sl:
            total_w = 0
            for name, info in weights.items():
                w = st.slider(f"{name}", 0.0, 1.0, info["weight"], 0.05,
                              help=f"{info['description']} | Unit: {info['unit']}")
                nw[name] = w; total_w += w
                st.caption(f"_{info['description']}_")
            if abs(total_w - 1.0) > 0.01:
                st.error(f"⚠️ Total bobot = {total_w:.2f} — harus 1.00")
            else:
                st.success(f"✅ Total bobot = {total_w:.2f}")

        with c_ch:
            lbls  = list(weights.keys())
            orig  = [info["weight"] for info in weights.values()]
            cust  = list(nw.values())
            fig = go.Figure()
            for vals, name, col in [(orig,"Bobot AHP Original","#F5A623"),(cust,"Bobot Custom","#00C4B4")]:
                fig.add_trace(go.Scatterpolar(
                    r=vals+[vals[0]], theta=lbls+[lbls[0]],
                    fill="toself", name=name,
                    line_color=col, fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.18)",
                    opacity=0.85,
                ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0,0.5],
                                   gridcolor=cc.get("grid","rgba(255,255,255,0.06)"),
                                   tickfont=dict(color=cc.get("text","#C8D8E8"), size=9)),
                    angularaxis=dict(gridcolor=cc.get("grid","rgba(255,255,255,0.06)"),
                                    tickfont=dict(color=cc.get("text","#C8D8E8"), size=10)),
                    bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
                ),
                paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
                font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
                legend=dict(bgcolor=cc.get("legend","rgba(7,17,32,0.88)"), borderwidth=0),
                margin=dict(l=60,r=60,t=40,b=40), height=400,
                title=dict(text="Radar Perbandingan Bobot", font=dict(color="#F5A623",size=13)),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
            <div class="info-card">
                <h4>📐 Consistency Ratio AHP</h4>
                <p>CR = CI/RI, CI = (λmax − n)/(n−1). Nilai CR &lt; 0.10 berarti matriks perbandingan
                konsisten. Model SEJI menggunakan CR = 0.08 ✅</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2: Distribution ──────────────────────────────────────
    with tab2:
        st.markdown("#### Distribusi Parameter per Kepulauan")
        param = st.selectbox("Pilih Parameter", [
            "seji_score","solar_kwh","electricity_access",
            "poverty_rate","pop_density","remoteness",
        ], format_func=lambda x: {
            "seji_score":"SEJI Score","solar_kwh":"Radiasi Matahari (kWh/m²)",
            "electricity_access":"Akses Listrik (ratio)","poverty_rate":"Tingkat Kemiskinan (%)",
            "pop_density":"Kepadatan Penduduk (pop/km²)","remoteness":"Indeks Keterpencilan",
        }.get(x,x))

        # Box plot
        fig_box = px.box(df, x="island", y=param, color="island",
                         color_discrete_map=ISLAND_COLORS, points="all", hover_name="province")
        fig_box.update_layout(
            paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
            plot_bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
            font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
            showlegend=False, height=360,
            xaxis=dict(gridcolor=cc.get("grid","rgba(255,255,255,0.06)")),
            yaxis=dict(gridcolor=cc.get("grid","rgba(255,255,255,0.06)")),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        cv1, cv2 = st.columns(2)
        with cv1:
            fig_v = px.violin(df, x="is_3t", y=param, color="is_3t",
                              color_discrete_map={True:"#FF4560",False:"#39D353"},
                              box=True, points="all", title="3T vs Non-3T")
            fig_v.update_layout(
                paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
                plot_bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
                font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
                showlegend=False, height=310,
            )
            st.plotly_chart(fig_v, use_container_width=True)
        with cv2:
            fig_h = px.histogram(df, x=param, color="priority",
                                 color_discrete_map=PRIORITY_COLORS,
                                 nbins=18, title="Distribusi Frekuensi", barmode="overlay")
            fig_h.update_traces(opacity=0.72)
            fig_h.update_layout(
                paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
                plot_bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
                font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
                height=310, legend=dict(bgcolor=cc.get("legend","rgba(7,17,32,0.88)")),
            )
            st.plotly_chart(fig_h, use_container_width=True)

    # ── Tab 3: Radar per Province ────────────────────────────────
    with tab3:
        st.markdown("#### Profil Komponen SEJI per Provinsi")
        sel = st.multiselect("Pilih Provinsi (max 5)", df["province"].tolist(),
                             default=df.head(3)["province"].tolist(), max_selections=5)
        if sel:
            dims   = ["solar_score","access_score","poverty_score","pop_score","remoteness_score"]
            dlabels= ["Solar","Energy Access\n(inv.)","Poverty","Population","Remoteness"]
            pal    = ["#FF4560","#F5A623","#00C4B4","#39D353","#8338EC"]
            fig_r  = go.Figure()
            for i, prov in enumerate(sel):
                row  = df[df["province"]==prov].iloc[0]
                vals = [row[d] for d in dims]
                col  = pal[i % len(pal)]
                fig_r.add_trace(go.Scatterpolar(
                    r=vals+[vals[0]], theta=dlabels+[dlabels[0]],
                    fill="toself", name=prov,
                    line_color=col,
                    fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.13)",
                ))
            fig_r.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True,range=[0,100],
                                   gridcolor=cc.get("grid","rgba(255,255,255,0.06)"),
                                   tickfont=dict(color=cc.get("text","#C8D8E8"),size=9)),
                    angularaxis=dict(gridcolor=cc.get("grid","rgba(255,255,255,0.06)"),
                                    tickfont=dict(color=cc.get("text","#C8D8E8"),size=10)),
                    bgcolor=cc.get("plot","rgba(17,34,64,0.85)"),
                ),
                paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
                font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
                legend=dict(bgcolor=cc.get("legend","rgba(7,17,32,0.88)")),
                margin=dict(l=80,r=80,t=50,b=50), height=450,
            )
            st.plotly_chart(fig_r, use_container_width=True)
            comp = df[df["province"].isin(sel)][
                ["province","seji_score","priority","solar_kwh",
                 "electricity_access","poverty_rate","remoteness"]
            ].set_index("province")
            comp["electricity_access"] = (comp["electricity_access"]*100).round(1).astype(str)+"%"
            comp.columns = ["SEJI","Prioritas","Solar (kWh/m²)","Akses Listrik","Kemiskinan (%)","Keterpencilan"]
            st.dataframe(comp, use_container_width=True)

    # ── Tab 4: Correlation ───────────────────────────────────────
    with tab4:
        st.markdown("#### Matriks Korelasi Pearson")
        num_cols  = ["seji_score","solar_kwh","electricity_access","poverty_rate","pop_density","remoteness"]
        col_lbls  = ["SEJI","Solar","E.Access","Poverty","Pop.Density","Remoteness"]
        corr = df[num_cols].corr()
        fig_c = go.Figure(go.Heatmap(
            z=corr.values, x=col_lbls, y=col_lbls,
            colorscale=[[0,"#FF4560"],[0.5,"#112240"],[1,"#00C4B4"]],
            zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}", textfont=dict(size=11,color="white"),
            hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
        ))
        fig_c.update_layout(
            paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
            font=dict(color=cc.get("text","#C8D8E8"), family="Plus Jakarta Sans"),
            height=400, title=dict(text="Pearson Correlation Matrix", font=dict(color="#F5A623")),
        )
        st.plotly_chart(fig_c, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="info-card"><h4>🔴 Korelasi Negatif</h4>
            <p>SEJI ↔ Akses Listrik (r ≈ −0.72): daerah akses rendah = prioritas intervensi lebih tinggi.</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="info-card"><h4>🟡 Korelasi Positif</h4>
            <p>Solar ↔ SEJI (r ≈ +0.65): konfirmasi bahwa daerah surya tinggi + akses rendah = prioritas utama.</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="info-card"><h4>🟢 Co-linearity</h4>
            <p>Kemiskinan ↔ Keterpencilan (r ≈ +0.68): wilayah terpencil cenderung lebih miskin.</p>
            </div>""", unsafe_allow_html=True)
