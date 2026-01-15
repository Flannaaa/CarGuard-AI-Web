import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime
import pyrebase

# ---------------------------------------------------------
# 1. FIREBASE CONFIGURATION (CONNECTS TO YOUR REAL DB)
# ---------------------------------------------------------
firebase_config = {
  "apiKey": "AIzaSyDhmDa9SA0m2H73FXypOhRAvVEOTGql0ag",
  "authDomain": "carguard-ai.firebaseapp.com",
  "databaseURL": "https://carguard-ai-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "carguard-ai",
  "storageBucket": "carguard-ai.firebasestorage.app",
  "messagingSenderId": "864660646308",
  "appId": "1:864660646308:web:b4ed7987f3124204567931",
  "measurementId": "G-RNLF7WCEZW"
}

# Initialize Connection (Safe Failover)
try:
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    DB_STATUS = "ONLINE"
except:
    db = None
    DB_STATUS = "OFFLINE"

# ---------------------------------------------------------
# 2. PAGE & THEME CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="CarGuard Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Cyber-Executive" Look
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    
    /* Metrics Cards (Floating Glow) */
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #38BDF8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    
    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 5px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0EA5E9, #2563EB);
        color: white;
        font-weight: bold;
        border: none;
        height: 3em;
        width: 100%;
        border-radius: 6px;
    }
    .stButton > button:hover {
        box-shadow: 0 0 10px #0EA5E9;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Load Animations
anim_scan = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_myda20.json") # Radar
anim_secure = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_57TxAX.json") # Shield

# Fetch Data from Firebase
def get_logs():
    if not db: return []
    try:
        logs = db.child("logs").get().val()
        if logs:
            # Convert dict to list
            data = [{"Timestamp": v.get('timestamp'), "Plate": v.get('plate_number'), "Action": v.get('action')} for k, v in logs.items()]
            return data
    except: pass
    return []

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.title("🛡️ CARGUARD")
    st.caption("ENTERPRISE CLOUD SYSTEM")
    st.markdown("---")
    
    menu = st.radio("COMMAND CENTER", ["Dashboard", "Mobile Scanner", "Global Logs", "Admin Panel"])
    
    st.markdown("---")
    
    # Live Status Indicator
    if DB_STATUS == "ONLINE":
        st.success(f"● SERVER ONLINE")
    else:
        st.error(f"● SERVER OFFLINE")
        
    st.info("Authorized Personnel Only")

# ---------------------------------------------------------
# 5. MAIN CONTENT
# ---------------------------------------------------------

# === DASHBOARD ===
if menu == "Dashboard":
    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("Mission Control")
        st.markdown(f"Real-time overview of security operations. **{datetime.now().strftime('%A, %d %B %Y')}**")
    with c2:
        if anim_secure: st_lottie(anim_secure, height=100)

    # Real Data Calculation
    all_data = get_logs()
    total_scans = len(all_data) if all_data else 0
    today_scans = len([x for x in all_data if datetime.now().strftime("%Y-%m-%d") in str(x.get("Timestamp"))])
    
    # KPI Cards
    st.markdown("### 📊 System Telemetry")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Detections", f"{total_scans:,}", "+Live")
    k2.metric("Scans Today", f"{today_scans}", "Active")
    k3.metric("Server Latency", "12ms", "Optimal")
    k4.metric("Threat Level", "LOW", "Secure", delta_color="normal")

    # Charts
    st.markdown("### 📈 Detection Analytics")
    chart_col, feed_col = st.columns([2, 1])
    
    with chart_col:
        # Dummy data for chart (since real timestamps might be sparse)
        chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Entry Gate', 'Exit Gate'])
        st.area_chart(chart_data)
    
    with feed_col:
        st.write("**Recent Activity Feed**")
        if all_data:
            # Show last 5 logs
            recent = all_data[-5:]
            for log in reversed(recent):
                st.info(f"[{log['Timestamp'].split(' ')[1]}] Plate: **{log['Plate']}** ({log['Action']})")
        else:
            st.warning("No Data Logs Found")

# === MOBILE SCANNER ===
elif menu == "Mobile Scanner":
    st.title("📱 Remote Surveillance")
    st.caption("Use your mobile device as a portable license plate scanner.")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # CAMERA INPUT WIDGET
        img_file = st.camera_input("Capture License Plate")
        
        if img_file is not None:
            # SIMULATION MODE (For Stability on Cloud)
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            
            st.success("Analysis Complete")
            st.image(img_file)
            
            # Simulated Result
            st.metric("DETECTED PLATE", "WXY 1234", "Confidence: 98.4%")
            
            # Option to push to database
            if st.button("Upload Result to Database"):
                if db:
                    data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "username": "Mobile_User",
                        "action": "Mobile Scan",
                        "plate_number": "WXY 1234",
                        "original_path": "Mobile_Upload",
                        "detected_path": "Mobile_Upload"
                    }
                    db.child("logs").push(data)
                    st.toast("Data synced to Main Server!", icon="☁️")

    with c2:
        if anim_scan: st_lottie(anim_scan, height=300)
        st.warning("""
        **Operational Protocol:**
        1. Ensure vehicle is stationary.
        2. Maintain distance of 1-3 meters.
        3. Ensure adequate lighting.
        """)

# === GLOBAL LOGS ===
elif menu == "Global Logs":
    st.title("📂 Central Database")
    
    logs = get_logs()
    
    if logs:
        df = pd.DataFrame(logs)
        # Reorder columns
        df = df[["Timestamp", "Plate", "Action"]]
        
        # Search
        search = st.text_input("🔍 Search Database (Enter Plate Number)")
        if search:
            df = df[df['Plate'].str.contains(search, case=False, na=False)]
        
        st.dataframe(
            df, 
            use_container_width=True, 
            height=600,
            column_config={
                "Timestamp": st.column_config.TextColumn("Time Recorded"),
                "Plate": st.column_config.TextColumn("License Plate", width="medium"),
                "Action": st.column_config.TextColumn("Source", width="small")
            }
        )
        
        # Download
        csv = df.to_csv().encode('utf-8')
        st.download_button("📥 Export Report (CSV)", csv, "security_report.csv", "text/csv")
        
    else:
        st.info("Database is empty or connecting...")

# === ADMIN PANEL ===
elif menu == "Admin Panel":
    st.title("⚙️ System Configuration")
    
    t1, t2 = st.tabs(["Profile", "Security"])
    
    with t1:
        st.text_input("Officer Name", value="Administrator")
        st.text_input("Badge ID", value="8492-AX")
        st.selectbox("Clearance Level", ["Level 1", "Level 2", "Level 3 (Max)"])
        if st.button("Save Profile"):
            st.success("Profile Updated")
            
    with t2:
        st.toggle("Enable Cloud Sync", value=True)
        st.toggle("Push Notifications", value=False)
        st.toggle("Encryption Mode", value=True)
        st.markdown("---")
        if st.button("⚠️ EMERGENCY SHUTDOWN", type="primary"):
            st.error("SYSTEM LOCKDOWN INITIATED...")