"""
Shared data generation and utility functions for SEJI Platform v3.0
"""

import streamlit as st
import numpy as np
import pandas as pd


@st.cache_data
def get_indonesia_3t_data():
    np.random.seed(42)

    provinces = [
        {"province": "Papua", "region": "Papua", "island": "Papua", "lat": -4.27, "lon": 138.08, "is_3t": True},
        {"province": "Papua Barat", "region": "Papua", "island": "Papua", "lat": -1.33, "lon": 133.17, "is_3t": True},
        {"province": "Papua Selatan", "region": "Papua", "island": "Papua", "lat": -6.50, "lon": 140.20, "is_3t": True},
        {"province": "Papua Tengah", "region": "Papua", "island": "Papua", "lat": -4.00, "lon": 136.50, "is_3t": True},
        {"province": "Papua Pegunungan", "region": "Papua", "island": "Papua", "lat": -4.80, "lon": 139.00, "is_3t": True},
        {"province": "Maluku", "region": "Maluku", "island": "Maluku", "lat": -3.24, "lon": 130.14, "is_3t": True},
        {"province": "Maluku Utara", "region": "Maluku", "island": "Maluku", "lat": 1.58, "lon": 127.98, "is_3t": True},
        {"province": "Nusa Tenggara Timur", "region": "Nusa Tenggara", "island": "Nusa Tenggara", "lat": -8.66, "lon": 121.08, "is_3t": True},
        {"province": "Nusa Tenggara Barat", "region": "Nusa Tenggara", "island": "Nusa Tenggara", "lat": -8.65, "lon": 117.36, "is_3t": False},
        {"province": "Kalimantan Utara", "region": "Kalimantan", "island": "Kalimantan", "lat": 3.07, "lon": 116.04, "is_3t": True},
        {"province": "Kalimantan Barat", "region": "Kalimantan", "island": "Kalimantan", "lat": 0.00, "lon": 109.34, "is_3t": False},
        {"province": "Kalimantan Tengah", "region": "Kalimantan", "island": "Kalimantan", "lat": -1.68, "lon": 113.38, "is_3t": False},
        {"province": "Kalimantan Selatan", "region": "Kalimantan", "island": "Kalimantan", "lat": -3.09, "lon": 115.28, "is_3t": False},
        {"province": "Kalimantan Timur", "region": "Kalimantan", "island": "Kalimantan", "lat": 1.64, "lon": 116.42, "is_3t": False},
        {"province": "Sulawesi Tenggara", "region": "Sulawesi", "island": "Sulawesi", "lat": -4.14, "lon": 122.17, "is_3t": True},
        {"province": "Gorontalo", "region": "Sulawesi", "island": "Sulawesi", "lat": 0.69, "lon": 122.45, "is_3t": False},
        {"province": "Sulawesi Barat", "region": "Sulawesi", "island": "Sulawesi", "lat": -2.84, "lon": 119.23, "is_3t": True},
        {"province": "Sulawesi Selatan", "region": "Sulawesi", "island": "Sulawesi", "lat": -3.67, "lon": 119.97, "is_3t": False},
        {"province": "Sulawesi Tengah", "region": "Sulawesi", "island": "Sulawesi", "lat": -1.43, "lon": 121.44, "is_3t": False},
        {"province": "Sulawesi Utara", "region": "Sulawesi", "island": "Sulawesi", "lat": 0.62, "lon": 123.97, "is_3t": False},
        {"province": "Aceh", "region": "Sumatera", "island": "Sumatera", "lat": 4.69, "lon": 96.75, "is_3t": False},
        {"province": "Sumatera Utara", "region": "Sumatera", "island": "Sumatera", "lat": 2.11, "lon": 99.54, "is_3t": False},
        {"province": "Riau", "region": "Sumatera", "island": "Sumatera", "lat": 0.29, "lon": 101.70, "is_3t": False},
        {"province": "Kepulauan Riau", "region": "Sumatera", "island": "Sumatera", "lat": 3.94, "lon": 108.14, "is_3t": True},
        {"province": "Bangka Belitung", "region": "Sumatera", "island": "Sumatera", "lat": -2.74, "lon": 106.44, "is_3t": False},
        {"province": "Bengkulu", "region": "Sumatera", "island": "Sumatera", "lat": -3.80, "lon": 102.27, "is_3t": False},
        {"province": "Sumatera Selatan", "region": "Sumatera", "island": "Sumatera", "lat": -3.31, "lon": 104.91, "is_3t": False},
        {"province": "Lampung", "region": "Sumatera", "island": "Sumatera", "lat": -4.55, "lon": 105.40, "is_3t": False},
        {"province": "Sumatera Barat", "region": "Sumatera", "island": "Sumatera", "lat": -0.72, "lon": 100.35, "is_3t": False},
        {"province": "Jambi", "region": "Sumatera", "island": "Sumatera", "lat": -1.61, "lon": 103.62, "is_3t": False},
        {"province": "DKI Jakarta", "region": "Jawa", "island": "Jawa", "lat": -6.21, "lon": 106.85, "is_3t": False},
        {"province": "Jawa Barat", "region": "Jawa", "island": "Jawa", "lat": -7.09, "lon": 107.67, "is_3t": False},
        {"province": "Jawa Tengah", "region": "Jawa", "island": "Jawa", "lat": -7.15, "lon": 110.14, "is_3t": False},
        {"province": "DI Yogyakarta", "region": "Jawa", "island": "Jawa", "lat": -7.80, "lon": 110.37, "is_3t": False},
        {"province": "Jawa Timur", "region": "Jawa", "island": "Jawa", "lat": -7.54, "lon": 112.24, "is_3t": False},
        {"province": "Banten", "region": "Jawa", "island": "Jawa", "lat": -6.40, "lon": 106.10, "is_3t": False},
        {"province": "Bali", "region": "Bali", "island": "Bali", "lat": -8.34, "lon": 115.09, "is_3t": False},
    ]

    df = pd.DataFrame(provinces)
    n = len(df)

    solar_base = np.where(df["island"].isin(["Papua", "Maluku", "Nusa Tenggara"]), 5.2, 4.8)
    solar_base = np.where(df["island"] == "Jawa", 4.5, solar_base)
    df["solar_kwh"] = np.clip(solar_base + np.random.normal(0, 0.3, n), 3.8, 6.0)

    access_base = np.where(df["is_3t"], np.random.uniform(0.3, 0.65, n), np.random.uniform(0.75, 0.99, n))
    df["electricity_access"] = np.clip(access_base, 0.1, 1.0)

    poverty_base = np.where(df["is_3t"], np.random.uniform(15, 40, n), np.random.uniform(4, 15, n))
    df["poverty_rate"] = np.clip(poverty_base, 1, 45)

    pop_base = np.where(
        df["island"] == "Jawa", np.random.uniform(500, 15000, n),
        np.where(df["is_3t"], np.random.uniform(5, 60, n), np.random.uniform(30, 300, n))
    )
    df["pop_density"] = np.clip(pop_base, 2, 16000)

    remote_base = np.where(df["is_3t"], np.random.uniform(0.55, 0.95, n), np.random.uniform(0.05, 0.50, n))
    df["remoteness"] = np.clip(remote_base, 0, 1)

    cloud_base = np.where(
        df["island"].isin(["Papua", "Kalimantan"]),
        np.random.uniform(0.5, 0.8, n), np.random.uniform(0.2, 0.55, n)
    )
    df["cloud_fraction"] = np.clip(cloud_base, 0.1, 0.9)

    # NTL index (VIIRS proxy, 0-1)
    df["ntl_index"] = np.clip(df["electricity_access"] + np.random.normal(0, 0.06, n), 0.05, 1.0).round(3)
    # NTL DN value (0-255)
    df["ntl_dn"] = (df["ntl_index"] * 220 + np.random.normal(0, 5, n)).clip(3, 250).round(1)

    def norm(x, invert=False):
        n_x = (x - x.min()) / (x.max() - x.min() + 1e-9)
        return 1 - n_x if invert else n_x

    solar_norm   = norm(df["solar_kwh"])
    access_norm  = norm(df["electricity_access"], invert=True)
    poverty_norm = norm(df["poverty_rate"])
    pop_norm     = norm(df["pop_density"])
    remote_norm  = norm(df["remoteness"])

    w = {"solar": 0.30, "access": 0.30, "poverty": 0.20, "population": 0.10, "remoteness": 0.10}
    df["seji_score"] = (
        w["solar"]      * solar_norm +
        w["access"]     * access_norm +
        w["poverty"]    * poverty_norm +
        w["population"] * pop_norm +
        w["remoteness"] * remote_norm
    )
    df["seji_score"] = (df["seji_score"] * 100).round(1)

    df["priority"] = pd.cut(
        df["seji_score"], bins=[0, 33, 55, 75, 100],
        labels=["Low", "Moderate", "High", "Critical"],
    )

    df["solar_score"]      = (solar_norm * 100).round(1)
    df["access_score"]     = (access_norm * 100).round(1)
    df["poverty_score"]    = (poverty_norm * 100).round(1)
    df["pop_score"]        = (pop_norm * 100).round(1)
    df["remoteness_score"] = (remote_norm * 100).round(1)

    df["solar_kwh"]    = df["solar_kwh"].round(2)
    df["poverty_rate"] = df["poverty_rate"].round(1)
    df["remoteness"]   = df["remoteness"].round(3)

    return df.sort_values("seji_score", ascending=False).reset_index(drop=True)


