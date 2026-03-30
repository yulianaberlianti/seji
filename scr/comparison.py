"""Side-by-Side Comparison of two provinces. v3.0"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def _color(pc):
    r, g, b = int(pc[1:3], 16), int(pc[3:5], 16), int(pc[5:7], 16)
    return f"rgba({r},{g},{b},0.15)"


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">🔄 KOMPARASI</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Komparasi Antar Wilayah</h2>
        <p class="hero-subtitle">Bandingkan dua provinsi secara langsung — bantu pembuat kebijakan melihat prioritas objektif</p>
    </div>
    """, unsafe_allow_html=True)

    all_prov = df["province"].tolist()
    c1, c2 = st.columns(2)
    with c1:
        prov_a = st.selectbox("🔵 Provinsi A", all_prov,
                              index=all_prov.index("Maluku Utara") if "Maluku Utara" in all_prov else 0)
    with c2:
        prov_b = st.selectbox("🟠 Provinsi B", all_prov,
                              index=all_prov.index("Papua Tengah") if "Papua Tengah" in all_prov else 1)

    ra = df[df["province"] == prov_a].iloc[0]
    rb = df[df["province"] == prov_b].iloc[0]
    pca = PRIORITY_COLORS.get(str(ra["priority"]), "#888")
    pcb = PRIORITY_COLORS.get(str(rb["priority"]), "#888")

    # ── Header cards ──────────────────────────────────────────────
    ca, cb = st.columns(2)
    for col, row, pc, label in [(ca, ra, pca, "A"), (cb, rb, pcb, "B")]:
        with col:
            badge_3t = "🔴 3T" if row["is_3t"] else "⚪ Non-3T"
            st.markdown(f"""
            <div style='background:var(--bg-card);border:2px solid {pc}44;
                        border-top:4px solid {pc};border-radius:16px;
                        padding:1.5rem;text-align:center;'>
                <div style='font-size:0.65rem;color:{pc};font-weight:700;
                            font-family:Space Mono;letter-spacing:1.5px;'>PROVINSI {label}</div>
                <div style='font-size:1.3rem;font-weight:800;color:var(--text-primary);
                            margin:6px 0;'>{row['province']}</div>
                <div style='font-size:0.75rem;color:var(--text-muted);margin-bottom:10px;'>
                    {badge_3t} · {row['island']}</div>
                <div style='font-size:3.2rem;font-weight:800;color:{pc};line-height:1;'>
                    {row['seji_score']:.1f}</div>
                <div style='font-size:0.7rem;color:var(--text-muted);'>SEJI Score / 100</div>
                <span style='display:inline-block;background:{pc}1A;border:1px solid {pc};
                             color:{pc};padding:4px 14px;border-radius:20px;
                             font-weight:700;font-size:0.8rem;margin-top:8px;'>
                    {str(row["priority"]).upper()} PRIORITY</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Who wins? verdict ─────────────────────────────────────────
    winner = prov_a if ra["seji_score"] > rb["seji_score"] else prov_b
    win_score = max(ra["seji_score"], rb["seji_score"])
    diff = abs(ra["seji_score"] - rb["seji_score"])
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(245,166,35,0.08),rgba(245,166,35,0.02));
                border:1px solid rgba(245,166,35,0.3);border-radius:14px;padding:1.2rem;
                text-align:center;margin-bottom:1.2rem;'>
        <span class="badge">⚖️ VERDICT</span>
        <p style='color:var(--text-primary);margin-top:0.7rem;font-size:0.95rem;'>
            <strong style='color:#F5A623;'>{winner}</strong> memiliki prioritas SEJI lebih tinggi
            (<strong style='color:#FF4560;'>{win_score:.1f}</strong>) —
            selisih <strong>{diff:.1f} poin</strong> dari {prov_b if winner==prov_a else prov_a}.
            {'Wilayah ini harus menjadi prioritas intervensi PLTS terlebih dahulu.' if diff > 10
             else 'Kedua wilayah memiliki prioritas yang hampir setara, keduanya perlu perhatian.'}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics side by side ──────────────────────────────────────
    st.markdown("### 📊 Perbandingan Metrik Utama")
    params = [
        ("SEJI Score",         ra["seji_score"],               rb["seji_score"],              100,   False),
        ("Solar (kWh/m²/hari)",ra["solar_kwh"],                rb["solar_kwh"],               6.5,   False),
        ("Akses Listrik (%)",  ra["electricity_access"]*100,   rb["electricity_access"]*100,  100,   True),
        ("Kemiskinan (%)",     ra["poverty_rate"],              rb["poverty_rate"],            45,    False),
        ("Keterpencilan (0-1)",ra["remoteness"],                rb["remoteness"],              1,     False),
        ("Pop. Density/km²",   ra["pop_density"],               rb["pop_density"],             1000,  True),
        ("NTL Index (0-1)",    ra["ntl_index"],                 rb["ntl_index"],               1,     True),
    ]

    for label, va, vb, mx, lower_is_worse in params:
        pct_a = min(va / mx * 100, 100) if mx > 0 else 0
        pct_b = min(vb / mx * 100, 100) if mx > 0 else 0
        better_a = (va >= vb) if not lower_is_worse else (va <= vb)
        col_a = pca if better_a else "#5A7A9A"
        col_b = pcb if not better_a else "#5A7A9A"

        st.markdown(f"""
        <div style='background:var(--bg-card);border-radius:12px;padding:0.9rem 1.2rem;
                    margin:0.3rem 0;border:1px solid var(--border-subtle);'>
            <div style='font-size:0.72rem;color:var(--text-muted);font-weight:700;
                        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;'>{label}</div>
            <div style='display:flex;align-items:center;gap:12px;'>
                <div style='flex:1;text-align:right;'>
                    <span style='font-size:1.1rem;font-weight:800;color:{col_a};'>{va:.2f if isinstance(va,float) else va}</span>
                    {'✓' if better_a else ''}
                </div>
                <div style='width:200px;'>
                    <div style='height:6px;background:rgba(255,255,255,0.08);border-radius:3px;margin:2px 0;overflow:hidden;'>
                        <div style='height:100%;width:{pct_a:.1f}%;background:{col_a};border-radius:3px;'></div>
                    </div>
                    <div style='height:6px;background:rgba(255,255,255,0.08);border-radius:3px;margin:2px 0;overflow:hidden;'>
                        <div style='height:100%;width:{pct_b:.1f}%;background:{col_b};border-radius:3px;'></div>
                    </div>
                </div>
                <div style='flex:1;text-align:left;'>
                    <span style='font-size:1.1rem;font-weight:800;color:{col_b};'>{vb:.2f if isinstance(vb,float) else vb}</span>
                    {'✓' if not better_a else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Radar ─────────────────────────────────────────────────────
    st.markdown("### 🕸️ Radar Komponen SEJI")
    dims   = ["solar_score", "access_score", "poverty_score", "pop_score", "remoteness_score"]
    dlbls  = ["Solar", "Energy Access\n(inv.)", "Poverty", "Population", "Remoteness"]

    fig_r = go.Figure()
    for row, pc, label in [(ra, pca, prov_a), (rb, pcb, prov_b)]:
        vals = [float(row[d]) for d in dims]
        r, g, b = int(pc[1:3], 16), int(pc[3:5], 16), int(pc[5:7], 16)
        fig_r.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=dlbls + [dlbls[0]],
            fill="toself", name=label,
            line_color=pc,
            fillcolor=f"rgba({r},{g},{b},0.15)",
        ))
    fig_r.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                           gridcolor=cc.get("grid", "rgba(255,255,255,0.06)"),
                           tickfont=dict(color=cc.get("text", "#C8D8E8"), size=9)),
            angularaxis=dict(gridcolor=cc.get("grid", "rgba(255,255,255,0.06)"),
                            tickfont=dict(color=cc.get("text", "#C8D8E8"), size=10)),
            bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
        ),
        paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
        font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
        legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
        margin=dict(l=80, r=80, t=50, b=50), height=420,
    )
    st.plotly_chart(fig_r, use_container_width=True)

    # ── Bar comparison ────────────────────────────────────────────
    st.markdown("### 📊 Perbandingan Bar Chart")
    all_vals = {
        "Solar": [ra["solar_score"], rb["solar_score"]],
        "E.Access": [ra["access_score"], rb["access_score"]],
        "Poverty": [ra["poverty_score"], rb["poverty_score"]],
        "Population": [ra["pop_score"], rb["pop_score"]],
        "Remoteness": [ra["remoteness_score"], rb["remoteness_score"]],
    }

    fig_b = go.Figure()
    fig_b.add_trace(go.Bar(
        name=prov_a, x=list(all_vals.keys()),
        y=[v[0] for v in all_vals.values()],
        marker_color=pca, opacity=0.9,
        text=[f"{v[0]:.1f}" for v in all_vals.values()],
        textposition="outside",
    ))
    fig_b.add_trace(go.Bar(
        name=prov_b, x=list(all_vals.keys()),
        y=[v[1] for v in all_vals.values()],
        marker_color=pcb, opacity=0.9,
        text=[f"{v[1]:.1f}" for v in all_vals.values()],
        textposition="outside",
    ))
    fig_b.update_layout(
        barmode="group",
        paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
        plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
        font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
        height=340,
        legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
        yaxis=dict(range=[0, 115], gridcolor=cc.get("grid", "rgba(255,255,255,0.06)"),
                   title="Score (0–100)"),
        margin=dict(l=5, r=5, t=20, b=35),
    )
    st.plotly_chart(fig_b, use_container_width=True)

    # ── Policy Table ──────────────────────────────────────────────
    st.markdown("### 📋 Tabel Perbandingan Lengkap")
    rows = [
        ("SEJI Score", f"{ra['seji_score']:.1f}", f"{rb['seji_score']:.1f}"),
        ("Prioritas", str(ra["priority"]), str(rb["priority"])),
        ("Status 3T", "✅ Ya" if ra["is_3t"] else "❌ Tidak", "✅ Ya" if rb["is_3t"] else "❌ Tidak"),
        ("Kepulauan", ra["island"], rb["island"]),
        ("Radiasi (kWh/m²/hari)", f"{ra['solar_kwh']:.2f}", f"{rb['solar_kwh']:.2f}"),
        ("Akses Listrik", f"{ra['electricity_access']*100:.1f}%", f"{rb['electricity_access']*100:.1f}%"),
        ("Kemiskinan", f"{ra['poverty_rate']:.1f}%", f"{rb['poverty_rate']:.1f}%"),
        ("Pop. Density", f"{ra['pop_density']:,.0f}/km²", f"{rb['pop_density']:,.0f}/km²"),
        ("Keterpencilan", f"{ra['remoteness']:.3f}", f"{rb['remoteness']:.3f}"),
        ("NTL Index", f"{ra['ntl_index']:.3f}", f"{rb['ntl_index']:.3f}"),
        ("Cloud Fraction", f"{ra['cloud_fraction']:.2f}", f"{rb['cloud_fraction']:.2f}"),
    ]
    import pandas as pd
    tbl = pd.DataFrame(rows, columns=["Parameter", prov_a, prov_b])
    st.dataframe(tbl.set_index("Parameter"), use_container_width=True)
