import streamlit as st
import cv2
import numpy as np
import os
from ultralytics import YOLO
from PIL import Image
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="CarGuard Ultimate", page_icon="🛡️", layout="wide")

# CSS to match your Dark CustomTkinter Theme
st.markdown("""
<style>
    .stApp { background-color: #0B0E14; color: white; }
    [data-testid="stSidebar"] { background-color: #181C29; border-right: 1px solid #2A2F45; }
    div.stButton > button { 
        background-color: #9D84FE; color: white; border-radius: 20px; border: none; font-weight: bold;
    }
    div[data-testid="metric-container"] { 
        background-color: #181C29; border: 1px solid #2A2F45; border-radius: 15px; padding: 20px; 
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INTERNAL YOLO LOGIC (The "Brain")
# ---------------------------------------------------------
def run_yolo_detection(image_path):
    """
    This function forces the exact same logic as your main.app
    It loads best.pt from the current folder.
    """
    # Force look for best.pt in the current directory
    model_path = os.path.join(os.getcwd(), "best.pt")

    if not os.path.exists(model_path):
        return ["ERR: 'best.pt' NOT FOUND", image_path]

    try:
        # Load the model
        model = YOLO(model_path)
        
        # Run Detection (conf=0.25 is standard)
        results = model(image_path, conf=0.25)
        
        # Draw the boxes
        result_plot = results[0].plot()
        
        # Save result to disk so Streamlit can show it
        save_path = image_path.replace(".jpg", "_result.jpg")
        cv2.imwrite(save_path, result_plot)
        
        # Get the text (License Plate Number)
        plate_text = "No Plate Found"
        if len(results[0].boxes) > 0:
            # If your model has classes, get the first one
            cls_id = int(results[0].boxes.cls[0])
            conf = results[0].boxes.conf[0]
            # Try to get the specific class name if available
            if model.names:
                plate_text = f"{model.names[cls_id]} ({conf:.2f})"
            else:
                plate_text = f"Detected ({conf:.2f})"
                
        return [plate_text, save_path]

    except Exception as e:
        return [f"ERR: CRASH {e}", image_path]

# ---------------------------------------------------------
# 3. APP INTERFACE
# ---------------------------------------------------------
if 'user' not in st.session_state: st.session_state.user = "Commander"

with st.sidebar:
    st.title("🛡️ CarGuard")
    st.caption("WEB LINK MODE")
    st.markdown("---")
    menu = st.radio("MENU", ["Dashboard", "Live Scanner"])
    st.markdown("---")

# === DASHBOARD ===
if menu == "Dashboard":
    st.title("📊 Mission Control")
    c1, c2 = st.columns(2)
    
    # Check Model Status
    if os.path.exists("best.pt"):
        c1.metric("Neural Engine", "ONLINE")
    else:
        c1.metric("Neural Engine", "OFFLINE (Missing best.pt)")
        st.error("⚠️ CRITICAL: Please put 'best.pt' in the same folder as this script!")

    c2.metric("System Mode", "Web-Tunneled")

# === SCANNER (THE FIX) ===
elif menu == "Live Scanner":
    st.title("📹 Field Scanner")
    
    # 1. GET IMAGE FROM BROWSER
    img_buffer = st.camera_input("Activate Optical Sensor")
    
    if img_buffer:
        # 2. THE BRIDGE: Save memory buffer to a REAL file
        # This is the step that makes it work like your desktop app!
        if not os.path.exists("temp"): os.makedirs("temp")
        real_file_path = os.path.join("temp", "temp_scan.jpg")
        
        with open(real_file_path, "wb") as f:
            f.write(img_buffer.getbuffer())
        
        # 3. RUN DETECTION on that real file
        with st.spinner("Analyzing..."):
            result = run_yolo_detection(real_file_path)
            
            plate_text = result[0]
            result_image = result[1]
            
            # 4. SHOW RESULTS
            c1, c2 = st.columns(2)
            if "ERR" in plate_text:
                c1.error(plate_text)
            else:
                c1.success(f"✅ DETECTED: {plate_text}")
                
            if os.path.exists(result_image):
                c2.image(result_image, caption="AI Analysis Result")
