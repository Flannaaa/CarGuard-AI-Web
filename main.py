# main.py - CarGuard AI (Executive Class UI)
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import re
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import threading
import time
import shutil
import cv2 
import pyrebase 

# --- MATPLOTLIB FOR GRAPHS ---
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print(">> Install matplotlib for graphs: pip install matplotlib")

# -----------------------
# 1. SETUP & CONFIGURATION
# -----------------------
LIVE_RESULTS_FILE = "resources/live_detection_results.txt"
HISTORY_FILE = "resources/history_logs.txt"
os.makedirs("resources", exist_ok=True)

if not os.path.exists(LIVE_RESULTS_FILE):
    with open(LIVE_RESULTS_FILE, "w") as f: f.write("")

TEST_MODE = False
SENDER_EMAIL = "manziechongggg@gmail.com" 
APP_PASSWORD = "swsezpfnbwrtvgmc"

# FIREBASE CONFIG
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
    print(">> Firebase Connected Successfully")
except Exception as e:
    print(f">> Firebase Connection Failed: {e}")
    db = None

# LOCAL DIRECTORIES
DETECTION_RESULTS_DIR = "detection_results"
os.makedirs(DETECTION_RESULTS_DIR, exist_ok=True)

# -----------------------
# 2. DETECTION MODELS
# -----------------------
try:
    from models.yolo.yoloPhoto import yoloDetectPhoto
    from models.yolo.yoloRealTimeDetection import yoloRealTimeModelDetect
    from models.sdd_MobileNetV2_FpnLite.sddMobileNetV2Photo import ssdDetectPhoto
    from models.sdd_MobileNetV2_FpnLite.ssdMobileNetV2RealTimeDetection import ssdRealTimeModelDetect
    from models.faster_rcnn.fasterRcnnPhoto import fasterRcnnDetectPhoto
    from models.faster_rcnn.fasterRcnnCamera import fasterRcnnRealTimeDetect

except ImportError as e:
    print(">> Detection models missing, using SIMULATION mode.")

    def yoloDetectPhoto(p): return ["DEMO-YOLO", p]
    def ssdDetectPhoto(p): return ["DEMO-SSD", p]
    def fasterRcnnDetectPhoto(p): return ["DEMO-RCNN", p]

    def simulate_detection_loop(model_name):
        print(f">> {model_name} Simulation Started")
        while True:
            time.sleep(2.5) 
            fake_plate = f"AKD{random.randint(1000, 9999)}"
            try:
                with open(LIVE_RESULTS_FILE, "a") as f:
                    f.write(f"{fake_plate}\n")
                print(f">> Simulated Detect: {fake_plate}")
            except: pass

    def yoloRealTimeModelDetect(): simulate_detection_loop("YOLO")
    def ssdRealTimeModelDetect(): simulate_detection_loop("SSD")
    def fasterRcnnRealTimeDetect(): simulate_detection_loop("R-CNN")

# -----------------------
# 3. HIGH-CLASS THEME
# -----------------------
class Theme:
    # "Midnight Executive" Palette
    BG_MAIN = "#050505"       # Void Black
    BG_SIDEBAR = "#0A0A0A"    # Deep Onyx
    
    # Cards
    CARD_BG = "#121212"       # Surface
    CARD_BORDER = "#2A2A2A"   # Subtle Border
    
    # Accents (The "Fancy" Part)
    PRIMARY = "#00F0FF"       # Neon Cyan
    SECONDARY = "#7000FF"     # Electric Purple
    SUCCESS = "#00FF9D"       # Cyber Green
    DANGER = "#FF003C"        # Cyber Red
    
    # Typography
    TEXT_WHITE = "#FFFFFF"
    TEXT_GREY = "#666666"
    
    FONT_FAMILY = "Segoe UI" # Clean, modern Windows font
    
    # Shapes
    CORNER = 6 # Smaller radius = more professional/tech look

