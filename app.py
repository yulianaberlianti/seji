""" 
Solar Energy Justice Index (SEJI)
A Nationwide WebGIS Platform for Mapping Solar Potential and Energy Equity in Indonesia's 3T Regions
"""

import streamlit as st

st.set_page_config(
    page_title="SEJI — Solar Energy Justice Index",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;800&display=swap');

:root {
    --solar-gold: #F5A623;
    --solar-amber: #FF6B00;
    --equity-teal: #00B4A6;
    --deep-navy: #0A1628;
    --dark-bg: #0D1B2A;
    --card-bg: #112240;
    --text-primary: #E8F4F8;
    --text-secondary: #8892A4;
    --accent-green: #39D353;
    --accent-red: #FF4560;
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--dark-bg);
    color: var(--text-primary);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background-color: var(--dark-bg);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #112240 100%);
    border-right: 1px solid rgba(245,166,35,0.2);
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--solar-gold) !important;
}

/* Headers */
h1, h2, h3 { font-family: 'Sora', sans-serif; }

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--card-bg);
    border: 1px solid rgba(245,166,35,0.15);
    border-radius: 12px;
    padding: 1rem;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--solar-gold);
    font-size: 2rem;
    font-weight: 800;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--card-bg);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--text-secondary);
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: var(--solar-amber) !important;
    color: white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--solar-amber), var(--solar-gold));
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    font-family: 'Sora', sans-serif;
    padding: 0.5rem 1.5rem;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(255,107,0,0.4);
}

/* Selectbox, Slider */
.stSelectbox > div, .stMultiSelect > div {
    background-color: var(--card-bg);
    border-radius: 8px;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0A1628 0%, #1a2f4a 50%, #0D2137 100%);
    border: 1px solid rgba(245,166,35,0.3);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(245,166,35,0.08) 0%, transparent 70%);
    border-radius: 50%;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #F5A623, #FF6B00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}

.hero-subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

.badge {
    display: inline-block;
    background: rgba(245,166,35,0.15);
    border: 1px solid rgba(245,166,35,0.4);
    color: var(--solar-gold);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
    margin-right: 8px;
}

.info-card {
    background: var(--card-bg);
    border: 1px solid rgba(0,180,166,0.2);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
}

.info-card h4 {
    color: var(--equity-teal);
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.5rem;
}

.info-card p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.6;
}

.seji-score-high { color: #FF4560; font-weight: 800; }
.seji-score-med  { color: #F5A623; font-weight: 800; }
.seji-score-low  { color: #39D353; font-weight: 800; }

/* Data table styling */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(245,166,35,0.15);
    border-radius: 10px;
}

/* Progress bars */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--solar-amber), var(--solar-gold));
    border-radius: 10px;
}

/* Plotly chart border */
[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(245,166,35,0.1);
    border-radius: 12px;
    background: var(--card-bg);
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin: 4px 0;
}
.legend-dot {
    width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem;'>☀️</div>
        <div style='font-family: Sora; font-weight:800; font-size:1.1rem; color:#F5A623;'>SEJI Platform</div>
        <div style='font-size:0.7rem; color:#8892A4; font-family: Space Mono;'>v1.0 — Indonesia 3T Regions</div>
    </div>
    <hr style='border-color: rgba(245,166,35,0.2);'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "🗺️ WebGIS Map", "📊 SEJI Analysis", "⚙️ SEJI Calculator", "📋 Data Explorer", "ℹ️ Methodology"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color: rgba(245,166,35,0.2);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.75rem; color:#8892A4; line-height:1.6;'>
    <strong style='color:#F5A623;'>Data Sources:</strong><br>
    NASA POWER · VIIRS DNB<br>
    WorldPop · BPS · OSM<br>
    BIG · GADM · MODIS<br>
    </div>
    """, unsafe_allow_html=True)

# ── Page Router ──────────────────────────────────────────────────────
if "Dashboard" in page:
    from pages import dashboard
    dashboard.show()
elif "WebGIS" in page:
    from pages import webgis
    webgis.show()
elif "SEJI Analysis" in page:
    from pages import seji_analysis
    seji_analysis.show()
elif "Calculator" in page:
    from pages import calculator
    calculator.show()
elif "Data Explorer" in page:
    from pages import data_explorer
    data_explorer.show()
elif "Methodology" in page:
    from pages import methodology
    methodology.show()
