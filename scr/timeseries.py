"""Time-Series Forecasting — 10-year solar trend + moving average forecast. v3.0"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, get_timeseries_data, ISLAND_COLORS


def moving_average(data, window=3):
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        result.append(np.mean(data[start:i+1]))
    return result


def forecast_ma(data, steps=12, window=6):
    """Simple moving average forecast."""
    last_window = data[-window:]
    forecast = []
    history = list(data)
    for _ in range(steps):
        pred = np.mean(history[-window:])
        forecast.append(round(pred, 3))
        history.append(pred)
    return forecast


def forecast_linear(data, steps=12):
    """Linear trend + seasonal decomposition forecast."""
    n = len(data)
    x = np.arange(n)
    coeffs = np.polyfit(x, data, 1)
    trend = np.poly1d(coeffs)
    detrended = [data[i] - trend(i) for i in range(n)]
    seasonal = [np.mean([detrended[j] for j in range(i % 12, n, 12)]) for i in range(12)]
    forecast = []
    for i in range(steps):
        idx = n + i
        f = trend(idx) + seasonal[idx % 12]
        forecast.append(round(float(f), 3))
    return forecast


def show():
    df = get_indonesia_3t_data()
    ts  = get_timeseries_data()
    cc  = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">📈 TIME-SERIES</span>
        <h2 class="hero-title" style="font-size:1.55rem;">Tren & Prediksi Time-Series</h2>
        <p class="hero-subtitle">Tren radiasi surya 10 tahun (2015–2024) + prediksi 1 tahun ke depan</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Province select ───────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        prov_sel = st.selectbox("Provinsi", df["province"].tolist())
    with c2:
        param = st.selectbox("Parameter", ["solar", "cloud"],
                             format_func=lambda x: "☀️ Radiasi Surya" if x == "solar" else "☁️ Tutupan Awan")
    with c3:
        method = st.selectbox("Metode Forecast",
                              ["Moving Average (MA)", "Linear Trend + Seasonal"],
                              help="MA = konservatif, Linear = menangkap tren jangka panjang")
    with c4:
        forecast_months = st.slider("Horizon Forecast (bulan)", 3, 24, 12, 3)

    data_dict = ts.get(prov_sel, {})
    raw_data  = data_dict.get(param, [])
    dates_str = data_dict.get("dates", [])
    if not raw_data:
        st.warning("Data tidak tersedia untuk provinsi ini.")
        return

    dates_hist = pd.to_datetime(dates_str)
    dates_fore = pd.date_range(dates_hist[-1] + pd.DateOffset(months=1), periods=forecast_months, freq="MS")

    if method == "Moving Average (MA)":
        forecast = forecast_ma(raw_data, steps=forecast_months, window=6)
    else:
        forecast = forecast_linear(raw_data, steps=forecast_months)

    ma3  = moving_average(raw_data, window=3)
    ma12 = moving_average(raw_data, window=12)

    # Confidence interval (simple ±1.5*std of last 12 months)
    std_last = np.std(raw_data[-12:])
    ci_upper = [f + 1.5 * std_last for f in forecast]
    ci_lower = [max(0.0, f - 1.5 * std_last) for f in forecast]

    label = "Radiasi (kWh/m²/hari)" if param == "solar" else "Cloud Fraction"
    color_raw  = "#F5A623"
    color_ma3  = "#00C4B4"
    color_ma12 = "#8338EC"
    color_fore = "#FF4560"

    # ── Main chart ────────────────────────────────────────────────
    fig = go.Figure()

    # CI band
    fig.add_trace(go.Scatter(
        x=list(dates_fore) + list(dates_fore[::-1]),
        y=ci_upper + ci_lower[::-1],
        fill="toself",
        fillcolor="rgba(255,69,96,0.10)",
        line=dict(color="rgba(255,0,0,0)"),
        name="CI ±1.5σ", showlegend=True,
        hoverinfo="skip",
    ))

    # Raw data
    fig.add_trace(go.Scatter(
        x=dates_hist, y=raw_data,
        name="Data Historis", line=dict(color=color_raw, width=1.2),
        opacity=0.7,
        hovertemplate="%{x|%b %Y}<br>" + label + ": %{y:.3f}<extra></extra>",
    ))

    # MA3
    fig.add_trace(go.Scatter(
        x=dates_hist, y=ma3,
        name="MA-3 bulan", line=dict(color=color_ma3, width=2, dash="dot"),
        hovertemplate="%{x|%b %Y}<br>MA-3: %{y:.3f}<extra></extra>",
    ))

    # MA12
    fig.add_trace(go.Scatter(
        x=dates_hist, y=ma12,
        name="MA-12 bulan", line=dict(color=color_ma12, width=2.5),
        hovertemplate="%{x|%b %Y}<br>MA-12: %{y:.3f}<extra></extra>",
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=dates_fore, y=forecast,
        name=f"Prediksi ({forecast_months} bln)",
        line=dict(color=color_fore, width=2.5, dash="dash"),
        hovertemplate="%{x|%b %Y}<br>Prediksi: %{y:.3f}<extra></extra>",
    ))

    # Separator line
    fig.add_vline(x=str(dates_hist[-1]), line_dash="dash",
                  line_color="rgba(255,255,255,0.25)", line_width=1.5,
                  annotation_text="Batas historis / prediksi",
                  annotation_font=dict(color=cc.get("text", "#C8D8E8"), size=9))

    fig.update_layout(
        paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
        plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
        font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
        height=430,
        yaxis=dict(title=label, gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
        xaxis=dict(title="Waktu", gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
        legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)"), borderwidth=0),
        margin=dict(l=5, r=5, t=30, b=35),
        title=dict(text=f"{prov_sel} — {label} (2015–2024 + Prediksi)", font=dict(color="#F5A623", size=13)),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Stats ─────────────────────────────────────────────────────
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        st.metric("Rata-rata Historis", f"{np.mean(raw_data):.3f}")
    with s2:
        st.metric("Std Dev", f"{np.std(raw_data):.3f}")
    with s3:
        st.metric("Min / Max", f"{min(raw_data):.2f} / {max(raw_data):.2f}")
    with s4:
        st.metric("Prediksi Rata-rata", f"{np.mean(forecast):.3f}")
    with s5:
        trend_dir = "↑ Naik" if forecast[-1] > forecast[0] else "↓ Turun"
        st.metric("Tren Forecast", trend_dir)

    # ── Annual aggregate ──────────────────────────────────────────
    st.markdown("### 📅 Rata-rata Tahunan (2015–2024)")
    annual_means, annual_stds = [], []
    for yr in range(2015, 2025):
        yr_data = [raw_data[i] for i, d in enumerate(dates_hist) if d.year == yr]
        annual_means.append(round(np.mean(yr_data), 3))
        annual_stds.append(round(np.std(yr_data), 3))

    fig_ann = go.Figure()
    fig_ann.add_trace(go.Bar(
        x=list(range(2015, 2025)), y=annual_means,
        name="Rata-rata Tahunan",
        marker_color="#F5A623", opacity=0.85,
        error_y=dict(type="data", array=annual_stds, visible=True, color="#FF8C00"),
        hovertemplate="Tahun %{x}<br>Rata-rata: %{y:.3f}<br>Std: <extra></extra>",
    ))
    # Trend line
    x_arr = np.array(range(10))
    coeffs = np.polyfit(x_arr, annual_means, 1)
    trend_line = np.poly1d(coeffs)(x_arr)
    fig_ann.add_trace(go.Scatter(
        x=list(range(2015, 2025)), y=trend_line.tolist(),
        name="Tren Linear", line=dict(color="#FF4560", width=2, dash="dot"),
    ))
    fig_ann.update_layout(
        paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
        plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
        font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
        height=300,
        yaxis=dict(title=label, gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
        xaxis=dict(dtick=1),
        legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
        margin=dict(l=5, r=5, t=20, b=35),
    )
    st.plotly_chart(fig_ann, use_container_width=True)

    # ── Multi-province compare ────────────────────────────────────
    st.markdown("### 🔄 Komparasi Multi-Provinsi (MA-12)")
    sel_prov = st.multiselect(
        "Pilih Provinsi (max 5)", df["province"].tolist(),
        default=df.head(3)["province"].tolist(), max_selections=5,
    )
    pal = ["#F5A623", "#00C4B4", "#FF4560", "#39D353", "#8338EC"]
    if sel_prov:
        fig_mp = go.Figure()
        for i, pv in enumerate(sel_prov):
            d = ts.get(pv, {}).get(param, [])
            if not d:
                continue
            ma = moving_average(d, 12)
            fig_mp.add_trace(go.Scatter(
                x=dates_hist, y=ma,
                name=pv, line=dict(color=pal[i % len(pal)], width=2),
                hovertemplate=f"{pv} %{{x|%b %Y}}<br>MA-12: %{{y:.3f}}<extra></extra>",
            ))
        fig_mp.update_layout(
            paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
            plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
            font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
            height=340,
            yaxis=dict(title=label, gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
            legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
            margin=dict(l=5, r=5, t=20, b=35),
        )
        st.plotly_chart(fig_mp, use_container_width=True)

    # ── Anomaly detection ─────────────────────────────────────────
    st.markdown("### ⚠️ Deteksi Anomali (> 2σ dari MA-12)")
    mean_val = np.mean(raw_data)
    std_val  = np.std(raw_data)
    anomalies = [(dates_hist[i], raw_data[i]) for i in range(len(raw_data))
                 if abs(raw_data[i] - ma12[i]) > 2 * std_val]
    if anomalies:
        fig_an = go.Figure()
        fig_an.add_trace(go.Scatter(
            x=dates_hist, y=raw_data,
            name="Data", line=dict(color="#F5A623", width=1.5), opacity=0.6,
        ))
        fig_an.add_trace(go.Scatter(
            x=dates_hist, y=ma12,
            name="MA-12", line=dict(color="#00C4B4", width=2),
        ))
        anom_x = [a[0] for a in anomalies]
        anom_y = [a[1] for a in anomalies]
        fig_an.add_trace(go.Scatter(
            x=anom_x, y=anom_y,
            mode="markers", name="Anomali",
            marker=dict(color="#FF4560", size=10, symbol="x",
                       line=dict(color="#FF0000", width=2)),
            hovertemplate="%{x|%b %Y}<br>Nilai: %{y:.3f}<extra>ANOMALI</extra>",
        ))
        fig_an.update_layout(
            paper_bgcolor=cc.get("paper", "rgba(0,0,0,0)"),
            plot_bgcolor=cc.get("plot", "rgba(17,34,64,0.85)"),
            font=dict(color=cc.get("text", "#C8D8E8"), family="Plus Jakarta Sans"),
            height=300,
            yaxis=dict(gridcolor=cc.get("grid", "rgba(255,255,255,0.06)")),
            legend=dict(bgcolor=cc.get("legend", "rgba(7,17,32,0.88)")),
            margin=dict(l=5, r=5, t=20, b=35),
            title=dict(text=f"{len(anomalies)} anomali terdeteksi", font=dict(color="#FF4560", size=12)),
        )
        st.plotly_chart(fig_an, use_container_width=True)
    else:
        st.success("✅ Tidak ada anomali signifikan yang terdeteksi untuk provinsi ini.")
