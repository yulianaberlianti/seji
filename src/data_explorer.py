"""Data Explorer — filters, table, scatter matrix, download. v2.0"""

import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">📋 DATA</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Data Explorer</h2>
        <p class="hero-subtitle">Filter, eksplorasi, dan unduh dataset SEJI seluruh provinsi Indonesia</p>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        isl = st.selectbox("Kepulauan", ["Semua"]+sorted(df["island"].unique().tolist()))
    with c2:
        pri = st.selectbox("Prioritas", ["Semua","Critical","High","Moderate","Low"])
    with c3:
        t3  = st.selectbox("Status 3T", ["Semua","3T Only","Non-3T Only"])
    with c4:
        rng = st.slider("SEJI Score Range", 0.0, 100.0, (0.0, 100.0), 1.0)

    filt = df.copy()
    if isl != "Semua": filt = filt[filt["island"]==isl]
    if pri != "Semua": filt = filt[filt["priority"]==pri]
    if t3  == "3T Only":    filt = filt[filt["is_3t"]]
    elif t3 == "Non-3T Only": filt = filt[~filt["is_3t"]]
    filt = filt[(filt["seji_score"]>=rng[0]) & (filt["seji_score"]<=rng[1])]

    st.caption(f"**{len(filt)} provinsi** ditemukan dari total {len(df)}")

    # Summary metrics
    if len(filt) > 0:
        mc1,mc2,mc3,mc4 = st.columns(4)
        with mc1: st.metric("Rata-rata SEJI", f"{filt['seji_score'].mean():.1f}", help="Rata-rata SEJI Score filter ini")
        with mc2: st.metric("Rata-rata Solar", f"{filt['solar_kwh'].mean():.2f} kWh/m²", help="NASA POWER tahunan")
        with mc3: st.metric("Rata-rata Akses", f"{filt['electricity_access'].mean()*100:.1f}%", help="Rasio elektrifikasi BPS")
        with mc4: st.metric("Rata-rata Miskin", f"{filt['poverty_rate'].mean():.1f}%", help="BPS 2023")

    # Table
    disp = filt[["province","island","is_3t","seji_score","priority",
                 "solar_kwh","electricity_access","poverty_rate","pop_density","remoteness"]].copy()
    disp["electricity_access"] = (disp["electricity_access"]*100).round(1).astype(str)+"%"
    disp["pop_density"] = disp["pop_density"].apply(lambda x: f"{x:,.0f}")
    disp["is_3t"] = disp["is_3t"].map({True:"✅ Ya", False:"❌ Tidak"})
    disp.columns = ["Provinsi","Kepulauan","3T","SEJI Score","Prioritas",
                    "Solar (kWh/m²)","Akses Listrik","Kemiskinan (%)","Pop. Density","Keterpencilan"]

    st.dataframe(disp, use_container_width=True, height=380,
                 column_config={
                     "SEJI Score": st.column_config.ProgressColumn(
                         "SEJI Score", min_value=0, max_value=100, format="%.1f"),
                 })

    # Downloads
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("⬇️ Download CSV", filt.to_csv(index=False),
                           "seji_data.csv", "text/csv")
    with dc2:
        st.download_button("⬇️ Download JSON", filt.to_json(orient="records", indent=2),
                           "seji_data.json", "application/json")
    with dc3:
        # GeoJSON export
        import json
        features = []
        for _, r in filt.iterrows():
            features.append({
                "type": "Feature",
                "geometry": {"type":"Point","coordinates":[r["lon"],r["lat"]]},
                "properties": {k:v for k,v in r.items() if k not in ["lat","lon"]},
            })
        geojson = json.dumps({"type":"FeatureCollection","features":features}, default=str)
        st.download_button("⬇️ Download GeoJSON", geojson, "seji_data.geojson", "application/json")

    # Scatter matrix
    st.markdown("### 📊 Scatter Matrix")
    if len(filt) >= 3:
        dims = ["seji_score","solar_kwh","electricity_access","poverty_rate","remoteness"]
        fig = px.scatter_matrix(
            filt, dimensions=dims, color="priority",
            color_discrete_map=PRIORITY_COLORS, hover_name="province",
            labels={"seji_score":"SEJI","solar_kwh":"Solar",
                    "electricity_access":"Access","poverty_rate":"Poverty","remoteness":"Remote"},
        )
        fig.update_traces(diagonal_visible=False, marker=dict(size=5, opacity=0.72))
        fig.update_layout(
            paper_bgcolor=cc.get("paper","rgba(0,0,0,0)"),
            font=dict(color=cc.get("text","#C8D8E8"),family="Plus Jakarta Sans"),
            height=520, legend=dict(bgcolor=cc.get("legend","rgba(7,17,32,0.88)")),
        )
        st.plotly_chart(fig, use_container_width=True)
