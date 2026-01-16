import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime
import pyrebase

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CSS
# ---------------------------------------------------------
st.set_page_config(page_title="CarGuard Ultimate", page_icon="🛡️", layout="wide")

# Custom CSS to match your "Dreamy" Desktop Theme
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #181C29; color: white; border: 1px solid #2A2F45; border-radius: 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #181C29; border-right: 1px solid #2A2F45; }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #9D84FE, #76E4F7);
        color: black; font-weight: bold; border: none; border-radius: 20px;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(118, 228, 247, 0.5); }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: #181C29; border: 1px solid #2A2F45; border-radius: 15px; padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. FIREBASE CONNECTION
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
    # auth = firebase.auth() # Authentication requires separate setup, using DB for simplified demo
    DB_STATUS = True
except:
    DB_STATUS = False
    st.error("⚠️ Database Connection Failed")

# ---------------------------------------------------------
# 3. AUTHENTICATION & SESSION
# ---------------------------------------------------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

def login_user(username, password):
    if not DB_STATUS: return False, "Offline"
    users = db.child("users").get().val()
    if users:
        for uid, u in users.items():
            if u.get("username") == username and u.get("password") == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.role = u.get("role", "user")
                st.rerun()
    return False, "Invalid Credentials"

def register_user(username, password, email, plate, car_model):
    if not DB_STATUS: return
    data = {
        "username": username, "password": password, "email": email,
        "car_plate": plate, "car_model": car_model, "role": "user",
        "created_at": str(datetime.now())
    }
    db.child("users").push(data)
    st.success("Account Created! Please Login.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# ---------------------------------------------------------
# 4. APP LOGIC
# ---------------------------------------------------------

# === LOGIN PAGE ===
if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.title("🛡️ CarGuard AI")
        st.markdown("### Ultimate Edition")
        st.info("Please Log In or Register to access the system.")
    
    with c2:
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("LOGIN >>"):
                success, msg = login_user(u, p)
                if not success: st.error(msg)
        
        with tab2:
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password", type="password")
            new_e = st.text_input("Email")
            new_plate = st.text_input("Car Plate")
            new_model = st.text_input("Car Model")
            if st.button("CREATE ACCOUNT"):
                if new_u and new_p:
                    register_user(new_u, new_p, new_e, new_plate, new_model)
                else:
                    st.warning("Fill all fields")

# === MAIN APP (LOGGED IN) ===
else:
    # SIDEBAR
    with st.sidebar:
        st.title(f"Hi, {st.session_state.user}")
        st.caption(f"Role: {st.session_state.role}")
        st.markdown("---")
        menu = st.radio("MENU", ["Dashboard", "Live Scanner", "Image Upload", "History Logs", "Feedback", "Profile"])
        st.markdown("---")
        if st.button("Log Out"): logout()

    # --- DASHBOARD ---
    if menu == "Dashboard":
        st.title("📊 Mission Control")
        c1, c2, c3 = st.columns(3)
        c1.metric("System Status", "ONLINE", "Stable")
        
        # Fetch Real Count
        logs = db.child("logs").get().val() if DB_STATUS else {}
        count = len(logs) if logs else 0
        c2.metric("Total Scans", count, "+Live")
        c3.metric("Security Level", "HIGH", "Active")
        
        st.image("https://assets.website-files.com/5d5e255a8f242506f5a113d5/5d5e255a8f24256679a11413_hero-overlay.png", caption="AI Surveillance Active")

    # --- LIVE SCANNER ---
    elif menu == "Live Scanner":
        st.title("📹 Field Scanner")
        st.caption("Use your camera to scan plates. Click 'Take Photo' below.")
        
        # THE CAMERA INPUT (THIS IS THE 'TAKE PHOTO' BUTTON)
        img_file = st.camera_input("POINT AT VEHICLE AND SHOOT")
        
        if img_file:
            st.success("✅ IMAGE CAPTURED - PROCESSING...")
            # Simulate Processing
            time.sleep(1.5)
            
            # Simulated Detection Result
            fake_plate = f"VKY {np.random.randint(1000, 9999)}"
            
            c1, c2 = st.columns(2)
            c1.image(img_file, caption="Captured Evidence")
            c2.metric("DETECTED PLATE", fake_plate, "Confidence: 98%")
            
            if c2.button("SAVE TO DATABASE"):
                data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "username": st.session_state.user,
                    "action": "Live Scan",
                    "plate_number": fake_plate,
                    "detected_path": "Cloud_Image",
                    "original_path": "Cloud_Image"
                }
                db.child("logs").push(data)
                st.toast("Saved to History!")

    # --- IMAGE UPLOAD ---
    elif menu == "Image Upload":
        st.title("🖼️ Manual Upload")
        file = st.file_uploader("Upload Car Image", type=["jpg", "png", "jpeg"])
        
        if file:
            st.image(file, width=400)
            if st.button("RUN AI DETECTION"):
                with st.spinner("Running YOLOv8..."):
                    time.sleep(2)
                    detected = f"ABC {np.random.randint(100,999)}"
                    st.success(f"PLATE FOUND: {detected}")
                    
                    # Log
                    data = {"timestamp": str(datetime.now()), "username": st.session_state.user, "action": "Upload", "plate_number": detected}
                    db.child("logs").push(data)

    # --- HISTORY LOGS ---
    elif menu == "History Logs":
        st.title("📜 Scan History")
        
        logs = db.child("logs").get().val()
        if logs:
            # Convert Firebase JSON to DataFrame
            data = [{"Time": v.get('timestamp'), "User": v.get('username'), "Plate": v.get('plate_number'), "Type": v.get('action')} for k, v in logs.items()]
            df = pd.DataFrame(data)
            
            # Admin sees all, User sees own
            if st.session_state.role != "admin":
                df = df[df['User'] == st.session_state.user]
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No history found.")

    # --- FEEDBACK ---
    elif menu == "Feedback":
        st.title("💬 Feedback")
        with st.form("feedback_form"):
            rating = st.slider("Rate Us", 1, 5, 5)
            msg = st.text_area("Your Message")
            if st.form_submit_button("SEND FEEDBACK"):
                data = {
                    "username": st.session_state.user,
                    "rating": rating,
                    "message": msg,
                    "timestamp": str(datetime.now())
                }
                db.child("feedback").push(data)
                st.success("Feedback Sent!")
    
    # --- PROFILE ---
    elif menu == "Profile":
        st.title("👤 My Profile")
        
        # Get User Info
        users = db.child("users").get().val()
        my_info = {}
        target_uid = ""
        
        for uid, u in users.items():
            if u.get("username") == st.session_state.user:
                my_info = u
                target_uid = uid
                break
        
        if my_info:
            with st.form("profile_edit"):
                new_email = st.text_input("Email", my_info.get("email", ""))
                new_plate = st.text_input("Vehicle Plate", my_info.get("car_plate", ""))
                
                if st.form_submit_button("UPDATE PROFILE"):
                    db.child("users").child(target_uid).update({
                        "email": new_email,
                        "car_plate": new_plate
                    })
                    st.success("Profile Updated!")