@st.cache_data
def get_timeseries_data():
    """Generate 10-year monthly time series for solar & cloud per province."""
    np.random.seed(99)
    df = get_indonesia_3t_data()
    months = 120
    dates = pd.date_range("2015-01", periods=months, freq="MS")
    t = np.arange(months)
    result = {}
    for _, row in df.iterrows():
        base_s = row["solar_kwh"]
        base_c = row["cloud_fraction"]
        solar_ts = base_s + 0.4 * np.sin(2 * np.pi * t / 12) + 0.15 * np.sin(2 * np.pi * t / 6) \
                   + 0.003 * t + np.random.normal(0, 0.18, months)
        cloud_ts = base_c + 0.12 * np.sin(2 * np.pi * t / 12 + 1.5) \
                   + np.random.normal(0, 0.06, months)
        result[row["province"]] = {
            "dates": [str(d.date()) for d in dates],
            "solar": np.clip(solar_ts, 2.5, 7.0).round(3).tolist(),
            "cloud": np.clip(cloud_ts, 0.05, 0.95).round(3).tolist(),
        }
    return result


@st.cache_data
def get_ahp_weights():
    return {
        "Solar Potential": {"weight": 0.30, "description": "GHI radiation (NASA POWER)", "unit": "kWh/m²/day"},
        "Energy Access":   {"weight": 0.30, "description": "Inverse of electrification ratio (VIIRS NTL)", "unit": "ratio"},
        "Poverty Rate":    {"weight": 0.20, "description": "% population below poverty line (BPS)", "unit": "%"},
        "Population":      {"weight": 0.10, "description": "Population density (WorldPop)", "unit": "pop/km²"},
        "Remoteness":      {"weight": 0.10, "description": "Distance from grid & urban centers", "unit": "index 0-1"},
    }


PRIORITY_COLORS = {
    "Critical": "#FF4560",
    "High":     "#F5A623",
    "Moderate": "#00B4A6",
    "Low":      "#39D353",
}

ISLAND_COLORS = {
    "Papua":         "#FF6B6B",
    "Maluku":        "#FFA552",
    "Nusa Tenggara": "#FFD166",
    "Sulawesi":      "#06D6A0",
    "Kalimantan":    "#118AB2",
    "Sumatera":      "#8338EC",
    "Jawa":          "#3A86FF",
    "Bali":          "#FB5607",
}
