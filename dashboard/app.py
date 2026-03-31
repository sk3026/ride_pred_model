import streamlit as st
import requests
from streamlit_folium import st_folium
import sys
import os

# FIX IMPORT PATH
sys.path.append(os.path.abspath("../src"))
from spatial_pipeline import generate_heatmap

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RidePulse · Demand Intelligence",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {
    --bg-base:      #0b0f1a;
    --bg-card:      #111827;
    --bg-hover:     #1a2236;
    --border:       #1e2d45;
    --accent:       #f0b429;
    --accent-dim:   rgba(240,180,41,.15);
    --accent-glow:  rgba(240,180,41,.35);
    --green:        #22c55e;
    --amber:        #f59e0b;
    --red:          #ef4444;
    --text-primary: #e8edf5;
    --text-muted:   #6b7fa3;
    --text-label:   #94a3b8;
    --mono:         'Space Mono', monospace;
    --sans:         'DM Sans', sans-serif;
}

/* ── App shell ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-base) !important;
    font-family: var(--sans) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Header banner ── */
.ridepulse-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 28px 32px 22px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.ridepulse-header .logo {
    font-family: var(--mono);
    font-size: 22px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -0.5px;
}
.ridepulse-header .tagline {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 2px;
}
.live-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse-dot 2s infinite;
    margin-left: auto;
}
@keyframes pulse-dot { 0%,100%{opacity:1;} 50%{opacity:.3;} }

