"""WebGIS Map — interactive Folium map with layers, click info, legend. v2.0"""

import streamlit as st
import folium
from folium.plugins import HeatMap, MiniMap
from streamlit_folium import st_folium
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">🗺️ WEBGIS</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Peta Interaktif SEJI Indonesia</h2>
        <p class="hero-subtitle">Klik marker untuk detail provinsi · Toggle layer di pojok kanan atas peta</p>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        map_layer = st.selectbox("🎨 Parameter Heatmap",
            ["SEJI Score","Solar Radiation","Energy Access","Poverty Rate","Remoteness"],
            help="Pilih variabel yang divisualisasikan sebagai heatmap")
    with c2:
        show_heat = st.checkbox("🌡️ Heatmap", value=True, help="Tampilkan overlay heatmap")
    with c3:
        show_3t   = st.checkbox("🏷️ Label 3T", value=True, help="Highlight wilayah 3T dengan outline merah")
    with c4:
        only_3t   = st.checkbox("Hanya 3T", value=False)
    with c5:
        min_seji  = st.slider("Min SEJI", 0, 90, 0, 5, help="Filter minimum SEJI Score")

    filt = df.copy()
    if only_3t: filt = filt[filt["is_3t"]]
    filt = filt[filt["seji_score"] >= min_seji]

    st.caption(f"**{len(filt)} provinsi** ditampilkan")

    # ── Build map ────────────────────────────────────────────────
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles=None, prefer_canvas=True)

    folium.TileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        name="Dark (CartoDB)", attr="CartoDB", max_zoom=19,
    ).add_to(m)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", attr="OSM").add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="Satellite (ESRI)", attr="ESRI",
    ).add_to(m)

    # Heatmap
    if show_heat and len(filt) > 0:
        col_map = {
            "SEJI Score": "seji_score",
            "Solar Radiation": "solar_score",
            "Energy Access": "access_score",
            "Poverty Rate": "poverty_score",
            "Remoteness": "remoteness_score",
        }
        hcol = col_map.get(map_layer, "seji_score")
        heat_data = [[r["lat"], r["lon"], r[hcol]/100] for _, r in filt.iterrows()]
        HeatMap(heat_data, name=f"Heatmap — {map_layer}",
                min_opacity=0.25, radius=65, blur=45,
                gradient={0.2:"#00B4A6", 0.5:"#F5A623", 0.8:"#FF6B00", 1.0:"#FF4560"},
        ).add_to(m)

    # Province markers
    markers = folium.FeatureGroup(name="Province Markers", show=True)
    for _, r in filt.iterrows():
        pc  = PRIORITY_COLORS.get(str(r["priority"]), "#888")
        rad = 7 + r["seji_score"] / 16
        border = "#FF2244" if (show_3t and r["is_3t"]) else pc
        bw     = 3 if (show_3t and r["is_3t"]) else 1.5
        badge  = "🔴 3T" if r["is_3t"] else "⚪ Non-3T"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif;width:270px;background:#0B1623;
                    color:#E8F0F8;border-radius:10px;padding:14px;border:1px solid {pc}40;">
            <div style="font-size:1rem;font-weight:700;color:#F5A623;">{r['province']}</div>
            <div style="font-size:0.72rem;color:#7A94B0;margin-bottom:8px;">{badge} · {r['island']}</div>
            <div style="background:#112240;border-radius:7px;padding:9px;margin-bottom:8px;
                        display:flex;align-items:center;gap:10px;">
                <span style="font-size:1.8rem;font-weight:800;color:{pc};">{r['seji_score']:.1f}</span>
                <div>
                    <div style="font-size:0.7rem;color:#7A94B0;">SEJI Score / 100</div>
                    <div style="font-size:0.78rem;font-weight:700;color:{pc};">{r['priority']} Priority</div>
                </div>
            </div>
            <table style="width:100%;font-size:0.77rem;border-collapse:collapse;">
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="color:#7A94B0;padding:4px 2px;">☀️ Solar</td>
                    <td style="text-align:right;font-weight:600;color:#FFD166;">{r['solar_kwh']:.2f} kWh/m²/day</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="color:#7A94B0;padding:4px 2px;">⚡ Elektrisitas</td>
                    <td style="text-align:right;font-weight:600;color:#06D6A0;">{r['electricity_access']*100:.1f}%</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="color:#7A94B0;padding:4px 2px;">💸 Kemiskinan</td>
                    <td style="text-align:right;font-weight:600;color:#FF6B6B;">{r['poverty_rate']:.1f}%</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="color:#7A94B0;padding:4px 2px;">👥 Pop. Density</td>
                    <td style="text-align:right;font-weight:600;color:#A0C4FF;">{r['pop_density']:,.0f}/km²</td>
                </tr>
                <tr>
                    <td style="color:#7A94B0;padding:4px 2px;">🌐 Keterpencilan</td>
                    <td style="text-align:right;font-weight:600;color:#BDB2FF;">{r['remoteness']:.2f}</td>
                </tr>
            </table>
            <div style="margin-top:8px;font-size:0.65rem;color:#4A6A8A;">
                📍 {r['lat']:.3f}°, {r['lon']:.3f}°
            </div>
        </div>"""

        folium.CircleMarker(
            location=[r["lat"], r["lon"]], radius=rad,
            color=border, fill=True, fill_color=pc,
            fill_opacity=0.72, weight=bw,
            popup=folium.Popup(popup_html, max_width=290),
            tooltip=f"<b>{r['province']}</b> — SEJI: {r['seji_score']:.1f} ({r['priority']})",
        ).add_to(markers)

    markers.add_to(m)
    MiniMap(toggle_display=True, position="bottomleft").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    # Legend
    m.get_root().html.add_child(folium.Element("""
    <div style="position:fixed;bottom:60px;right:20px;z-index:9999;
                background:rgba(11,22,35,0.93);border:1px solid rgba(245,166,35,0.4);
                border-radius:12px;padding:12px 16px;font-family:Arial,sans-serif;
                box-shadow:0 4px 20px rgba(0,0,0,0.4);">
        <div style="font-size:0.78rem;font-weight:700;color:#F5A623;margin-bottom:8px;
                    letter-spacing:1px;">SEJI PRIORITY</div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#FF4560;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">Critical  (&gt;75)</span>
        </div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#F5A623;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">High      (55–75)</span>
        </div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#00B4A6;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">Moderate  (33–55)</span>
        </div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#39D353;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">Low       (&lt;33)</span>
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:7px 0;">
        <div style="font-size:0.65rem;color:#5A7A9A;">
            ◆ = 3T Region (outline merah)<br>
            ● Ukuran = SEJI Score
        </div>
    </div>
    """))

    out = st_folium(m, width="100%", height=560, returned_objects=["last_object_clicked"])

    # Click info panel
    if out and out.get("last_object_clicked"):
        cl = out["last_object_clicked"]
        lat, lon = cl.get("lat"), cl.get("lng")
        if lat and lon:
            dists = ((df["lat"]-lat)**2 + (df["lon"]-lon)**2)
            nr = df.loc[dists.idxmin()]
            pc = PRIORITY_COLORS.get(str(nr["priority"]), "#888")
            st.markdown(f"""
            <div style='background:var(--bg-card);border:1px solid rgba(245,166,35,0.28);
                        border-radius:12px;padding:1.1rem;margin-top:0.6rem;
                        display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;'>
                <div>
                    <div style='font-size:0.72rem;color:var(--text-muted);'>PROVINSI DIPILIH</div>
                    <div style='font-size:1.1rem;font-weight:700;color:#F5A623;'>{nr['province']}</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:1.6rem;font-weight:800;color:{pc};'>{nr['seji_score']}</div>
                    <div style='font-size:0.68rem;color:var(--text-muted);'>SEJI Score</div>
                </div>
                <div style='font-size:0.82rem;color:var(--text-secondary);line-height:1.7;'>
                    ☀️ {nr['solar_kwh']:.2f} kWh/m²/day &nbsp;|&nbsp;
                    ⚡ {nr['electricity_access']*100:.1f}% &nbsp;|&nbsp;
                    💸 {nr['poverty_rate']:.1f}% kemiskinan &nbsp;|&nbsp;
                    🌐 Keterpencilan {nr['remoteness']:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
