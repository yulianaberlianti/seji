"""Optimal Location Finder — spatial query + highlight. v3.0"""

import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS
import plotly.express as px


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">🎯 LOCATION FINDER</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Optimal Location Finder</h2>
        <p class="hero-subtitle">Masukkan kriteria spasial → sistem otomatis menyoroti wilayah yang memenuhi syarat</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Query Builder ─────────────────────────────────────────────
    st.markdown("### 🔧 Kriteria Pencarian")
    with st.expander("☀️ Filter Potensi Surya", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            solar_min = st.slider("Radiasi Min (kWh/m²/hari)", 3.5, 6.5, 4.8, 0.1,
                                  help="Ambang batas minimum radiasi matahari")
        with c2:
            solar_max = st.slider("Radiasi Max (kWh/m²/hari)", 3.5, 6.5, 6.5, 0.1)

    with st.expander("⚡ Filter Akses Energi", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            acc_min = st.slider("Akses Listrik Min (%)", 0, 100, 0, 1)
        with c2:
            acc_max = st.slider("Akses Listrik Max (%)", 0, 100, 50, 1,
                                help="Wilayah dengan akses < 50% = target utama")

    with st.expander("💸 Filter Sosial Ekonomi"):
        c1, c2 = st.columns(2)
        with c1:
            pov_min = st.slider("Kemiskinan Min (%)", 0.0, 45.0, 0.0, 0.5)
        with c2:
            pov_min2 = st.slider("Kemiskinan Max (%)", 0.0, 45.0, 45.0, 0.5)

    with st.expander("📊 Filter SEJI & Lainnya"):
        c1, c2, c3 = st.columns(3)
        with c1:
            seji_min = st.slider("SEJI Score Min", 0, 100, 0, 1)
        with c2:
            only_3t = st.checkbox("Hanya Wilayah 3T", value=False)
        with c3:
            island_filter = st.selectbox("Kepulauan", ["Semua"] + sorted(df["island"].unique().tolist()))

    # ── Apply Query ───────────────────────────────────────────────
    filt = df.copy()
    filt = filt[filt["solar_kwh"].between(solar_min, solar_max)]
    filt = filt[filt["electricity_access"].between(acc_min / 100, acc_max / 100)]
    filt = filt[filt["poverty_rate"].between(pov_min, pov_min2)]
    filt = filt[filt["seji_score"] >= seji_min]
    if only_3t:
        filt = filt[filt["is_3t"]]
    if island_filter != "Semua":
        filt = filt[filt["island"] == island_filter]

    match_count = len(filt)
    total = len(df)

    # ── Result Summary ────────────────────────────────────────────
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Wilayah Ditemukan", f"{match_count}", f"dari {total} provinsi")
    with r2:
        val = filt["seji_score"].mean() if match_count > 0 else 0
        st.metric("Rata-rata SEJI", f"{val:.1f}", help="Skor rata-rata hasil filter")
    with r3:
        val2 = filt["solar_kwh"].mean() if match_count > 0 else 0
        st.metric("Avg Solar", f"{val2:.2f} kWh/m²")
    with r4:
        val3 = (filt["electricity_access"].mean() * 100) if match_count > 0 else 0
        st.metric("Avg Akses Listrik", f"{val3:.1f}%")

    if match_count == 0:
        st.warning("⚠️ Tidak ada wilayah yang memenuhi semua kriteria. Coba longgarkan filter.")
        return

    # ── Map ───────────────────────────────────────────────────────
    st.markdown(f"### 🗺️ Peta Hasil Query — **{match_count} wilayah** ditemukan")
    st.caption("Lingkaran kuning besar = hasil query · Lingkaran abu-abu kecil = tidak memenuhi syarat")

    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles=None, prefer_canvas=True)
    folium.TileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        name="Dark", attr="CartoDB", max_zoom=19,
    ).add_to(m)
    folium.TileLayer("OpenStreetMap", name="OSM", attr="OSM").add_to(m)

    # Non-matching markers (dimmed)
    non_match = df[~df["province"].isin(filt["province"])]
    for _, r in non_match.iterrows():
        folium.CircleMarker(
            location=[r["lat"], r["lon"]], radius=5,
            color="#334455", fill=True, fill_color="#334455",
            fill_opacity=0.4, weight=1,
            tooltip=f"{r['province']} — tidak memenuhi kriteria",
        ).add_to(m)

    # Matching markers (highlighted)
    match_group = folium.FeatureGroup(name="✅ Wilayah Optimal", show=True)
    if len(filt) > 0:
        heat_data = [[r["lat"], r["lon"], r["seji_score"] / 100] for _, r in filt.iterrows()]
        HeatMap(heat_data, name="Heatmap Optimal",
                min_opacity=0.35, radius=70, blur=50,
                gradient={0.3: "#F5A623", 0.7: "#FF8C00", 1.0: "#FF4560"},
                ).add_to(m)

    for rank, (_, r) in enumerate(filt.sort_values("seji_score", ascending=False).iterrows(), 1):
        pc = PRIORITY_COLORS.get(str(r["priority"]), "#F5A623")
        rad = 10 + r["seji_score"] / 14

        popup_html = f"""
        <div style="font-family:Arial;width:260px;background:#0B1623;color:#E8F0F8;
                    border-radius:10px;padding:14px;border:2px solid {pc};">
            <div style="font-size:0.72rem;color:#F5A623;font-weight:700;">#{rank} HASIL QUERY</div>
            <div style="font-size:1rem;font-weight:700;color:#F5A623;margin:3px 0;">{r['province']}</div>
            <div style="font-size:0.7rem;color:#7A94B0;margin-bottom:8px;">
                {'🔴 3T' if r['is_3t'] else '⚪ Non-3T'} · {r['island']}
            </div>
            <div style="display:flex;align-items:center;gap:10px;background:#112240;
                        border-radius:7px;padding:8px;margin-bottom:8px;">
                <span style="font-size:1.6rem;font-weight:800;color:{pc};">{r['seji_score']:.1f}</span>
                <div>
                    <div style="font-size:0.68rem;color:#7A94B0;">SEJI Score</div>
                    <div style="font-size:0.74rem;font-weight:700;color:{pc};">{r['priority']} Priority</div>
                </div>
            </div>
            <table style="width:100%;font-size:0.75rem;border-collapse:collapse;">
                <tr><td style="color:#7A94B0;padding:3px 2px;">☀️ Solar</td>
                    <td style="text-align:right;color:#FFD166;font-weight:600;">{r['solar_kwh']:.2f} kWh/m²/day</td></tr>
                <tr><td style="color:#7A94B0;padding:3px 2px;">⚡ Akses</td>
                    <td style="text-align:right;color:#06D6A0;font-weight:600;">{r['electricity_access']*100:.1f}%</td></tr>
                <tr><td style="color:#7A94B0;padding:3px 2px;">💸 Miskin</td>
                    <td style="text-align:right;color:#FF6B6B;font-weight:600;">{r['poverty_rate']:.1f}%</td></tr>
            </table>
        </div>"""

        folium.CircleMarker(
            location=[r["lat"], r["lon"]], radius=rad,
            color="#F5A623", fill=True, fill_color=pc,
            fill_opacity=0.85, weight=2.5,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"<b>#{rank} {r['province']}</b> — SEJI: {r['seji_score']:.1f}",
        ).add_to(match_group)

    match_group.add_to(m)
    folium.LayerControl(position="topright").add_to(m)

    st_folium(m, width="100%", height=500, returned_objects=[])

    # ── Ranked Table ──────────────────────────────────────────────
    st.markdown("### 📋 Ranking Hasil Query")
    display = filt.sort_values("seji_score", ascending=False)[
        ["province", "island", "is_3t", "seji_score", "priority",
         "solar_kwh", "electricity_access", "poverty_rate", "remoteness"]
    ].copy()
    display.insert(0, "Rank", range(1, len(display) + 1))
    display["electricity_access"] = (display["electricity_access"] * 100).round(1).astype(str) + "%"
    display["is_3t"] = display["is_3t"].map({True: "✅ 3T", False: "❌"})
    display.columns = ["Rank", "Provinsi", "Kepulauan", "3T", "SEJI", "Prioritas",
                       "Solar (kWh/m²)", "Akses Listrik", "Miskin (%)", "Keterpencilan"]
    st.dataframe(display.set_index("Rank"), use_container_width=True,
                 column_config={"SEJI": st.column_config.ProgressColumn("SEJI", min_value=0, max_value=100, format="%.1f")})

    # ── Why These Locations? Chart ────────────────────────────────
    if match_count >= 2:
        st.markdown("### 📊 Perbandingan Parameter Wilayah Optimal")
        fig = px.bar(
            filt.sort_values("seji_score", ascending=False).head(10),
            x="province", y=["solar_score", "access_score", "poverty_score"],
            barmode="group",
            color_discrete_map={"solar_score": "#FFD166", "access_score": "#FF6B6B", "poverty_score": "#A29BFE"},
            labels={"value": "Score (0-100)", "province": "Provinsi"},
            title="Komponen Score — Top 10 Hasil Query",
        )
        fig.update_layout(
            paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
            plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
            font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
            height=350,
            legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
            xaxis=dict(tickangle=-30),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Download results
    st.download_button(
        "⬇️ Download Hasil Query (CSV)",
        filt.to_csv(index=False),
        "optimal_locations.csv", "text/csv"
    )