# -----------------------
# 4. BACKEND LOGIC
# -----------------------
class AuthSystem:
    current_user = None
    current_role = None

    @staticmethod
    def validate_password(password, confirm):
        if not password: return False, "Password cannot be empty."
        if password != confirm: return False, "Passwords do not match."
        if len(password) < 8: return False, "Password must be at least 8 characters."
        if not re.search(r"\d", password): return False, "Password must contain a number."
        if not re.search(r"[A-Z]", password): return False, "Password must contain an uppercase letter."
        return True, "Valid"

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email): return False, "Invalid email format."
        return True, "Valid"

    @staticmethod
    def validate_username(username):
        if len(username) < 3: return False, "Username too short (min 3 chars)."
        if not re.match(r'^[a-zA-Z0-9_]+$', username): return False, "Username alphanumeric only."
        return True, "Valid"

    @staticmethod
    def validate_plate(plate):
        if not plate: return False, "Plate empty."
        if not re.match(r'^[A-Z0-9]+$', plate.upper()): return False, "Alphanumeric only."
        return True, "Valid"

    @staticmethod
    def send_verification_email(email):
        otp = str(random.randint(100000, 999999))
        if TEST_MODE:
            print(f"[DEBUG] OTP: {otp}")
            return otp, "OTP printed to console"
        try:
            msg = MIMEText(f"Your CarGuard Verification Code is: {otp}")
            msg['Subject'] = "CarGuard AI - Verification Code"
            msg['From'] = f"CarGuard AI <{SENDER_EMAIL}>"
            msg['To'] = email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)
            return otp, "Code sent to email!"
        except Exception as e:
            print(e)
            return None, "Failed to send email."

    @staticmethod
    def register(username, password, role, email, plate="", color="", model=""):
        if not db: return False, "Database Offline"
        try:
            users = db.child("users").get().val()
            if users:
                for uid, info in users.items():
                    if info.get("username") == username: return False, "Username exists."
                    if info.get("email") == email: return False, "Email exists."
            
            data = {
                "username": username, "password": password, "role": role, "email": email,
                "car_plate": plate, "car_color": color, "car_model": model,
                "created_at": str(datetime.now())
            }
            db.child("users").push(data)
            return True, "Registration Successful!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def login(username, password):
        if not db: return False, "Database Offline"
        try:
            all_users = db.child("users").get().val()
            if not all_users: return False, "No users in database."
            for uid, user_data in all_users.items():
                if str(user_data.get("username")) == str(username) and str(user_data.get("password")) == str(password):
                    AuthSystem.current_user = username
                    AuthSystem.current_role = user_data.get("role", "user")
                    return True, "Success"
            return False, "Invalid Credentials"
        except Exception as e:
            return False, f"Connection Error: {e}"
            
    @staticmethod
    def get_info(username, role):
        if not db: return {}
        all_users = db.child("users").get().val()
        if all_users:
            for uid, u in all_users.items():
                if u.get("username") == username: return u
        return {}

    @staticmethod
    def update_profile(username, role, data):
        if not db: return False, "Database Offline"
        try:
            all_users = db.child("users").get().val()
            target_uid = None
            if all_users:
                for uid, info in all_users.items():
                    if info.get("username") == username:
                        target_uid = uid
                        break
            if target_uid:
                db.child("users").child(target_uid).update(data)
                return True, "Profile Updated Successfully!"
            else:
                return False, "User record not found."
        except Exception as e:
            return False, f"Update Failed: {e}"

class CloudLogger:
    @staticmethod
    def log_detection(username, action, plate, orig_path, det_path):
        if not db: return
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username, "action": action, "plate_number": plate,
            "original_path": orig_path, "detected_path": det_path
        }
        db.child("logs").push(data)

    @staticmethod
    def log_feedback(username, rating, name, email, message):
        if not db: return
        data = {
            "username": username, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "rating": rating, "full_name": name, "email": email, "message": message
        }
        db.child("feedback").push(data)

