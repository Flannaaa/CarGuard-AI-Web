import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="CarGuard Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. STYLING (The "Cyber" Look)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Dark Theme Background */
    .stApp {
        background-color: #0F172A; /* Dark Navy */
        color: #F8FAFC;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    
    /* Glowing Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #0EA5E9; /* Cyan Glow */
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.4);
        transform: translateY(-2px);
    }
    
    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0EA5E9, #2563EB);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. ANIMATION LOADER
# ---------------------------------------------------------
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=1)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# ---------------------------------------------------------
# 4. SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("🛡️ CARGUARD")
    st.caption("AI SURVEILLANCE SYSTEM")
    st.success("● SYSTEM ONLINE")
    
    st.markdown("---")
    menu = st.radio("NAVIGATION", ["Mission Control", "Mobile Scanner", "Live Logs"])
    st.markdown("---")
    
    st.info("🔒 Secure Connection: TLS 1.3")

# ---------------------------------------------------------
# 5. PAGE: MISSION CONTROL
# ---------------------------------------------------------
if menu == "Mission Control":
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("Mission Control")
        st.markdown(f"**Unit:** ALPHA-01 | **Date:** {datetime.now().strftime('%d %B %Y')}")
    with c2:
        # A cool spinning radar animation
        anim = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_57TxAX.json")
        if anim: st_lottie(anim, height=100)

    # Fake Data for the Demo (Looks very real!)
    st.markdown("### 📡 Live Telemetry")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Vehicles Scanned", "1,248", "+12/hr")
    k2.metric("Threats Detected", "0", "Stable")
    k3.metric("System Latency", "14ms", "Optimal")
    k4.metric("Cloud Storage", "84%", "Normal")

    st.markdown("### 📊 Activity Analytics")
    chart_data = pd.DataFrame(
        np.random.randn(20, 2),
        columns=['Inbound Traffic', 'Outbound Traffic']
    )
    st.line_chart(chart_data)

# ---------------------------------------------------------
# 6. PAGE: MOBILE SCANNER
# ---------------------------------------------------------
elif menu == "Mobile Scanner":
    st.title("📱 Field Scanner")
    st.caption("Use device camera for manual license plate verification.")
    
    col_cam, col_res = st.columns([1, 1])
    
    with col_cam:
        img = st.camera_input("Capture License Plate")
    
    with col_res:
        if img:
            with st.spinner("Processing biometric signature..."):
                time.sleep(1.5) # Fake "Processing" delay
                st.success("✅ PLATE RECOGNIZED")
                
                # Generate a random plate for the demo
                fake_plate = f"VKY {np.random.randint(1000, 9999)}"
                st.metric("Detected Number", fake_plate, "Confidence: 99.8%")
                
                st.image(img, caption="Evidence Capture")
                
                if st.button("UPLOAD TO HQ"):
                    st.toast("Evidence uploaded to Central Database!", icon="☁️")
                    st.balloons()
        else:
            st.info("Waiting for video feed...")
            anim_scan = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_myda20.json")
            if anim_scan: st_lottie(anim_scan, height=200)

# ---------------------------------------------------------
# 7. PAGE: LOGS
# ---------------------------------------------------------
elif menu == "Live Logs":
    st.title("📂 Enforcement Logs")
    
    # Create a nice looking fake table
    data = {
        "Timestamp": ["10:42:01", "10:45:15", "10:48:33", "11:02:10"],
        "Plate Number": ["VKA 1234", "WB 8821 C", "JEU 9922", "VKY 4040"],
        "Status": ["Clear", "Clear", "Clear", "Flagged"],
        "Officer": ["Unit-1", "Unit-1", "Unit-2", "Unit-1"]
    }
    df = pd.DataFrame(data)
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status", 
                help="Security Status", 
                validate="^(Flagged|Clear)$"
            )
        }
    )
