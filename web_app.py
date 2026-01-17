import streamlit as st
import cv2
import numpy as np
import os
import time
from datetime import datetime
import pyrebase
from PIL import Image

# ---------------------------------------------------------
# 1. SETUP PAGE & "CUSTOMTKINTER" THEME (CSS)
# ---------------------------------------------------------
st.set_page_config(page_title="CarGuard Ultimate", page_icon="🛡️", layout="wide")

# This CSS mimics your 'Theme' class from main.py
st.markdown("""
<style>
    /* 1. MAIN BACKGROUND (Theme.BG_BASE) */
    .stApp {
        background-color: #0B0E14;
        color: #FFFFFF;
    }

    /* 2. SIDEBAR (Theme.SIDEBAR) */
    [data-testid="stSidebar"] {
        background-color: #181C29;
        border-right: 1px solid #2A2F45;
    }

    /* 3. INPUT FIELDS (SoftEntry style) */
    .stTextInput > div > div > input {
        background-color: #0F1116;
        color: white;
        border: 1px solid #2A2F45;
        border-radius: 20px; /* Corner Radius from your code */
        padding: 10px;
    }

    /* 4. BUTTONS (BubblePillBtn style) */
    div.stButton > button {
        background-color: #23283D; /* GLASS_HOVER */
        color: white;
        border: 1px solid #2A2F45;
        border-radius: 30px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #1DD1A1; /* BTN_SUCCESS */
        color: black;
        border-color: #1DD1A1;
        box-shadow: 0 0 15px rgba(29, 209, 161, 0.5);
    }

    /* 5. METRIC CARDS (SoftGlassCard imitation) */
    div[data-testid="metric-container"] {
        background-color: #181C29;
        border: 1px solid #2A2F45;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* 6. HEADERS */
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. YOUR ORIGINAL LOGIC (Unchanged)
# ---------------------------------------------------------
LIVE_RESULTS_FILE = "resources/live_detection_results.txt"
if not os.path.exists("resources"): os.makedirs("resources")

# FIREBASE (Your Config)
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

# YOLO IMPORT
try:
    from yoloPhoto import yoloDetectPhoto
    MODEL_STATUS = True
except ImportError:
    MODEL_STATUS = False
    def yoloDetectPhoto(p): return ["ERR: MODEL MISSING", p]

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
class AuthSystem:
    @staticmethod
    def login(username, password):
        if not DB_STATUS: return False, "Database Offline"
        try:
            all_users = db.child("users").get().val()
            if not all_users: return False, "No users found."
            for uid, user_data in all_users.items():
                if str(user_data.get("username")) == str(username) and str(user_data.get("password")) == str(password):
                    return True, user_data.get("role", "user")
            return False, "Invalid Credentials"
        except Exception as e: return False, str(e)

    @staticmethod
    def register(username, password, email, plate):
        if not DB_STATUS: return False, "Offline"
        data = {"username": username, "password": password, "email": email, "car_plate": plate, "role": "user", "created_at": str(datetime.now())}
        db.child("users").push(data)
        return True, "Success"

# ---------------------------------------------------------
# 4. APP STATE
# ---------------------------------------------------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

# ---------------------------------------------------------
# 5. UI FLOW
# ---------------------------------------------------------

# === LOGIN SCREEN ===
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Create a container that looks like your "SoftGlassCard"
        with st.container():
            st.title("🛡️ CarGuard AI")
            st.caption("ULTIMATE EDITION")
            
            tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
            
            with tab1:
                u = st.text_input("Username", placeholder="Enter Username")
                p = st.text_input("Password", type="password", placeholder="Enter Password")
                if st.button("LOGIN", use_container_width=True):
                    success, role = AuthSystem.login(u, p)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.session_state.role = role
                        st.rerun()
                    else:
                        st.error(role)
            
            with tab2:
                new_u = st.text_input("New User")
                new_p = st.text_input("New Pass", type="password")
                new_e = st.text_input("Email")
                new_pl = st.text_input("Car Plate")
                if st.button("CREATE ACCOUNT", use_container_width=True):
                    s, m = AuthSystem.register(new_u, new_p, new_e, new_pl)
                    if s: st.success("Registered! Login now.")
                    else: st.error(m)

# === MAIN APP ===
else:
    with st.sidebar:
        st.title(f"Hi, {st.session_state.user}")
        st.caption(f"Role: {st.session_state.role}")
        st.markdown("---")
        # Exact icons from your main.py intent
        menu = st.radio("NAVIGATION", ["Dashboard", "Live Scan", "Image Upload", "History", "Feedback", "Profile"])
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "Dashboard":
        st.header("📊 Mission Control")
        
        # SoftGlassCard Mimicry
        c1, c2, c3 = st.columns(3)
        c1.metric("System Status", "ONLINE", "Stable")
        c2.metric("Active Units", "4", "+1")
        c3.metric("Total Scans", "1,240", "+12")
        
        # Grid Layout like your desktop app
        st.markdown("### Quick Actions")
        g1, g2, g3 = st.columns(3)
        if g1.button("📹 LIVE SCAN", use_container_width=True): st.info("Use Sidebar -> Live Scan")
        if g2.button("🖼️ UPLOAD", use_container_width=True): st.info("Use Sidebar -> Image Upload")
        if g3.button("📜 HISTORY", use_container_width=True): st.info("Use Sidebar -> History")

    # --- LIVE SCAN (The Bridge Method) ---
    elif menu == "Live Scan":
        st.header("📹 Live Feed")
        
        img_buffer = st.camera_input("Scanner")
        
        if img_buffer:
            # 1. SAVE TO DISK (Bridge)
            if not os.path.exists("temp"): os.makedirs("temp")
            path = os.path.join("temp", "scan.jpg")
            with open(path, "wb") as f: f.write(img_buffer.getbuffer())
            
            # 2. RUN YOLO
            try:
                result = yoloDetectPhoto(path)
                if isinstance(result, (list, tuple)):
                    plate = result[0]
                    res_path = result[1]
                    
                    c1, c2 = st.columns(2)
                    c1.success(f"DETECTED: {plate}")
                    if os.path.exists(res_path):
                        c2.image(res_path, caption="AI Analysis")
                    
                    # LOG
                    if DB_STATUS:
                        db.child("logs").push({
                            "timestamp": str(datetime.now()),
                            "user": st.session_state.user,
                            "plate": plate,
                            "type": "Live"
                        })
            except Exception as e:
                st.error(f"Error: {e}")

    # --- IMAGE UPLOAD ---
    elif menu == "Image Upload":
        st.header("🖼️ Manual Upload")
        
        file = st.file_uploader("Select Image", type=['jpg', 'png'])
        if file:
            # Save
            if not os.path.exists("temp"): os.makedirs("temp")
            path = os.path.join("temp", file.name)
            with open(path, "wb") as f: f.write(file.getbuffer())
            
            st.image(path, width=300)
            
            if st.button("RUN DETECTION"):
                result = yoloDetectPhoto(path)
                if isinstance(result, (list, tuple)):
                    st.success(f"Plate: {result[0]}")
                    if os.path.exists(result[1]): st.image(result[1])

    # --- HISTORY ---
    elif menu == "History":
        st.header("📜 Logs")
        if DB_STATUS:
            logs = db.child("logs").get().val()
            if logs:
                # Filter Logic
                data = []
                for k, v in logs.items():
                    # Admin sees all, User sees own
                    if st.session_state.role == 'admin' or v.get('user') == st.session_state.user:
                        data.append(v)
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No logs.")
        else:
            st.error("DB Offline")

    # --- FEEDBACK ---
    elif menu == "Feedback":
        st.header("💬 Feedback")
        with st.form("fb"):
            txt = st.text_area("Your feedback")
            rate = st.slider("Rating", 1, 5, 5)
            if st.form_submit_button("SEND"):
                if DB_STATUS:
                    db.child("feedback").push({"user": st.session_state.user, "msg": txt, "rate": rate})
                    st.success("Sent!")

    # --- PROFILE ---
    elif menu == "Profile":
        st.header("👤 Profile")
        if DB_STATUS:
            users = db.child("users").get().val()
            my_data = None
            my_uid = None
            if users:
                for uid, u in users.items():
                    if u.get("username") == st.session_state.user:
                        my_data = u
                        my_uid = uid
                        break
            
            if my_data:
                with st.form("prof"):
                    e = st.text_input("Email", my_data.get("email"))
                    p = st.text_input("Plate", my_data.get("car_plate"))
                    if st.form_submit_button("UPDATE"):
                        db.child("users").child(my_uid).update({"email": e, "car_plate": p})
                        st.success("Updated!")