class LiveDetectionManager:
    def __init__(self):
        self.is_monitoring = False
        self.last_position = 0
        self._timer = None

    def start_monitoring(self, callback):
        if os.path.exists(LIVE_RESULTS_FILE):
            self.last_position = os.path.getsize(LIVE_RESULTS_FILE)
        self.is_monitoring = True
        self._poll(callback)

    def stop_monitoring(self):
        self.is_monitoring = False
        if self._timer:
            try: self._timer.cancel()
            except: pass

    def _poll(self, callback):
        if not self.is_monitoring: return
        try:
            if os.path.exists(LIVE_RESULTS_FILE):
                curr = os.path.getsize(LIVE_RESULTS_FILE)
                if curr > self.last_position:
                    with open(LIVE_RESULTS_FILE, "r", encoding="utf-8") as f:
                        f.seek(self.last_position)
                        content = f.read()
                        self.last_position = f.tell()
                        if content.strip():
                            matches = re.findall(r'\b[A-Z0-9]{5,8}\b', content)
                            if matches:
                                try: callback(matches)
                                except: pass
            self._timer = threading.Timer(0.5, lambda: self._poll(callback))
            self._timer.daemon = True
            self._timer.start()
        except:
            self._timer = threading.Timer(1.0, lambda: self._poll(callback))
            self._timer.daemon = True
            self._timer.start()

# -----------------------
# 5. UI WIDGETS (EXECUTIVE STYLE)
# -----------------------
class ExecutiveCard(ctk.CTkFrame):
    def __init__(self, master, width=None, height=None, border_color=Theme.CARD_BORDER, **kwargs):
        super().__init__(master, 
                         fg_color=Theme.CARD_BG, 
                         corner_radius=Theme.CORNER, 
                         border_width=1, 
                         border_color=border_color, 
                         **kwargs)
        if width: self.configure(width=width)
        if height: self.configure(height=height)

class MetricWidget(ExecutiveCard):
    """A Fancy Card for displaying a single statistic"""
    def __init__(self, master, title, value, icon, color=Theme.PRIMARY):
        super().__init__(master, height=120, border_color=color)
        self.pack_propagate(False) # Force size
        
        # Icon/Symbol
        ctk.CTkLabel(self, text=icon, font=("Arial", 24), text_color=color).pack(anchor="ne", padx=15, pady=(15,0))
        
        # Data
        ctk.CTkLabel(self, text=value, font=(Theme.FONT_FAMILY, 32, "bold"), text_color="white").pack(anchor="w", padx=15, pady=(0, 5))
        ctk.CTkLabel(self, text=title.upper(), font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_GREY).pack(anchor="w", padx=15)

class GradientButton(ctk.CTkButton):
    def __init__(self, master, text, command, type="primary", **kwargs):
        color = Theme.PRIMARY if type == "primary" else Theme.CARD_BG
        hover = Theme.SECONDARY if type == "primary" else "#222222"
        text_col = "black" if type == "primary" else "white"
        
        super().__init__(master, text=text, command=command, 
                         fg_color=color, hover_color=hover, 
                         text_color=text_col,
                         corner_radius=Theme.CORNER, 
                         font=(Theme.FONT_FAMILY, 13, "bold"), 
                         height=45, 
                         **kwargs)

class SecureEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder_text="", **kwargs):
        super().__init__(master, height=50, corner_radius=Theme.CORNER, 
                         fg_color="#000000", 
                         border_width=1, border_color=Theme.CARD_BORDER, 
                         text_color="white", font=(Theme.FONT_FAMILY, 14),
                         placeholder_text=placeholder_text,
                         placeholder_text_color=Theme.TEXT_GREY, **kwargs)

