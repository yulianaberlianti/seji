"""WebGIS interactive map page."""

import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap
from streamlit_folium import st_folium
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def show():
    df = get_indonesia_3t_data()

    st.markdown("""
    <div class="hero-banner" style="padding:1.5rem 2rem;">
        <span class="badge">🗺️ WEBGIS</span>
        <h2 class="hero-title" style="font-size:1.6rem;">Peta Interaktif SEJI — Indonesia</h2>
        <p class="hero-subtitle">Klik marker untuk detail. Gunakan layer control kanan atas untuk toggle lapisan.</p>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        map_layer = st.selectbox("Layer Utama", ["SEJI Score", "Solar Radiation", "Energy Access", "Poverty Rate"])
    with col2:
        show_heatmap = st.checkbox("Tampilkan Heat Map", value=True)
    with col3:
        filter_3t = st.checkbox("Hanya 3T Regions", value=False)
    with col4:
        min_seji = st.slider("Min SEJI Score", 0, 100, 0, 5)

    # Apply filters
    filtered = df.copy()
    if filter_3t:
        filtered = filtered[filtered["is_3t"]]
    filtered = filtered[filtered["seji_score"] >= min_seji]

    st.markdown(f"**{len(filtered)} provinsi** ditampilkan dari total {len(df)}")

    # ── Build Folium Map ─────────────────────────────────────────
    m = folium.Map(
        location=[-2.5, 118.0],
        zoom_start=5,
        tiles=None,
        prefer_canvas=True,
    )

    # Base tiles
    folium.TileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        name="Dark (CartoDB)",
        attr="CartoDB",
        max_zoom=19,
    ).add_to(m)

    folium.TileLayer(
        "OpenStreetMap",
        name="OpenStreetMap",
        attr="OSM",
    ).add_to(m)

    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="Satellite (ESRI)",
        attr="ESRI",
    ).add_to(m)

    # ── Heatmap Layer ───────────────────────────────────────────
    if show_heatmap and len(filtered) > 0:
        heat_col = {
            "SEJI Score": "seji_score",
            "Solar Radiation": "solar_score",
            "Energy Access": "access_score",
            "Poverty Rate": "poverty_score",
        }.get(map_layer, "seji_score")

        heat_data = [[row["lat"], row["lon"], row[heat_col] / 100]
                     for _, row in filtered.iterrows()]

        HeatMap(
            heat_data,
            name=f"Heatmap — {map_layer}",
            min_opacity=0.3,
            max_zoom=10,
            radius=60,
            blur=40,
            gradient={0.2: "#00B4A6", 0.5: "#F5A623", 0.8: "#FF6B00", 1.0: "#FF4560"},
        ).add_to(m)

    # ── Province Markers ────────────────────────────────────────
    marker_group = folium.FeatureGroup(name="Province Markers", show=True)

    for _, row in filtered.iterrows():
        pcolor = PRIORITY_COLORS.get(str(row["priority"]), "#888")
        radius = 8 + row["seji_score"] / 15
        is3t_badge = "🔴 3T Region" if row["is_3t"] else "⚪ Non-3T"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif; width:260px; background:#0D1B2A; 
                    color:#E8F4F8; border-radius:8px; padding:12px;">
            <div style="font-size:1rem; font-weight:700; color:#F5A623; margin-bottom:4px;">
                {row['province']}
            </div>
            <div style="font-size:0.75rem; color:#8892A4; margin-bottom:8px;">
                {is3t_badge} · {row['island']}
            </div>
            <div style="background:#112240; border-radius:6px; padding:8px; margin-bottom:6px;">
                <span style="font-size:1.6rem; font-weight:800; color:{pcolor};">
                    {row['seji_score']:.1f}
                </span>
                <span style="font-size:0.8rem; color:#8892A4;">/100 — {row['priority']} Priority</span>
            </div>
            <table style="width:100%; font-size:0.78rem; border-collapse:collapse;">
                <tr><td style="color:#8892A4; padding:2px;">☀️ Solar</td>
                    <td style="text-align:right; font-weight:600; color:#FFD166;">{row['solar_kwh']:.2f} kWh/m²/day</td></tr>
                <tr><td style="color:#8892A4; padding:2px;">⚡ Electricity</td>
                    <td style="text-align:right; font-weight:600; color:#06D6A0;">{row['electricity_access']*100:.1f}%</td></tr>
                <tr><td style="color:#8892A4; padding:2px;">💸 Poverty</td>
                    <td style="text-align:right; font-weight:600; color:#FF6B6B;">{row['poverty_rate']:.1f}%</td></tr>
                <tr><td style="color:#8892A4; padding:2px;">👥 Pop. Density</td>
                    <td style="text-align:right; font-weight:600; color:#A0C4FF;">{row['pop_density']:.0f}/km²</td></tr>
                <tr><td style="color:#8892A4; padding:2px;">🌐 Remoteness</td>
                    <td style="text-align:right; font-weight:600; color:#BDB2FF;">{row['remoteness']:.2f}</td></tr>
            </table>
        </div>
        """

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=radius,
            color=pcolor,
            fill=True,
            fill_color=pcolor,
            fill_opacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row['province']} — SEJI: {row['seji_score']:.1f}",
        ).add_to(marker_group)

    marker_group.add_to(m)

    # MiniMap & Layer Control
    MiniMap(toggle_display=True, position="bottomleft").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    # Legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; right: 20px; z-index: 9999;
                background: rgba(13,27,42,0.92); border: 1px solid rgba(245,166,35,0.4);
                border-radius: 10px; padding: 10px 14px; font-family: Arial, sans-serif;">
        <div style="font-size:0.8rem; font-weight:700; color:#F5A623; margin-bottom:6px;">
            SEJI Priority
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin:3px 0;">
            <div style="width:12px;height:12px;border-radius:50%;background:#FF4560;"></div>
            <span style="color:#E8F4F8; font-size:0.75rem;">Critical (&gt;75)</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin:3px 0;">
            <div style="width:12px;height:12px;border-radius:50%;background:#F5A623;"></div>
            <span style="color:#E8F4F8; font-size:0.75rem;">High (55–75)</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin:3px 0;">
            <div style="width:12px;height:12px;border-radius:50%;background:#00B4A6;"></div>
            <span style="color:#E8F4F8; font-size:0.75rem;">Moderate (33–55)</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin:3px 0;">
            <div style="width:12px;height:12px;border-radius:50%;background:#39D353;"></div>
            <span style="color:#E8F4F8; font-size:0.75rem;">Low (&lt;33)</span>
        </div>
        <hr style="border-color:rgba(255,255,255,0.1); margin:5px 0;">
        <div style="font-size:0.65rem; color:#8892A4;">◆ = 3T Region</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Render map
    map_output = st_folium(m, width="100%", height=560, returned_objects=["last_object_clicked"])

    # ── Clicked Province Details ────────────────────────────────
    if map_output and map_output.get("last_object_clicked"):
        clicked = map_output["last_object_clicked"]
        lat, lon = clicked.get("lat"), clicked.get("lng")
        if lat and lon:
            # Find nearest province
            dists = ((df["lat"] - lat)**2 + (df["lon"] - lon)**2)
            nearest = df.loc[dists.idxmin()]
            st.markdown(f"""
            <div style='background:#112240; border:1px solid rgba(245,166,35,0.3);
                        border-radius:10px; padding:1rem; margin-top:0.5rem;'>
                <b style='color:#F5A623;'>📍 {nearest['province']}</b> —
                SEJI: <b style='color:#FF4560;'>{nearest['seji_score']}</b>/100 |
                Solar: {nearest['solar_kwh']:.2f} kWh/m²/day |
                Akses Listrik: {nearest['electricity_access']*100:.1f}% |
                Kemiskinan: {nearest['poverty_rate']:.1f}%
            </div>
            """, unsafe_allow_html=True)
