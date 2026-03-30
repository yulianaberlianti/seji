"""Investment Simulator — SEJI Calculator + solar investment formula. v3.0"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">⚙️ INVESTMENT SIMULATOR</span>
        <h2 class="hero-title" style="font-size:1.55rem;">SEJI Investment Simulator</h2>
        <p class="hero-subtitle">Hitung SEJI Score + Simulasi teknis PLTS: energi tahunan, emisi CO₂, rumah teraliri</p>
    </div>
    """, unsafe_allow_html=True)

    tab_seji, tab_invest = st.tabs(["📊 SEJI Score Calculator", "💡 Simulasi Investasi PLTS"])

    # ── Tab 1: SEJI Score ─────────────────────────────────────────
    with tab_seji:
        c_inp, c_res = st.columns([2, 3])

        with c_inp:
            st.markdown("### 📥 Input Parameter Wilayah")
            loc = st.text_input("Nama Wilayah / Desa", value="Desa Contoh")
            st.markdown("---")

            with st.expander("☀️ Potensi Surya", expanded=True):
                solar = st.slider("Radiasi (kWh/m²/hari)", 3.0, 7.0, 5.0, 0.1,
                                  help="NASA POWER atau Global Solar Atlas")
                cloud = st.slider("Cloud Fraction (0=cerah)", 0.0, 1.0, 0.3, 0.05)

            with st.expander("⚡ Akses Energi", expanded=True):
                acc  = st.slider("Akses Listrik (%)", 0, 100, 45, 1)
                ntl  = st.slider("Nighttime Light Index (0–1)", 0.0, 1.0, 0.2, 0.05)

            with st.expander("💸 Sosial Ekonomi", expanded=True):
                pov  = st.slider("Kemiskinan (%)", 0.0, 50.0, 25.0, 0.5)
                pop  = st.number_input("Kepadatan Penduduk (jiwa/km²)", 1, 20000, 50, 10)
                rem  = st.slider("Keterpencilan (0–1)", 0.0, 1.0, 0.7, 0.05)

            with st.expander("🏋️ Bobot AHP", expanded=False):
                w1 = st.number_input("w₁ Solar",   0.0, 1.0, 0.30, 0.05)
                w2 = st.number_input("w₂ Access",  0.0, 1.0, 0.30, 0.05)
                w3 = st.number_input("w₃ Poverty", 0.0, 1.0, 0.20, 0.05)
                w4 = st.number_input("w₄ Pop.",    0.0, 1.0, 0.10, 0.05)
                w5 = st.number_input("w₅ Remote.", 0.0, 1.0, 0.10, 0.05)
                tw = w1 + w2 + w3 + w4 + w5
                if abs(tw - 1.0) > 0.01:
                    st.error(f"Total bobot = {tw:.2f} (harus 1.00)")
                else:
                    st.success(f"✅ Total = {tw:.2f}")

        with c_res:
            def n(val, col, invert=False):
                mn, mx = df[col].min(), df[col].max()
                v = max(0, min(1, (val - mn) / (mx - mn + 1e-9)))
                return 1 - v if invert else v

            sn = n(solar, "solar_kwh")
            an = n(acc / 100, "electricity_access", invert=True)
            pn = n(pov, "poverty_rate")
            dn = n(pop, "pop_density")
            rn = n(rem, "remoteness")

            seji = round((w1*sn + w2*an + w3*pn + w4*dn + w5*rn) * 100, 1)
            pri  = "Critical" if seji > 75 else "High" if seji > 55 else "Moderate" if seji > 33 else "Low"
            pc   = PRIORITY_COLORS[pri]

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,var(--bg-card),var(--bg-card2));
                        border:2px solid {pc}55;border-radius:18px;padding:2rem;
                        text-align:center;margin-bottom:1.4rem;'>
                <div style='font-size:0.72rem;color:var(--text-muted);font-family:Space Mono;
                            letter-spacing:2.5px;'>SOLAR ENERGY JUSTICE INDEX</div>
                <div style='font-size:5rem;font-weight:800;color:{pc};
                            line-height:1;margin:0.5rem 0;'>{seji}</div>
                <div style='font-size:1rem;color:var(--text-primary);margin-bottom:0.5rem;'>{loc}</div>
                <span style='display:inline-block;background:{pc}1A;border:1px solid {pc};
                             color:{pc};padding:5px 18px;border-radius:20px;
                             font-weight:700;font-size:0.88rem;'>{pri.upper()} PRIORITY</span>
            </div>
            """, unsafe_allow_html=True)

            # Component bar chart
            comps = [
                ("Solar Potential",      sn * 100, "#FFD166"),
                ("Energy Access (inv.)", an * 100, "#FF6B6B"),
                ("Poverty",              pn * 100, "#FF9F43"),
                ("Population",           dn * 100, "#A29BFE"),
                ("Remoteness",           rn * 100, "#00CEC9"),
            ]
            fig = go.Figure()
            for nm, val, col in comps:
                fig.add_trace(go.Bar(
                    name=nm, x=[val], y=[nm], orientation="h",
                    marker_color=col,
                    text=f"{val:.1f}", textposition="inside",
                    textfont=dict(color="white", size=11, family="Space Mono"),
                ))
            fig.update_layout(
                paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
                plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
                font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
                height=260, showlegend=False, barmode="group",
                xaxis=dict(range=[0, 105], gridcolor=cc.get("grid", "rgba(255,255,255,0.06)"),
                           title="Score (0–100, sebelum pembobotan)"),
                yaxis=dict(tickfont=dict(size=10)),
                margin=dict(l=5, r=5, t=30, b=35),
                title=dict(text="Komponen Score", font=dict(color="#F5A623", size=12)),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Ranking
            st.markdown("### 📍 Posisi Nasional")
            user_row = {"province": f"⭐ {loc}", "seji_score": seji, "priority": pri}
            cmp = pd.concat(
                [df[["province", "seji_score", "priority"]].copy(), pd.DataFrame([user_row])],
                ignore_index=True
            )
            cmp = cmp.sort_values("seji_score", ascending=False).reset_index(drop=True)
            rank = cmp[cmp["province"] == f"⭐ {loc}"].index[0] + 1

            st.markdown(f"""
            <div style='background:var(--bg-card);border:1px solid rgba(245,166,35,0.28);
                        border-radius:12px;padding:1rem;text-align:center;margin-bottom:0.8rem;'>
                <div style='color:var(--text-muted);font-size:0.8rem;'>Peringkat Wilayah</div>
                <div style='font-size:2.6rem;font-weight:800;color:#F5A623;line-height:1.1;'>#{rank}</div>
                <div style='color:var(--text-muted);font-size:0.78rem;'>dari {len(cmp)} wilayah</div>
            </div>
            """, unsafe_allow_html=True)

            start = max(0, rank - 4)
            end   = min(len(cmp), rank + 3)
            nb    = cmp.iloc[start:end].copy()
            nb.index = range(start + 1, end + 1)
            nb.index.name = "Rank"
            st.dataframe(nb.rename(columns={"province": "Wilayah", "seji_score": "SEJI Score", "priority": "Prioritas"}),
                         use_container_width=True)

            recs = {
                "Critical": ("🚨 Intervensi Segera", "#FF4560",
                    "Instalasi PLTS off-grid komunal segera. Potensi surya tinggi + akses listrik sangat rendah = kandidat ideal program PLTS 100–500 kWp. Prioritaskan dalam APBN/APBD jangka pendek."),
                "High":     ("⚡ Prioritas Tinggi", "#F5A623",
                    "Rencanakan PLTS terdesentralisasi dalam 1–2 tahun. Pertimbangkan microgrid solar hybrid untuk menjangkau lebih banyak rumah tangga terpencil."),
                "Moderate": ("📋 Jangka Menengah", "#00C4B4",
                    "Kandidat program PLTS atap bersubsidi atau kemitraan KPBU. Infrastruktur dasar sudah ada, akselerasi penetrasi PLTS perlu didorong."),
                "Low":      ("✅ Kondisi Relatif Baik", "#39D353",
                    "Fokus optimasi efisiensi energi dan PLTS rooftop sebagai pelengkap jaringan PLN yang sudah ada."),
            }
            rt, rc, rb = recs[pri]
            st.markdown(f"""
            <div style='background:rgba({int(rc[1:3],16)},{int(rc[3:5],16)},{int(rc[5:7],16)},0.08);
                        border:1px solid {rc}44;border-radius:12px;padding:1.2rem;margin-top:0.6rem;'>
                <div style='color:{rc};font-weight:700;font-size:0.95rem;margin-bottom:0.5rem;'>{rt}</div>
                <div style='color:var(--text-secondary);font-size:0.87rem;line-height:1.68;'>{rb}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2: Investment Simulation ──────────────────────────────
    with tab_invest:
        st.markdown("### 💡 Simulasi Energi & Investasi PLTS")
        st.markdown("""
        <div class="info-card" style="margin-bottom:1rem;">
            <h4>📐 Formula</h4>
            <p><strong>E = A × r × H × PR</strong><br>
            E = Energi (kWh/tahun) | A = Luas panel (m²) | r = Efisiensi panel |
            H = Radiasi tahunan (kWh/m²/tahun) | PR = Performance Ratio</p>
        </div>
        """, unsafe_allow_html=True)

        ci1, ci2 = st.columns([1, 2])

        with ci1:
            st.markdown("#### Parameter Teknis")
            prov_sel = st.selectbox("Lokasi / Provinsi", ["Custom"] + df["province"].tolist())
            if prov_sel != "Custom":
                row = df[df["province"] == prov_sel].iloc[0]
                h_daily = float(row["solar_kwh"])
                st.info(f"📡 Data NASA POWER: **{h_daily:.2f} kWh/m²/hari**")
            else:
                h_daily = st.slider("Radiasi Harian (kWh/m²/hari)", 3.0, 7.0, 5.0, 0.1)

            area     = st.number_input("Luas Lahan / Panel (m²)", 10, 100000, 1000, 50)
            eff      = st.slider("Efisiensi Panel (%)", 10, 25, 18, 1, help="Monocrystalline ~20%, Polycrystalline ~15-17%") / 100
            pr       = st.slider("Performance Ratio (PR)", 0.60, 0.90, 0.75, 0.01,
                                 help="0.75–0.80 untuk sistem off-grid umum")
            co2_grid = st.number_input("Emisi Grid (kg CO₂/kWh)", 0.1, 1.5, 0.85, 0.05,
                                       help="Indonesia grid emission factor ~0.85 kg CO₂/kWh (PLN)")
            kwh_house = st.number_input("Konsumsi per Rumah (kWh/bulan)", 10, 500, 35, 5,
                                        help="Rata-rata rumah tangga 3T ~35 kWh/bulan")
            capex_per_kwp = st.number_input("Capex (Juta Rp/kWp)", 5, 30, 12, 1,
                                            help="PLTS off-grid ~10-15 juta Rp/kWp (2024)")

        with ci2:
            H_annual = h_daily * 365
            E_annual = area * eff * H_annual * pr
            co2_saved = E_annual * co2_grid / 1000  # ton CO₂/year
            kwp = area * eff
            houses = int(E_annual / (kwh_house * 12))
            capex_total = kwp * capex_per_kwp
            lcoe = (capex_total * 1e6) / (E_annual * 25) if E_annual > 0 else 0  # Rp/kWh, 25yr lifespan
            yearly_savings = E_annual * 1500  # Rp/kWh tariff approx

            # Big result cards
            st.markdown("#### 📊 Hasil Simulasi")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Energi / Tahun", f"{E_annual:,.0f} kWh",
                          f"{E_annual/1000:,.1f} MWh")
            with m2:
                st.metric("Reduksi CO₂", f"{co2_saved:,.1f} ton/thn",
                          f"≈ {co2_saved*1000/21:.0f} pohon/thn")
            with m3:
                st.metric("Rumah Teraliri", f"{houses:,}",
                          f"@ {kwh_house} kWh/bln")

            m4, m5, m6 = st.columns(3)
            with m4:
                st.metric("Kapasitas PLTS", f"{kwp:,.1f} kWp")
            with m5:
                st.metric("Capex Estimasi", f"Rp {capex_total:,.0f} Jt")
            with m6:
                st.metric("LCOE", f"Rp {lcoe:,.0f}/kWh",
                          help="Levelized Cost of Energy, 25 tahun")

            # 25-year projection chart
            st.markdown("#### 📈 Proyeksi Energi 25 Tahun")
            years_proj = list(range(1, 26))
            deg_rate   = 0.005  # 0.5% panel degradation/year
            e_proj     = [E_annual * ((1 - deg_rate) ** (y - 1)) for y in years_proj]
            co2_proj   = [e * co2_grid / 1000 for e in e_proj]
            cum_co2    = np.cumsum(co2_proj).tolist()

            fig_proj = go.Figure()
            fig_proj.add_trace(go.Bar(
                x=years_proj, y=e_proj, name="Energi (kWh/thn)",
                marker_color="#F5A623", opacity=0.85,
                hovertemplate="Tahun %{x}<br>%{y:,.0f} kWh<extra></extra>",
            ))
            fig_proj.add_trace(go.Scatter(
                x=years_proj, y=cum_co2, name="CO₂ Kumulatif (ton)",
                line=dict(color="#00C4B4", width=2.5), yaxis="y2",
                hovertemplate="Tahun %{x}<br>%{y:,.1f} ton CO₂ kumulatif<extra></extra>",
            ))
            fig_proj.update_layout(
                paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
                plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
                font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
                height=320,
                yaxis=dict(title="Energi (kWh/tahun)", gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
                yaxis2=dict(title="CO₂ Kumulatif (ton)", overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)"),
                legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
                margin=dict(l=5, r=5, t=20, b=35),
                xaxis=dict(title="Tahun ke-"),
            )
            st.plotly_chart(fig_proj, use_container_width=True)

            # Summary box
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,rgba(0,196,180,0.08),rgba(245,166,35,0.04));
                        border:1px solid rgba(0,196,180,0.3);border-radius:14px;padding:1.3rem;'>
                <span class="badge">💡 RINGKASAN SIMULASI</span>
                <p style='color:var(--text-secondary);margin-top:0.8rem;line-height:1.85;font-size:0.88rem;'>
                    PLTS seluas <strong style='color:#F5A623;'>{area:,} m²</strong> ({kwp:.1f} kWp) di lokasi
                    dengan radiasi <strong>{h_daily:.2f} kWh/m²/hari</strong> dapat menghasilkan
                    <strong style='color:#00C4B4;'>{E_annual:,.0f} kWh/tahun</strong>,
                    mereduksi <strong style='color:#39D353;'>{co2_saved:,.1f} ton CO₂/tahun</strong>,
                    dan menerangi <strong style='color:#F5A623;'>{houses:,} rumah tangga</strong>.
                    Dengan estimasi capex <strong>Rp {capex_total:,.0f} juta</strong>,
                    LCOE sebesar <strong>Rp {lcoe:,.0f}/kWh</strong> (asumsi 25 tahun).
                </p>
            </div>
            """, unsafe_allow_html=True)
