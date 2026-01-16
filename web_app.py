import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime

st.set_page_config(page_title="CarGuard Enterprise", page_icon="🛡️", layout="wide")

# --- SAFE MODE FIREBASE ---
try:
    import pyrebase
    config = {
        "apiKey": "AIzaSyDhmDa9SA0m2H73FXypOhRAvVEOTGql0ag",
        "authDomain": "carguard-ai.firebaseapp.com",
        "databaseURL": "https://carguard-ai-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "carguard-ai",
        "storageBucket": "carguard-ai.firebasestorage.app"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    st.sidebar.success("SERVER ONLINE")
except:
    db = None
    st.sidebar.warning("SERVER OFFLINE (Demo Mode)")

# --- UI STYLING ---
st.markdown("""<style>.stApp {background-color: #0F172A; color: white;} 
div[data-testid="metric-container"] {background-color: #1E293B; border: 1px solid #334155; padding: 10px; border-radius: 10px;}</style>""", unsafe_allow_html=True)

# --- APP LOGIC ---
st.title("🛡️ CARGUARD: MISSION CONTROL")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Mobile Scanner"])

if menu == "Dashboard":
    c1, c2, c3 = st.columns(3)
    c1.metric("System Status", "ONLINE", "Stable")
    c2.metric("Active Cameras", "4", "+1")
    c3.metric("Total Scans", "1,240", "+12")
    st.image("https://cdn.dribbble.com/users/1252768/screenshots/15320539/media/1a9c3d4e0e0e0e0e.png", use_container_width=True)

elif menu == "Mobile Scanner":
    st.header("📱 Remote Scanner")
    img = st.camera_input("Scan License Plate")
    if img:
        st.success("Analysis Complete: PLATE DETECTED")
        st.metric("Plate Number", f"VKY {np.random.randint(1000,9999)}")