# -----------------------
# 6. MAIN APPLICATION
# -----------------------
class CarGuardApp:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        
        self.app = ctk.CTk()
        self.app.title("CarGuard AI | Enterprise Verification System")
        self.app.geometry("1440x900")
        self.app.configure(fg_color=Theme.BG_MAIN)
        
        self.cap = None 
        self.live_detection_manager = LiveDetectionManager()
        self.live_detection_active = False
        self.photo_refs = []
        
        self.show_login()

    def clear_screen(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        for widget in self.app.winfo_children():
            widget.destroy()

    # --- LOGIN (SECURE PORTAL LOOK) ---
    def show_login(self):
        self.clear_screen()
        
        # Background decoration (glow)
        bg_glow = ctk.CTkFrame(self.app, width=500, height=600, corner_radius=50, fg_color=Theme.SECONDARY)
        bg_glow.place(relx=0.5, rely=0.5, anchor="center")
        # Blur hack: overlay semi-transparent dark box
        
        login_card = ExecutiveCard(self.app, width=450, height=550, border_color=Theme.PRIMARY)
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        login_card.pack_propagate(False)
        
        # Header
        ctk.CTkLabel(login_card, text="SYSTEM LOGIN", font=(Theme.FONT_FAMILY, 24, "bold"), text_color="white").pack(pady=(60, 5))
        ctk.CTkLabel(login_card, text="AUTHORIZED PERSONNEL ONLY", font=(Theme.FONT_FAMILY, 10), text_color=Theme.PRIMARY).pack(pady=(0, 40))
        
        self.user_entry = SecureEntry(login_card, placeholder_text="OPERATOR ID")
        self.user_entry.pack(fill="x", padx=40, pady=10)
        
        self.pass_entry = SecureEntry(login_card, placeholder_text="ACCESS KEY", show="•")
        self.pass_entry.pack(fill="x", padx=40, pady=10)
        
        GradientButton(login_card, text="ESTABLISH CONNECTION >", command=self.handle_login).pack(fill="x", padx=40, pady=(40, 10))
        
        ctk.CTkButton(login_card, text="Request New Clearance", fg_color="transparent", 
                      text_color=Theme.TEXT_GREY, hover_color=Theme.CARD_BG, 
                      command=self.show_register).pack()

    def handle_login(self):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        if not u or not p: messagebox.showerror("Error", "Input Required"); return
        success, msg = AuthSystem.login(u, p)
        if success: self.setup_main_layout()
        else: messagebox.showerror("Security Alert", msg)

    # --- REGISTER ---
    def show_register(self):
        top = ctk.CTkToplevel(self.app)
        top.geometry("500x750")
        top.title("Registration")
        top.configure(fg_color=Theme.BG_MAIN)
        top.attributes("-topmost", True)
        
        card = ExecutiveCard(top)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(card, text="NEW OPERATOR REGISTRATION", font=(Theme.FONT_FAMILY, 18, "bold"), text_color=Theme.PRIMARY).pack(pady=20)
        
        role_var = ctk.StringVar(value="User")
        
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=30)

        u = SecureEntry(form, placeholder_text="Username"); u.pack(pady=5, fill="x")
        e = SecureEntry(form, placeholder_text="Email Address"); e.pack(pady=5, fill="x")
        p1 = SecureEntry(form, placeholder_text="Password", show="•"); p1.pack(pady=5, fill="x")
        p2 = SecureEntry(form, placeholder_text="Confirm Password", show="•"); p2.pack(pady=5, fill="x")
        
        def toggle(val):
            if val == "User": car_frame.pack(pady=10, fill="x")
            else: car_frame.pack_forget()
            
        ctk.CTkSegmentedButton(form, values=["User", "Admin"], variable=role_var, command=toggle, 
                               fg_color="black", selected_color=Theme.PRIMARY, text_color="white", selected_hover_color=Theme.SECONDARY).pack(pady=15)
        
        car_frame = ctk.CTkFrame(form, fg_color="transparent")
        pl = SecureEntry(car_frame, placeholder_text="Vehicle Plate ID"); pl.pack(pady=5, fill="x")
        co = SecureEntry(car_frame, placeholder_text="Vehicle Color"); co.pack(pady=5, fill="x")
        mo = SecureEntry(car_frame, placeholder_text="Vehicle Model"); mo.pack(pady=5, fill="x")
        car_frame.pack(pady=10, fill="x") 

        def process():
            otp, msg = AuthSystem.send_verification_email(e.get())
            if not otp: messagebox.showerror("Error", msg, parent=top); return
            code = simpledialog.askstring("2FA Verification", f"Enter OTP sent to {e.get()}", parent=top)
            if code == otp:
                s, m = AuthSystem.register(u.get(), p1.get(), role_var.get().lower(), e.get(), pl.get(), co.get(), mo.get())
                if s: top.destroy(); messagebox.showinfo("Success", "Clearance Granted")
                else: messagebox.showerror("Error", m)
            else: messagebox.showerror("Error", "Invalid OTP")

        GradientButton(card, text="SUBMIT APPLICATION", command=process).pack(fill="x", padx=30, pady=30)

    # --- MAIN LAYOUT ---
    def setup_main_layout(self):
        self.clear_screen()
        
        # 1. Sidebar (Full Height, Darker)
        self.sidebar = ctk.CTkFrame(self.app, width=280, fg_color=Theme.BG_SIDEBAR, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Logo Area
        logo_box = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=100)
        logo_box.pack(fill="x", pady=30)
        ctk.CTkLabel(logo_box, text="CARGUARD", font=(Theme.FONT_FAMILY, 30, "bold"), text_color="white").pack()
        ctk.CTkLabel(logo_box, text="INTELLIGENT SYSTEM", font=(Theme.FONT_FAMILY, 10), text_color=Theme.PRIMARY, spacing=5).pack()
        
        # Navigation
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=15, pady=20)
        
        self.nav_btn(nav_container, "OVERVIEW", "🏠", self.show_dashboard_page, active=True)
        self.nav_btn(nav_container, "LIVE SURVEILLANCE", "📹", lambda: self.launch_tool("live"))
        self.nav_btn(nav_container, "IMAGE ANALYSIS", "🖼️", lambda: self.launch_tool("photo"))
        self.nav_btn(nav_container, "DATA LOGS", "📊", self.show_logs)
        self.nav_btn(nav_container, "OPERATOR PROFILE", "👤", self.show_profile)
        self.nav_btn(nav_container, "SYSTEM FEEDBACK", "💬", self.show_feedback)
        
        # Bottom User Profile
        u_box = ExecutiveCard(self.sidebar, height=80, border_color="#333")
        u_box.pack(side="bottom", fill="x", padx=15, pady=20)
        ctk.CTkLabel(u_box, text=AuthSystem.current_user, font=(Theme.FONT_FAMILY, 14, "bold")).place(x=15, y=15)
        ctk.CTkLabel(u_box, text=f"LEVEL: {AuthSystem.current_role.upper()}", font=(Theme.FONT_FAMILY, 10), text_color=Theme.SUCCESS).place(x=15, y=40)
        
        ctk.CTkButton(u_box, text="⏻", width=30, height=30, fg_color=Theme.CARD_BG, hover_color=Theme.DANGER, command=self.show_login).place(x=200, y=25)

        # 2. Main Content
        self.content = ctk.CTkFrame(self.app, fg_color=Theme.BG_MAIN, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)
        
        self.show_dashboard_page()

    def nav_btn(self, parent, text, icon, cmd, active=False):
        color = Theme.CARD_BG if active else "transparent"
        btn = ctk.CTkButton(parent, text=f"  {icon}   {text}", anchor="w", 
                            fg_color=color, hover_color="#222", 
                            height=50, font=(Theme.FONT_FAMILY, 12, "bold"), 
                            corner_radius=Theme.CORNER, command=cmd)
        btn.pack(fill="x", pady=5)

    # --- DASHBOARD PAGE ---
    def show_dashboard_page(self):
        for w in self.content.winfo_children(): w.destroy()
        
        # Top Bar
        top_bar = ctk.CTkFrame(self.content, fg_color="transparent")
        top_bar.pack(fill="x", padx=40, pady=40)
        ctk.CTkLabel(top_bar, text="Mission Control", font=(Theme.FONT_FAMILY, 32, "bold")).pack(side="left")
        ctk.CTkLabel(top_bar, text=datetime.now().strftime("%H:%M  |  %d %B %Y"), font=(Theme.FONT_FAMILY, 14), text_color=Theme.TEXT_GREY).pack(side="right")

        # Metrics Grid
        grid = ctk.CTkFrame(self.content, fg_color="transparent")
        grid.pack(fill="x", padx=40, pady=10)
        grid.columnconfigure((0,1,2,3), weight=1, uniform="x")
        
        MetricWidget(grid, "System Status", "ONLINE", "🟢", Theme.SUCCESS).grid(row=0, column=0, padx=5, sticky="ew")
        MetricWidget(grid, "Detections", "842", "👁️", Theme.PRIMARY).grid(row=0, column=1, padx=5, sticky="ew")
        MetricWidget(grid, "Security Level", "HIGH", "🛡️", Theme.SECONDARY).grid(row=0, column=2, padx=5, sticky="ew")
        MetricWidget(grid, "Database Latency", "12ms", "⚡", Theme.DANGER).grid(row=0, column=3, padx=5, sticky="ew")

        # Main Workspace (Graph + Shortcuts)
        work_area = ctk.CTkFrame(self.content, fg_color="transparent")
        work_area.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Left: Graph
        graph_card = ExecutiveCard(work_area)
        graph_card.pack(side="left", fill="both", expand=True, padx=(0, 20))
        ctk.CTkLabel(graph_card, text="Weekly Activity", font=(Theme.FONT_FAMILY, 16, "bold"), text_color=Theme.TEXT_GREY).pack(anchor="w", padx=20, pady=20)
        
        if HAS_MATPLOTLIB: self.embed_graph(graph_card)
        else: ctk.CTkLabel(graph_card, text="[Chart Module Missing]", text_color="grey").pack(expand=True)

        # Right: Quick Access
        actions = ExecutiveCard(work_area, width=300)
        actions.pack(side="right", fill="y")
        actions.pack_propagate(False)
        
        ctk.CTkLabel(actions, text="QUICK DEPLOY", font=(Theme.FONT_FAMILY, 14, "bold"), text_color=Theme.PRIMARY).pack(anchor="w", padx=20, pady=20)
        
        GradientButton(actions, text="LAUNCH CAMERA", command=lambda: self.launch_tool("live")).pack(fill="x", padx=20, pady=10)
        GradientButton(actions, text="ANALYZE FILE", type="secondary", command=lambda: self.launch_tool("photo")).pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(actions, text="NOTIFICATIONS", font=(Theme.FONT_FAMILY, 12, "bold"), text_color=Theme.TEXT_GREY).pack(anchor="w", padx=20, pady=(30, 10))
        ctk.CTkLabel(actions, text="• System update available", font=(Theme.FONT_FAMILY, 11), text_color="white").pack(anchor="w", padx=20, pady=2)
        ctk.CTkLabel(actions, text="• Database backup complete", font=(Theme.FONT_FAMILY, 11), text_color="white").pack(anchor="w", padx=20, pady=2)

    def embed_graph(self, parent):
        # Professional Dark Mode Graph
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor(Theme.CARD_BG)
        ax.set_facecolor(Theme.CARD_BG)
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        data = [random.randint(10, 50) for _ in range(7)]
        
        # Gradient fill effect simulation
        ax.fill_between(days, data, color=Theme.PRIMARY, alpha=0.3)
        ax.plot(days, data, color=Theme.PRIMARY, marker='o', linewidth=2)
        
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('#333')
        ax.spines['left'].set_color('#333') 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # --- TOOLS ---
    def launch_tool(self, tool_type):
        self.live_detection_active = False
        if self.cap: self.cap.release()
        for w in self.content.winfo_children(): w.destroy()
        
        title = "LIVE SURVEILLANCE" if tool_type == "live" else "IMAGE FORENSICS"
        
        h = ctk.CTkFrame(self.content, fg_color="transparent")
        h.pack(fill="x", padx=40, pady=30)
        ctk.CTkLabel(h, text=title, font=(Theme.FONT_FAMILY, 28, "bold")).pack(side="left")
        
        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        if tool_type == "live": self.tool_live_ui(main)
        else: self.tool_photo_ui(main)

    def tool_live_ui(self, parent):
        self.live_model_var = ctk.StringVar(value="YOLO")
        self.live_seen = set()
        
        parent.columnconfigure(0, weight=3)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Camera Feed with "Cyber" Border
        cam_container = ExecutiveCard(parent, border_color=Theme.SUCCESS)
        cam_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        self.cam_frame = ctk.CTkLabel(cam_container, text="WAITING FOR SIGNAL...", font=("Consolas", 16), text_color=Theme.SUCCESS)
        self.cam_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Controls
        ctrl_panel = ExecutiveCard(parent)
        ctrl_panel.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(ctrl_panel, text="DETECTION LOG", font=(Theme.FONT_FAMILY, 14, "bold"), text_color=Theme.PRIMARY).pack(pady=15)
        
        self.live_scroll = ctk.CTkScrollableFrame(ctrl_panel, fg_color="transparent")
        self.live_scroll.pack(fill="both", expand=True, padx=10)
        
        action_area = ctk.CTkFrame(ctrl_panel, fg_color="transparent")
        action_area.pack(fill="x", padx=15, pady=15)
        
        GradientButton(action_area, text="INITIATE FEED", command=lambda: self.live_toggle(True)).pack(fill="x", pady=5)
        GradientButton(action_area, text="TERMINATE", type="secondary", command=lambda: self.live_toggle(False)).pack(fill="x", pady=5)

    def live_toggle(self, start):
        if start:
            if self.live_detection_active: return
            self.live_detection_active = True
            self.live_detection_manager.start_monitoring(self.update_live_list)
            self.start_camera_preview()
            # Start Thread
            model = self.live_model_var.get()
            if model == "YOLO": threading.Thread(target=yoloRealTimeModelDetect, daemon=True).start()
            elif model == "SSD": threading.Thread(target=ssdRealTimeModelDetect, daemon=True).start()
            else: threading.Thread(target=fasterRcnnRealTimeDetect, daemon=True).start()
        else:
            self.live_detection_active = False
            self.live_detection_manager.stop_monitoring()
            if self.cap: self.cap.release()
            self.cam_frame.configure(image=None, text="SIGNAL LOST")

    def start_camera_preview(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        def update():
            try:
                if not self.cam_frame.winfo_exists(): self.cap.release(); return
            except: self.cap.release(); return

            if self.live_detection_active and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Overlay UI on Camera
                    cv2.rectangle(frame, (20, 20), (620, 460), (0, 255, 0), 2)
                    cv2.putText(frame, "LIVE SCANNING", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    img = Image.fromarray(frame)
                    tk_img = ctk.CTkImage(img, size=(640, 480))
                    try:
                        self.cam_frame.configure(image=tk_img, text="")
                        self.cam_frame.image = tk_img
                        self.app.after(10, update) 
                    except: self.cap.release()
                else: self.cap.release()
            else: self.cap.release()
        update()

    def update_live_list(self, plates):
        if not self.live_detection_active: return
        self.app.after(0, lambda: self._add_live_card(plates))

    def _add_live_card(self, plates):
        for p in plates:
            if p in self.live_seen: continue
            self.live_seen.add(p)
            c = ctk.CTkFrame(self.live_scroll, fg_color="#222", corner_radius=5)
            c.pack(fill="x", pady=2)
            ctk.CTkLabel(c, text=p, font=("Consolas", 16, "bold"), text_color=Theme.SUCCESS).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(c, text=datetime.now().strftime("%H:%M:%S"), font=("Arial", 10)).pack(side="right", padx=10)
            
            with open(HISTORY_FILE, "a") as f: f.write(f"{datetime.now()} - {p}\n")
            CloudLogger.log_detection(AuthSystem.current_user, "Live", p, "", "")

    def tool_photo_ui(self, parent):
        self.photo_model_var = ctk.StringVar(value="YOLO")
        parent.columnconfigure((0,1), weight=1)
        
        # Source
        l = ExecutiveCard(parent)
        l.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(l, text="SOURCE INPUT", font=(Theme.FONT_FAMILY, 12, "bold"), text_color=Theme.TEXT_GREY).pack(pady=10)
        self.lbl_orig = ctk.CTkLabel(l, text="[ DRAG & DROP ]", text_color="#444")
        self.lbl_orig.pack(expand=True)
        
        # Result
        r = ExecutiveCard(parent)
        r.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(r, text="AI ANALYSIS", font=(Theme.FONT_FAMILY, 12, "bold"), text_color=Theme.TEXT_GREY).pack(pady=10)
        self.lbl_det = ctk.CTkLabel(r, text="[ AWAITING DATA ]", text_color="#444")
        self.lbl_det.pack(expand=True)
        
        # Bottom Bar
        bot = ctk.CTkFrame(parent, fg_color="transparent")
        bot.grid(row=1, column=0, columnspan=2, pady=20)
        
        self.lbl_plate_text = ctk.CTkLabel(bot, text="READY FOR INSPECTION", font=(Theme.FONT_FAMILY, 20), text_color=Theme.PRIMARY)
        self.lbl_plate_text.pack(pady=10)
        GradientButton(bot, text="SELECT EVIDENCE FILE", command=self.run_photo).pack()

    def run_photo(self):
        path = filedialog.askopenfilename(parent=self.app)
        if not path: return
        try:
            img = Image.open(path); img.thumbnail((400, 300)); tk_img = ctk.CTkImage(img, size=img.size)
            self.lbl_orig.configure(image=tk_img, text=""); self.photo_refs.append(tk_img)
            model = self.photo_model_var.get()
            if model == "YOLO": plate, det_path = yoloDetectPhoto(path)
            elif model == "SSD": plate, det_path = ssdDetectPhoto(path)
            else: plate, det_path = fasterRcnnDetectPhoto(path)
            
            if det_path and os.path.exists(det_path):
                img2 = Image.open(det_path); img2.thumbnail((400, 300)); tk_img2 = ctk.CTkImage(img2, size=img2.size)
                self.lbl_det.configure(image=tk_img2, text=""); self.photo_refs.append(tk_img2)
            self.lbl_plate_text.configure(text=f"IDENTIFIED: {plate}")
            CloudLogger.log_detection(AuthSystem.current_user, f"Photo-{model}", plate, path, det_path)
        except Exception as e: messagebox.showerror("Error", str(e))

    # --- LOGS & PROFILE (Placeholder Styles) ---
    def show_logs(self): self.generic_list_view("DATA LOGS", "logs")
    def show_profile(self): self.edit_profile_modal() 
    def show_feedback(self): messagebox.showinfo("Info", "Feedback Module Active")

    def generic_list_view(self, title, db_node):
        for w in self.content.winfo_children(): w.destroy()
        ctk.CTkLabel(self.content, text=title, font=(Theme.FONT_FAMILY, 28, "bold")).pack(anchor="w", padx=40, pady=30)
        
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40)
        
        if db:
            try:
                data = db.child(db_node).get().val()
                if data:
                    for k, v in list(data.items())[-15:]: 
                        c = ExecutiveCard(scroll, height=60, border_color="#333")
                        c.pack(fill="x", pady=5)
                        ctk.CTkLabel(c, text=v.get('timestamp',''), width=180, text_color=Theme.TEXT_GREY).pack(side="left", padx=15)
                        ctk.CTkLabel(c, text=v.get('plate_number','Unknown').upper(), font=("Consolas", 14, "bold"), text_color="white").pack(side="left")
                        ctk.CTkLabel(c, text="ARCHIVED", font=("Arial", 10), text_color=Theme.SUCCESS).pack(side="right", padx=15)
            except: pass

    def edit_profile_modal(self):
        top = ctk.CTkToplevel(self.app)
        top.geometry("400x500")
        top.configure(fg_color=Theme.BG_MAIN)
        ctk.CTkLabel(top, text="EDIT PROFILE", font=(Theme.FONT_FAMILY, 18, "bold")).pack(pady=20)
        # Reuse SecureEntry and GradientButton here as needed

if __name__ == "__main__":
    app = CarGuardApp()
    app.app.mainloop()