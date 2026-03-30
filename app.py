"""
Solar Energy Justice Index (SEJI) — v2.0
Fix: renamed pages → src to avoid Streamlit multi-page conflict
Added: dark/light toggle, caching, spinner, province filter, tooltips
"""

import streamlit as st

st.set_page_config(
    page_title="SEJI — Solar Energy Justice Index",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "province_filter" not in st.session_state:
    st.session_state.province_filter = "Semua Provinsi"

DARK = st.session_state.theme == "dark"

THEME_VARS = """
    --solar-gold:  #F5A623;
    --solar-amber: #E8820C;
    --equity-teal: #00C4B4;
    --accent-red:  #FF4560;
    --accent-green:#2ECC71;
""" + ("""
    --bg-main:       #0B1623;
    --bg-card:       #112240;
    --bg-card2:      #0D1F38;
    --text-primary:  #F0F6FF;
    --text-secondary:#A8B8CC;
    --text-muted:    #6B7E96;
    --border-subtle: rgba(245,166,35,0.18);
""" if DARK else """
    --bg-main:       #F4F7FB;
    --bg-card:       #FFFFFF;
    --bg-card2:      #EDF2F9;
    --text-primary:  #0D1F38;
    --text-secondary:#3A5068;
    --text-muted:    #6B7E96;
    --border-subtle: rgba(245,166,35,0.35);
""")

SIDEBAR_BG = "linear-gradient(180deg,#071120 0%,#0E1E35 100%)" if DARK else "linear-gradient(180deg,#1A3050 0%,#243D5C 100%)"
HERO_BG    = "linear-gradient(135deg,#071120 0%,#0E2040 50%,#071828 100%)" if DARK else "linear-gradient(135deg,#1A3050 0%,#243D5C 50%,#1A2A42 100%)"
CHART_PLOT = "rgba(17,34,64,0.85)" if DARK else "rgba(237,242,249,0.9)"
CHART_GRID = "rgba(255,255,255,0.06)" if DARK else "rgba(0,0,0,0.06)"
CHART_TEXT = "#C8D8E8" if DARK else "#1A2F48"
LEGEND_BG  = "rgba(7,17,32,0.88)" if DARK else "rgba(255,255,255,0.88)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
:root {{ {THEME_VARS} }}

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}}
.main .block-container {{
    padding: 1.5rem 2rem 3rem;
    background-color: var(--bg-main);
    max-width: 1400px;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid rgba(245,166,35,0.22);
}}
section[data-testid="stSidebar"] * {{ color: #D8E8F4 !important; }}
section[data-testid="stSidebar"] .stRadio label {{ font-size:0.9rem; padding:3px 0; }}

/* Metrics */
[data-testid="metric-container"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 1.1rem !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.18);
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.9px;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: var(--solar-gold) !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
}}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--bg-card2);
    border-radius: 12px; padding: 4px; gap: 3px;
    border: 1px solid var(--border-subtle);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 9px; color: var(--text-secondary) !important;
    font-weight: 600; font-size: 0.87rem; padding: 7px 14px;
}}
.stTabs [aria-selected="true"] {{
    background: var(--solar-amber) !important; color:#fff !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg,#E8820C,#F5A623) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    padding: 0.5rem 1.4rem !important; font-size: 0.88rem !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 4px 14px rgba(232,130,12,0.28) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(232,130,12,0.48) !important;
}}

/* Inputs */
.stSelectbox > div > div, .stMultiSelect > div, .stTextInput > div > input {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    border-color: var(--border-subtle) !important;
}}

