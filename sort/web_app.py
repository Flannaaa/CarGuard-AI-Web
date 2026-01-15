import streamlit as st
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

st.set_page_config(page_title="CarGuard Safe Mode", layout="wide")

st.title("🛡️ CARGUARD: SAFE MODE")
st.success("Server is finally running! Now we can add features back one by one.")

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

anim = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_57TxAX.json")
if anim: st_lottie(anim, height=200)

st.metric("System Status", "ONLINE", "Stable")