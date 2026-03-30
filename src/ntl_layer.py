"""NTL Vulnerability Layer — VIIRS Nighttime Lights analysis. v3.0"""

import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS, ISLAND_COLORS


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">🌃 NTL VULNERABILITY</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Nighttime Lights Vulnerability Index</h2>
        <p class="hero-subtitle">VIIRS DNB — wilayah surya tinggi + NTL gelap = target utama Energy Justice</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Info cards ────────────────────────────────────────────────
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown("""<div class="info-card">
        <h4>🛰️ VIIRS DNB</h4>
        <p>Visible Infrared Imaging Radiometer Suite - Day/Night Band.
        Mendeteksi cahaya artifisial malam hari dari orbit 824 km.</p>
        </div>""", unsafe_allow_html=True)
    with i2:
        st.markdown("""<div class="info-card">
        <h4>🌑 Interpretasi</h4>
        <p>NTL gelap (DN rendah) = akses listrik rendah. Kombinasikan dengan
        potensi surya untuk identifikasi area intervensi PLTS prioritas.</p>
        </div>""", unsafe_allow_html=True)
    with i3:
        st.markdown("""<div class="info-card">
        <h4>⚡ Indeks Kerentanan</h4>
        <p>Vuln = Solar_norm × (1 − NTL_norm). Nilai tinggi = potensi surya
        tinggi namun belum teraliri listrik.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Compute vulnerability index ───────────────────────────────
    s_norm = (df["solar_kwh"] - df["solar_kwh"].min()) / (df["solar_kwh"].max() - df["solar_kwh"].min() + 1e-9)
    n_norm = (df["ntl_index"] - df["ntl_index"].min()) / (df["ntl_index"].max() - df["ntl_index"].min() + 1e-9)
    df = df.copy()
    df["vulnerability"] = ((s_norm * (1 - n_norm)) * 100).round(1)

    # ── Controls ──────────────────────────────────────────────────
    st.markdown("### 🗺️ Peta Dual Layer: Solar Potensi vs NTL")
    cc1, cc2, cc3, cc4 = st.columns(4)
    with cc1:
        layer_mode = st.selectbox("Layer Aktif", ["NTL Intensity", "Solar Potential", "Vulnerability Index"])
    with cc2:
        opacity_layer = st.slider("Transparansi Heatmap", 0.1, 1.0, 0.6, 0.05)
    with cc3:
        show_vuln_markers = st.checkbox("Tampilkan Marker Kerentanan", value=True)
    with cc4:
        min_vuln = st.slider("Min Vulnerability", 0, 100, 30, 5)

    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles=None, prefer_canvas=True)
    folium.TileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        name="Dark", attr="CartoDB", max_zoom=19,
    ).add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="Satellite", attr="ESRI",
    ).add_to(m)

    # NTL heatmap layer
    if layer_mode == "NTL Intensity":
        ntl_heat = [[r["lat"], r["lon"], r["ntl_index"]] for _, r in df.iterrows()]
        HeatMap(ntl_heat, name="NTL Heatmap",
                min_opacity=opacity_layer * 0.4, radius=70, blur=50,
                gradient={0.0: "#000033", 0.3: "#0D1B40", 0.6: "#FFD700", 1.0: "#FFFFFF"},
                ).add_to(m)
    elif layer_mode == "Solar Potential":
        sol_heat = [[r["lat"], r["lon"], (r["solar_kwh"] - 3.5) / 2.5] for _, r in df.iterrows()]
        HeatMap(sol_heat, name="Solar Heatmap",
                min_opacity=opacity_layer * 0.4, radius=70, blur=50,
                gradient={0.2: "#0D3B6E", 0.5: "#F5A623", 0.8: "#FF6B00", 1.0: "#FF0000"},
                ).add_to(m)
    else:  # Vulnerability
        vuln_heat = [[r["lat"], r["lon"], r["vulnerability"] / 100] for _, r in df.iterrows()]
        HeatMap(vuln_heat, name="Vulnerability Heatmap",
                min_opacity=opacity_layer * 0.4, radius=70, blur=50,
                gradient={0.2: "#00B4A6", 0.5: "#F5A623", 0.8: "#FF4560", 1.0: "#FF0000"},
                ).add_to(m)

    # Vulnerability markers
    if show_vuln_markers:
        vuln_group = folium.FeatureGroup(name="Vulnerability Markers")
        for _, r in df[df["vulnerability"] >= min_vuln].iterrows():
            vc  = "#FF4560" if r["vulnerability"] > 70 else "#F5A623" if r["vulnerability"] > 50 else "#00C4B4"
            rad = 6 + r["vulnerability"] / 15
            popup_html = f"""
            <div style="font-family:Arial;width:250px;background:#0B1623;color:#E8F0F8;
                        border-radius:10px;padding:12px;border:1px solid {vc}60;">
                <div style="font-size:1rem;font-weight:700;color:#F5A623;">{r['province']}</div>
                <div style="font-size:0.7rem;color:#7A94B0;margin-bottom:8px;">
                    {'🔴 3T' if r['is_3t'] else '⚪ Non-3T'} · {r['island']}</div>
                <div style="background:#112240;border-radius:7px;padding:8px;margin-bottom:8px;
                            display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.6rem;font-weight:800;color:{vc};">{r['vulnerability']:.1f}</span>
                    <div><div style="font-size:0.68rem;color:#7A94B0;">Vulnerability Index</div></div>
                </div>
                <table style="width:100%;font-size:0.74rem;border-collapse:collapse;">
                    <tr><td style="color:#7A94B0;padding:3px 2px;">☀️ Solar</td>
                        <td style="text-align:right;color:#FFD166;font-weight:600;">{r['solar_kwh']:.2f} kWh/m²</td></tr>
                    <tr><td style="color:#7A94B0;padding:3px 2px;">🌃 NTL Index</td>
                        <td style="text-align:right;color:#8BE0FF;font-weight:600;">{r['ntl_index']:.3f}</td></tr>
                    <tr><td style="color:#7A94B0;padding:3px 2px;">💡 NTL DN</td>
                        <td style="text-align:right;color:#8BE0FF;font-weight:600;">{r['ntl_dn']:.0f} DN</td></tr>
                    <tr><td style="color:#7A94B0;padding:3px 2px;">⚡ Akses</td>
                        <td style="text-align:right;color:#06D6A0;font-weight:600;">{r['electricity_access']*100:.1f}%</td></tr>
                </table>
            </div>"""
            folium.CircleMarker(
                location=[r["lat"], r["lon"]], radius=rad,
                color=vc, fill=True, fill_color=vc, fill_opacity=0.75, weight=2,
                popup=folium.Popup(popup_html, max_width=270),
                tooltip=f"<b>{r['province']}</b> — Vuln: {r['vulnerability']:.1f}",
            ).add_to(vuln_group)
        vuln_group.add_to(m)

    folium.LayerControl(position="topright").add_to(m)

    # Legend
    m.get_root().html.add_child(folium.Element("""
    <div style="position:fixed;bottom:60px;right:20px;z-index:9999;
                background:rgba(11,22,35,0.93);border:1px solid rgba(245,166,35,0.4);
                border-radius:12px;padding:12px 16px;font-family:Arial,sans-serif;">
        <div style="font-size:0.78rem;font-weight:700;color:#F5A623;margin-bottom:8px;">
            VULNERABILITY INDEX</div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#FF4560;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">High (&gt;70)</span>
        </div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#F5A623;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">Medium (50–70)</span>
        </div>
        <div style="display:flex;align-items:center;gap:9px;margin:4px 0;">
            <div style="width:13px;height:13px;border-radius:50%;background:#00C4B4;"></div>
            <span style="color:#E8F0F8;font-size:0.74rem;">Low (&lt;50)</span>
        </div>
    </div>
    """))

    st_folium(m, width="100%", height=520, returned_objects=[])

    # ── Scatter: Solar vs NTL ─────────────────────────────────────
    st.markdown("### 🌙 Analisis: Solar Potential vs Nighttime Light")
    st.caption("Pojok kiri bawah = gelap + surya tinggi = target utama Energy Justice")

    fig_s = px.scatter(
        df, x="ntl_index", y="solar_kwh",
        color="vulnerability",
        color_continuous_scale=["#39D353", "#F5A623", "#FF4560"],
        size="poverty_rate", size_max=25,
        hover_name="province",
        hover_data={"ntl_index": ":.3f", "solar_kwh": ":.2f", "vulnerability": ":.1f",
                    "electricity_access": ":.1%", "is_3t": True},
        labels={"ntl_index": "NTL Index (0=gelap, 1=terang)",
                "solar_kwh": "Radiasi Matahari (kWh/m²/hari)",
                "vulnerability": "Vulnerability"},
        symbol="is_3t", symbol_map={True: "diamond", False: "circle"},
    )
    fig_s.add_vline(x=0.4, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                    annotation_text="NTL threshold 0.4",
                    annotation_font=dict(color=cc.get("text", "#C8D8E8"), size=10))
    fig_s.add_hline(y=4.9, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                    annotation_text="4.9 kWh/m²",
                    annotation_font=dict(color=cc.get("text", "#C8D8E8"), size=10))
    fig_s.add_annotation(x=0.15, y=5.6,
                         text="🎯 ZONA TARGET<br>(Surya Tinggi + NTL Gelap)",
                         showarrow=False, font=dict(color="#FF4560", size=10),
                         bgcolor="rgba(255,69,96,0.1)", bordercolor="#FF4560",
                         borderwidth=1, borderpad=4)
    fig_s.update_layout(
        paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
        plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
        font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
        height=430,
        xaxis=dict(gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
        yaxis=dict(gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
    )
    st.plotly_chart(fig_s, use_container_width=True)

    # ── Ranking by Vulnerability ──────────────────────────────────
    st.markdown("### 🔴 Top 10 Kerentanan Tertinggi")
    top_vuln = df.nlargest(10, "vulnerability")[
        ["province", "island", "is_3t", "vulnerability", "solar_kwh", "ntl_index", "ntl_dn", "electricity_access"]
    ].copy()
    top_vuln["electricity_access"] = (top_vuln["electricity_access"] * 100).round(1).astype(str) + "%"
    top_vuln["is_3t"] = top_vuln["is_3t"].map({True: "✅ 3T", False: "❌"})
    top_vuln.columns = ["Provinsi", "Kepulauan", "3T", "Vulnerability", "Solar (kWh/m²)", "NTL Index", "NTL DN", "Akses Listrik"]
    st.dataframe(top_vuln.reset_index(drop=True), use_container_width=True,
                 column_config={"Vulnerability": st.column_config.ProgressColumn("Vulnerability", min_value=0, max_value=100, format="%.1f")})