/* Hero */
.hero-banner {{
    background: {HERO_BG};
    border: 1px solid rgba(245,166,35,0.32);
    border-radius: 18px; padding: 2rem 2.6rem;
    margin-bottom: 1.6rem; position: relative; overflow: hidden;
}}
.hero-banner::after {{
    content:'☀️'; position:absolute; right:2rem; top:50%;
    transform:translateY(-50%); font-size:5rem; opacity:0.1;
}}
.hero-title {{
    font-size: 1.95rem; font-weight: 800;
    background: linear-gradient(135deg,#F5A623 30%,#FF8C42 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0.4rem 0 0; line-height: 1.2;
}}
.hero-subtitle {{ color:#9AB0C8; font-size:0.92rem; margin-top:0.4rem; }}

.badge {{
    display:inline-block; background:rgba(245,166,35,0.16);
    border:1px solid rgba(245,166,35,0.48); color:#F5A623;
    padding:3px 10px; border-radius:20px; font-size:0.68rem;
    font-weight:700; font-family:'Space Mono',monospace;
    letter-spacing:1.2px; margin-right:5px; margin-bottom:5px;
}}

.info-card {{
    background: var(--bg-card); border:1px solid rgba(0,196,180,0.22);
    border-radius:14px; padding:1.3rem; height:100%;
}}
.info-card h4 {{
    color: var(--equity-teal); font-size:0.76rem; font-weight:700;
    text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.5rem;
}}
.info-card p {{ color:var(--text-secondary); font-size:0.87rem; line-height:1.65; margin:0; }}

[data-testid="stDataFrame"] {{
    border:1px solid var(--border-subtle) !important;
    border-radius:12px !important;
}}
[data-testid="stDownloadButton"] > button {{
    background: linear-gradient(135deg,#0D9B8A,#00C4B4) !important;
    box-shadow: 0 4px 14px rgba(0,196,180,0.28) !important;
}}
iframe {{ border-radius:14px; border:1px solid var(--border-subtle); }}

/* Tooltip helper */
.tooltip-box {{
    background: var(--bg-card); border:1px solid var(--border-subtle);
    border-radius:8px; padding:0.6rem 0.9rem;
    font-size:0.78rem; color:var(--text-secondary);
    margin-top:4px; display:block;
}}
</style>
""", unsafe_allow_html=True)

# Pass theme config to all pages via session_state
st.session_state["is_dark"] = DARK
st.session_state["cc"] = {       # chart config shorthand
    "paper": "rgba(0,0,0,0)",
    "plot":  CHART_PLOT,
    "grid":  CHART_GRID,
    "text":  CHART_TEXT,
    "legend": LEGEND_BG,
    "font_color": CHART_TEXT,
}

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:0.8rem 0 0.4rem;'>
        <div style='font-size:2.6rem;line-height:1;'>☀️</div>
        <div style='font-family:Plus Jakarta Sans;font-weight:800;
                    font-size:1rem;color:#F5A623;margin-top:5px;'>SEJI Platform</div>
        <div style='font-size:0.62rem;color:#5A7A9A;font-family:Space Mono;
                    margin-top:2px;'>v2.0 · Indonesia 3T Regions</div>
    </div>
    <hr style='border:none;border-top:1px solid rgba(245,166,35,0.18);margin:8px 0;'>
    """, unsafe_allow_html=True)

    # Dark / Light toggle
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "dark"; st.rerun()
    with c2:
        if st.button("☀ Light", use_container_width=True):
            st.session_state.theme = "light"; st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠 Dashboard", "🗺️ WebGIS Map", "📊 SEJI Analysis",
        "⚙️ SEJI Calculator", "📋 Data Explorer", "ℹ️ Metodologi",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(245,166,35,0.14);margin:8px 0;'>",
                unsafe_allow_html=True)

    # Global province filter
    from utils.data import get_indonesia_3t_data
    _df = get_indonesia_3t_data()
    prov_opts = ["Semua Provinsi"] + sorted(_df["province"].tolist())
    st.session_state.province_filter = st.selectbox(
        "🔍 Filter Provinsi Global", prov_opts, index=0,
        help="Filter ini berlaku di semua halaman untuk fokus ke satu provinsi",
    )

    st.markdown("""
    <hr style='border:none;border-top:1px solid rgba(245,166,35,0.12);margin:8px 0;'>
    <div style='font-size:0.7rem;color:#5A7A9A;line-height:1.85;'>
        <strong style='color:#B8901A;font-size:0.72rem;'>DATA SOURCES</strong><br>
        NASA POWER · VIIRS DNB<br>
        WorldPop · BPS · OSM<br>
        BIG / GADM · MODIS
    </div>
    """, unsafe_allow_html=True)

# ── Router ───────────────────────────────────────────────────────────
with st.spinner("Memuat..."):
    if "Dashboard" in page:
        from src import dashboard; dashboard.show()
    elif "WebGIS" in page:
        from src import webgis; webgis.show()
    elif "SEJI Analysis" in page:
        from src import seji_analysis; seji_analysis.show()
    elif "Calculator" in page:
        from src import calculator; calculator.show()
    elif "Data Explorer" in page:
        from src import data_explorer; data_explorer.show()
    elif "Metodologi" in page:
        from src import methodology; methodology.show()
