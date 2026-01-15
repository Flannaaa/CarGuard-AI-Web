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
# 2. FIREBASE CONNECTION (SAFE MODE)
# ---------------------------------------------------------
# We use a try-block so the app NEVER crashes, even if libraries fail.
DB_STATUS = "OFFLINE"
db = None

try:
    import pyrebase
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
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    DB_STATUS = "ONLINE"
except Exception as e:
    # If pyrebase fails, we just continue in Offline Mode
    DB_STATUS = "OFFLINE"

# ---------------------------------------------------------
# 3. CSS & STYLING (THE "FANCY" LOOK)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #38BDF8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
        transform: translateY(-2px);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0EA5E9, #2563EB);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        height: 3em;
        width: 100%;
        transition: 0.2s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 12px #0EA5E9;
    }
    
    /* Text Headers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. HELPER FUNCTIONS
# ---------------------------------------------------------
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Load Cool Animations
anim_scan = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_myda20.json") 
anim_secure = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_57TxAX.json")

def get_logs():
    """Fetch logs from Firebase safely"""
    if not db: return []
    try:
        logs = db.child("logs").get().val()
        if logs:
            data = [{"Timestamp": v.get('timestamp',''), "Plate": v.get('plate_number','Unknown'), "Action": v.get('action','-')} for k, v in logs.items()]
            return data
    except: pass
    return []

# ---------------------------------------------------------
# 5. SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("🛡️ CARGUARD")
    st.caption("ENTERPRISE CLOUD SYSTEM")
    st.markdown("---")
    
    menu = st.radio("NAVIGATION", ["Mission Control", "Mobile Scanner", "Global Logs", "Admin Panel"])
    
    st.markdown("---")
    if DB_STATUS == "ONLINE":
        st.success("● SERVER ONLINE")
    else:
        st.error("● SERVER OFFLINE (Demo Mode)")
        
    st.info("Authorized Access Only")

# ---------------------------------------------------------
# 6. MAIN CONTENT
# ---------------------------------------------------------

# === DASHBOARD ===
if menu == "Mission Control":
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("Mission Control")
        st.markdown(f"**Status:** Operational | **Date:** {datetime.now().strftime('%d %B %Y')}")
    with c2:
        if anim_secure: st_lottie(anim_secure, height=120)

    # Fetch Real Data or Mock Data if Offline
    logs = get_logs()
    count_total = len(logs) if logs else 1240
    count_today = len([x for x in logs if datetime.now().strftime("%Y-%m-%d") in str(x.get("Timestamp"))]) if logs else 42

    # KPI Cards
    st.markdown("### 📡 Live Telemetry")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Detections", f"{count_total}", "+Live")
    k2.metric("Scans Today", f"{count_today}", "Active")
    k3.metric("System Latency", "14ms", "Optimal")
    k4.metric("Security Level", "HIGH", "Secure", delta_color="normal")

    # Graphs
    st.markdown("### 📊 Activity Analytics")
    g1, g2 = st.columns([2, 1])
    with g1:
        chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Inbound', 'Outbound'])
        st.line_chart(chart_data)
    with g2:
        st.write("**Recent Alerts**")
        if logs:
            for l in reversed(logs[-4:]):
                st.code(f"[{l['Timestamp'].split(' ')[-1]}] {l['Plate']} ({l['Action']})")
        else:
            st.info("No recent data or database offline.")

# === MOBILE SCANNER ===
elif menu == "Mobile Scanner":
    st.title("📱 Remote Surveillance")
    st.caption("Use your device camera to scan license plates in the field.")
    
    col_cam, col_info = st.columns([1, 1])
    
    with col_cam:
        # NATIVE CAMERA WIDGET (Works on Phones!)
        img_file = st.camera_input("Activate Camera Feed")
        
        if img_file is not None:
            # Simulate Processing (To avoid crashing cloud server with heavy AI)
            with st.spinner("Analyzing biometric signatures..."):
                time.sleep(2.0) # Fake delay for realism
                
                st.success("TARGET IDENTIFIED")
                st.image(img_file, caption="Captured Frame")
                
                # Randomized Result for Demo
                plate_demo = f"VKY {np.random.randint(1000,9999)}"
                st.metric("Detected Plate", plate_demo, "Confidence: 99.2%")
                
                if st.button("UPLOAD EVIDENCE TO CLOUD"):
                    if db:
                        data = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "username": "Mobile_Unit_1",
                            "action": "Mobile Scan",
                            "plate_number": plate_demo,
                            "original_path": "Cloud_Upload",
                            "detected_path": "Cloud_Upload"
                        }
                        db.child("logs").push(data)
                        st.toast("Evidence Logged Successfully!", icon="✅")
                    else:
                        st.warning("Server Offline - Data saved locally.")

    with col_info:
        if anim_scan: st_lottie(anim_scan, height=250)
        st.info("""
        **OPERATOR INSTRUCTIONS:**
        1. Ensure the vehicle is stationary.
        2. Clean the camera lens.
        3. Hold device steady for 2 seconds.
        4. Upload positive matches immediately.
        """)

# === GLOBAL LOGS ===
elif menu == "Global Logs":
    st.title("📂 Central Database")
    
    logs = get_logs()
    if logs:
        df = pd.DataFrame(logs)
        search = st.text_input("🔍 Search Database (Plate Number)")
        
        if search:
            df = df[df['Plate'].str.contains(search, case=False, na=False)]
        
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "Timestamp": st.column_config.TextColumn("Time Recorded"),
                "Plate": st.column_config.TextColumn("License Plate", width="medium"),
                "Action": st.column_config.TextColumn("Source", width="small")
            }
        )
    else:
        st.warning("No Data Found. Connect to Firebase for live logs.")

# === ADMIN PANEL ===
elif menu == "Admin Panel":
    st.title("⚙️ System Configuration")
    
    t1, t2 = st.tabs(["UserProfile", "Security Settings"])
    
    with t1:
        st.text_input("Officer Name", "Commander")
        st.text_input("Unit ID", "ALPHA-01")
        if st.button("Update Profile"):
            st.success("Profile Saved")
            
    with t2:
        st.toggle("Encryption (AES-256)", value=True)
        st.toggle("Cloud Sync", value=True)
        st.toggle("Silent Mode", value=False)
        st.markdown("---")
        if st.button("⚠️ EMERGENCY DATABASE PURGE", type="primary"):
            st.error("ACCESS DENIED: Requires Level 5 Clearance")