/* ── Sidebar labels ── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    font-family: var(--mono) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--text-muted) !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] .st-emotion-cache-10trblm {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
    font-size: 13px !important;
    letter-spacing: 1px;
}

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div {
    background: var(--border) !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
    box-shadow: 0 0 8px var(--accent-glow) !important;
}
.stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] {
    color: var(--text-muted) !important;
}

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    background: var(--bg-hover) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: var(--sans) !important;
}

/* ── Predict button ── */
div[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: #0b0f1a !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 32px !important;
    width: 100% !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 20px var(--accent-glow) !important;
    transition: transform .15s, box-shadow .15s !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px var(--accent-glow) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 20px 24px !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
}
[data-testid="metric-container"] label {
    font-family: var(--mono) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: var(--text-muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

/* ── Alert / status badges ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    letter-spacing: .5px !important;
    border: none !important;
}

/* ── Section headings ── */
.section-heading {
    font-family: var(--mono);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    color: var(--text-muted);
    padding: 0 0 10px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-heading span.accent { color: var(--accent); }

/* ── Info box ── */
.info-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    border-radius: 20px;
    padding: 6px 16px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 20px;
}

/* ── Map wrapper ── */
.map-container {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 32px rgba(0,0,0,.5);
}

/* ── Error / warning states ── */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(239,68,68,.08) !important;
    border-left: 3px solid var(--red) !important;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Footer ── */
.dashboard-footer {
    text-align: center;
    font-family: var(--mono);
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 1.5px;
    padding: 24px 0 8px;
    border-top: 1px solid var(--border);
    margin-top: 40px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="ridepulse-header">
    <div>
        <div class="logo">⬡ RidePulse</div>
        <div class="tagline">Demand Intelligence Platform</div>
    </div>
    <div class="live-dot" title="Live"></div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LOAD LOCATIONS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_locations():
    try:
        res = requests.get("http://127.0.0.1:5000/locations", timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return []

with st.spinner("Connecting to data layer…"):
    locations = load_locations()

if not locations:
    st.error("**Backend unreachable.** Ensure the Flask server is running on port 5000.")
    st.stop()


# ─────────────────────────────────────────────
#  SIDEBAR CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configuration")
    st.markdown("---")

    hour = st.slider(
        "Hour of Day",
        min_value=0, max_value=23, value=10,
        help="Select prediction hour (24 h)"
    )

    # Human-readable hour display
    ampm = "AM" if hour < 12 else "PM"
    display_hour = hour if hour in (0, 12) else hour % 12
    st.markdown(
        f"<div class='info-pill'>🕐 {display_hour:02d}:00 {ampm}</div>",
        unsafe_allow_html=True
    )

    day = st.selectbox(
        "Day of Week",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )

    zone_list = [loc["location_id"] for loc in locations]
    selected_zone = st.selectbox(
        "Zone",
        zone_list,
        format_func=lambda x: f"Zone {x}"
    )

    st.markdown("---")
    predict_clicked = st.button("⚡ Run Prediction")

    st.markdown("---")
    st.markdown(
        "<p style='font-size:10px;color:#3d5068;text-align:center;'>"
        "RidePulse v2.0 · ML-Powered</p>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
#  API HELPER
# ─────────────────────────────────────────────
def get_prediction(hour: int, day: str, location_id) -> dict | None:
    try:
        res = requests.post(
            "http://127.0.0.1:5000/predict",
            json={"hour": hour, "day": day, "location_id": location_id},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()
    except Exception:
        return None


# ─────────────────────────────────────────────
#  MAIN CONTENT — two columns: metrics | map
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 2], gap="large")

# ── LEFT: Prediction Panel ──────────────────
with left_col:
    st.markdown(
        "<div class='section-heading'><span class='accent'>◈</span> Demand Forecast</div>",
        unsafe_allow_html=True,
    )

    if predict_clicked:
        with st.spinner("Computing forecast…"):
            st.session_state.result = get_prediction(hour, day, selected_zone)

    result = st.session_state.get("result")

    if result:
        # Zone + Demand metrics
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Zone", f"#{result['location']}")
        with m2:
            st.metric("Predicted Demand", round(result["predicted_demand"], 2))

        # Demand level badge
        level = result["demand_level"]
        st.markdown("<br>", unsafe_allow_html=True)
        if level == "High":
            st.error(f"🔥 HIGH DEMAND — Deploy additional fleet")
        elif level == "Moderate":
            st.warning(f"⚠️ MODERATE DEMAND — Monitor closely")
        else:
            st.success(f"✅ LOW DEMAND — Standard coverage")

        # Context summary card
        st.markdown(
            f"""
            <div style="
                margin-top:16px;
                background:var(--bg-card);
                border:1px solid var(--border);
                border-radius:10px;
                padding:16px 20px;
            ">
                <div style="font-family:var(--mono);font-size:10px;
                            letter-spacing:2px;color:var(--text-muted);
                            text-transform:uppercase;margin-bottom:12px;">
                    Query Snapshot
                </div>
                <table style="width:100%;font-size:13px;border-collapse:collapse;">
                    <tr>
                        <td style="color:var(--text-muted);padding:4px 0;
                                   font-family:var(--mono);font-size:11px;">DAY</td>
                        <td style="text-align:right;font-weight:500;">{day}</td>
                    </tr>
                    <tr>
                        <td style="color:var(--text-muted);padding:4px 0;
                                   font-family:var(--mono);font-size:11px;">HOUR</td>
                        <td style="text-align:right;font-weight:500;">
                            {display_hour:02d}:00 {ampm}
                        </td>
                    </tr>
                    <tr>
                        <td style="color:var(--text-muted);padding:4px 0;
                                   font-family:var(--mono);font-size:11px;">ZONE ID</td>
                        <td style="text-align:right;font-weight:500;">{result['location']}</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        # Empty-state illustration
        st.markdown(
            """
            <div style="
                margin-top:24px;
                text-align:center;
                padding:40px 20px;
                border:1px dashed var(--border);
                border-radius:12px;
                color:var(--text-muted);
            ">
                <div style="font-size:36px;margin-bottom:12px;">◎</div>
                <div style="font-family:var(--mono);font-size:11px;
                            letter-spacing:2px;text-transform:uppercase;">
                    No prediction yet
                </div>
                <div style="font-size:12px;margin-top:6px;color:#3d5068;">
                    Configure inputs and click Run
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── RIGHT: Heatmap ──────────────────────────
with right_col:
    st.markdown(
        "<div class='section-heading'><span class='accent'>◈</span> Spatial Heatmap</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='map-container'>", unsafe_allow_html=True)
    try:
        map_obj = generate_heatmap(hour=hour, selected_zone=selected_zone)
        st_folium(map_obj, width=None, height=480, returned_objects=[])
    except Exception as e:
        st.warning(f"**Map unavailable** — {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(
    "<div class='dashboard-footer'>RidePulse · Demand Intelligence · "
    "Powered by Streamlit &amp; Flask</div>",
    unsafe_allow_html=True,
)