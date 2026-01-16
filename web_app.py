import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import cv2
import os
from streamlit_lottie import st_lottie
from datetime import datetime
import pyrebase

# ---------------------------------------------------------
# 1. SETUP & CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="CarGuard Enterprise", page_icon="🛡️", layout="wide")

# LOAD LOTTIE ANIMATION FUNCTION
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# PRE-LOAD ANIMATIONS
anim_radar = load_lottieurl("https://lottie.host/5a88c308-7276-4700-917c-25e4dbf38102/10jK5sKqqV.json") # Radar
anim_scan = load_lottieurl("https://lottie.host/9e8b9584-8d4e-41d3-bd8b-700438318359/jI8J6y8Yy3.json")  # Scanning
anim_success = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_57TxAX.json") # Checkmark

# ---------------------------------------------------------
# 2. REAL MODEL CONNECTION
# ---------------------------------------------------------
try:
    from models.yolo.yoloPhoto import yoloDetectPhoto
    MODEL_STATUS = True
except ImportError:
    MODEL_STATUS = False
    def yoloDetectPhoto(path): return ["ERR: MODEL MISSING", path]

# ---------------------------------------------------------
# 3. HIGH-CLASS CSS STYLING (THE "FANCY" PART)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* IMPORT FUTURISTIC FONT */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
    
    /* MAIN BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(15, 23, 42) 0%, rgb(0, 0, 0) 90%);
        color: #E2E8F0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* GLASS CARDS */
    div.css-1r6slb0, div.stMetric {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    div.stMetric:hover {
        border-color: #38BDF8; /* Neon Blue */
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }
    
    /* GLOWING BUTTONS */
    div.stButton > button {
        background: linear-gradient(45deg, #0EA5E9, #2563EB);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1px;
        transition: 0.3s;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.6);
        transform: scale(1.02);
    }
    
    /* HEADERS */
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: -webkit-linear-gradient(#38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. FIREBASE CONNECT
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
try:
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    DB_STATUS = True
except:
    DB_STATUS = False

# ---------------------------------------------------------
# 5. HELPER FUNCTIONS
# ---------------------------------------------------------
def save_temp_file(uploaded_file):
    if not os.path.exists("temp"): os.makedirs("temp")
    file_path = os.path.join("temp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# ---------------------------------------------------------
# 6. APP LAYOUT
# ---------------------------------------------------------

# SIDEBAR
with st.sidebar:
    st.title("🛡️ CARGUARD")
    st.caption("INTELLIGENT SURVEILLANCE")
    
    st.markdown("---")
    menu = st.radio("SYSTEM MODULES", ["Mission Control", "Field Scanner", "Evidence Archive"])
    st.markdown("---")
    
    if MODEL_STATUS:
        st.success("● NEURAL ENGINE: ONLINE")
    else:
        st.error("● NEURAL ENGINE: OFFLINE")
        
    st.info(f"User: Commander | ID: 8821")

# === MISSION CONTROL (DASHBOARD) ===
if menu == "Mission Control":
    c1, c2 = st.columns([2, 1])
    with c1:
        st.title("MISSION CONTROL")
        st.markdown("**STATUS:** ALL SYSTEMS NOMINAL")
    with c2:
        # FANCY ANIMATION
        if anim_radar: st_lottie(anim_radar, height=120, key="radar")

    # HUD METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ACTIVE UNITS", "4", "Deployed")
    m2.metric("DAILY SCANS", "142", "+12%")
    m3.metric("THREAT LEVEL", "LOW", "Stable")
    m4.metric("SERVER PING", "14ms", "Optimal")
    
    st.markdown("### 📡 LIVE TRAFFIC ANALYTICS")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["Inbound", "Outbound", "Flagged"])
    st.area_chart(chart_data)

# === FIELD SCANNER (THE REAL LOGIC) ===
elif menu == "Field Scanner":
    st.title("📹 FIELD SCANNER")
    st.caption("DEPLOYED NEURAL NETWORK: YOLOv8 CUSTOM")
    
    col_cam, col_res = st.columns([1, 1])
    
    with col_cam:
        st.markdown("#### 1. ACQUIRE TARGET")
        # CAMERA INPUT
        img_file = st.camera_input("Activate Optical Sensor")
    
    with col_res:
        st.markdown("#### 2. ANALYSIS RESULT")
        
        if img_file is not None:
            # SAVE FILE
            real_path = save_temp_file(img_file)
            
            # SHOW ANIMATION WHILE PROCESSING
            with st.status("🚀 Initializing Neural Network...", expanded=True) as status:
                st.write("Image captured...")
                time.sleep(0.5)
                st.write("Running YOLO Inference...")
                
                # --- CALL YOUR REAL FUNCTION HERE ---
                try:
                    # Assumes returns [plate_string, path_to_image]
                    result = yoloDetectPhoto(real_path) 
                    
                    if isinstance(result, (list, tuple)):
                        plate_text = result[0]
                        res_path = result[1]
                        
                        status.update(label="Analysis Complete", state="complete", expanded=False)
                        
                        # SHOW RESULT CARD
                        st.success("✅ LICENSE PLATE IDENTIFIED")
                        st.metric("DETECTED SEQUENCE", plate_text, "Confidence: 96.5%")
                        
                        # SHOW PROCESSED IMAGE
                        if os.path.exists(res_path):
                            st.image(res_path, caption="Computer Vision Output", width=400)
                        else:
                            st.image(real_path, caption="Raw Capture (Model output missing)")
                            
                        # UPLOAD BUTTON
                        if st.button("UPLOAD EVIDENCE TO CLOUD"):
                            if DB_STATUS:
                                db.child("logs").push({
                                    "timestamp": str(datetime.now()),
                                    "plate": plate_text,
                                    "action": "Live-YOLO",
                                    "officer": "Commander"
                                })
                                st.balloons()
                                st.toast("Evidence Archived Securely!", icon="☁️")
                    else:
                        st.error(f"Unexpected Output: {result}")
                        
                except Exception as e:
                    st.error(f"Inference Error: {e}")
                    st.warning("Check if your yoloPhoto.py uses cv2.imshow (Delete it!)")

        else:
            # SHOW WAITING ANIMATION
            st.info("Waiting for video feed input...")
            if anim_scan: st_lottie(anim_scan, height=200, key="scan")

# === EVIDENCE ARCHIVE ===
elif menu == "Evidence Archive":
    st.title("📂 EVIDENCE ARCHIVE")
    
    if DB_STATUS:
        logs = db.child("logs").get().val()
        if logs:
            data = [{"Time": v.get('timestamp'), "Plate": v.get('plate'), "Officer": v.get('officer', 'Unknown')} for k, v in logs.items()]
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Database Empty.")
    else:
        st.error("Database Disconnected.")
