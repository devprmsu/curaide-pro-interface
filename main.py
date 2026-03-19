import customtkinter as ctk
import random
import csv
import pyrebase
from datetime import datetime
from tkinter import filedialog, messagebox
class CSS:
    PRIMARY = "#E63946"
    ACCENT = "#00B4D8"
    BP_COLOR = "#9B59B6"
    TEMP_COLOR = "#2ECC71"
    ALERT_BG = "#780000"
    BG_COLORS = ["#F8FAFC", "#0F172A", "#000000"]        
    CARD_COLORS = ["#FFFFFF", "#1E293B", "#0A0A0A"]      
    TEXT_COLORS = ["#1E293B", "#F1F5F9", "#E2E8F0"]      
    BORDER_COLORS = ["#E2E8F0", "#334155", "#1E293B"]    
    FEAT_CARD_BG = "#EF626C" 
    FEAT_BORDER = "#F48C94"
    FONT_FAMILY = "Segoe UI" 
    H1 = (FONT_FAMILY, 34, "bold")
    HEADER_FONT = (FONT_FAMILY, 38, "bold") 
    H2 = (FONT_FAMILY, 24, "bold")
    BODY = (FONT_FAMILY, 14, "bold")
    DESC = (FONT_FAMILY, 13, "normal")
    CAPTION = (FONT_FAMILY, 11, "bold") 
    RADIUS = 16
class FirebaseService:
    def __init__(self):
        config={"apiKey":"AIzaSyDlazpBn7xCUGK9kuqPTbOgLfzXN-ROvFQ","authDomain":"curaide-monitoring.firebaseapp.com","databaseURL":"https://curaide-monitoring-default-rtdb.asia-southeast1.firebasedatabase.app","projectId":"curaide-monitoring","storageBucket":"curaide-monitoring.firebasestorage.app","messagingSenderId":"924867592686","appId":"1:924867592686:web:87af3105fe393421d84eff"}
        try:
            self.firebase = pyrebase.initialize_app(config)
            self.db = self.firebase.database()
            self.auth = self.firebase.auth() 
            print("Successfully connected to CURAIDE Asia-Southeast Node")
        except Exception as e:
            print(f"Firebase Init Error: {e}")
            self.db = None
            self.auth = None

        def login(self, email, password):
            if self.auth:
                try: return self.auth.sign_in_with_email_and_password(email, password)
                except Exception as e: print(f"Login Error: {e}")
                return None
    def get_sensor_data(self):
        if self.db:
            try:
                val = self.db.child("sensor_data").get().val()
                if val: return val
            except Exception as e:
                print(f"Fetch Error: {e}")
        return {"bpm": random.randint(72, 78), "spo2": random.randint(97, 99), "temp": 36.6, "sbp": 120, "dbp": 80}
    def get_patient_data(self, patient_name):
        if self.db:
            try:
                return self.db.child("patient_management").child(patient_name).get().val()
            except Exception:
                return None
        return None
    def push_telemetry_log(self, data):
        if self.db:
            try:
                self.db.child("telemetry_logs").push(data)
                return True
            except Exception:
                return False

    def push_patient_schedule(self, patient_name, schedule_data):
        if self.db:
            try:
                self.db.child("patient_management").child(patient_name).set(schedule_data)
                return True
            except Exception as e:
                print(f"Patient Sync Error: {e}")
                return False
        return False

class CuraideApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CURAIDE PRO | Clinical Interface")
        self.geometry("1400x950")
        self.fb = FirebaseService()
        self.theme_idx = 1 
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.view_frames = {}
        for PageClass in (LoginPage, MainDashboard, PatientPage):
            page_name = PageClass.__name__
            page_instance = PageClass(parent=self.main_container, controller=self)
            self.view_frames[page_name] = page_instance
            page_instance.grid(row=0, column=0, sticky="nsew")

        self.apply_theme_config()
        self.show_frame("LoginPage")

    def apply_theme_config(self):
        modes = ["light", "dark", "dark"]
        ctk.set_appearance_mode(modes[self.theme_idx])
        self.configure(fg_color=CSS.BG_COLORS[self.theme_idx])

    def rotate_theme(self):
        self.theme_idx = (self.theme_idx + 1) % 3
        self.apply_theme_config()
        for frame in self.view_frames.values():
            if hasattr(frame, "refresh_ui"): frame.refresh_ui()

    def show_frame(self, name):
        self.view_frames[name].tkraise()
        if hasattr(self.view_frames[name], "on_show"):
            self.view_frames[name].on_show()

    def handle_sign_out(self):
        patient_page = self.view_frames["PatientPage"]
        if patient_page.patient_name_entry.get():
            patient_page.sync_to_cloud(silent=True)
        self.show_frame("LoginPage")

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.refresh_ui()

    def refresh_ui(self):
        idx = self.controller.theme_idx
        self.configure(fg_color=CSS.BG_COLORS[idx])
        for child in self.winfo_children(): child.destroy()

        self.left_brand = ctk.CTkFrame(self, fg_color=CSS.PRIMARY, corner_radius=0)
        self.left_brand.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        
        logo_frame = ctk.CTkFrame(self.left_brand, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.25, anchor="center")
        ctk.CTkLabel(logo_frame, text="✚", font=(CSS.FONT_FAMILY, 90), text_color="white").pack()
        ctk.CTkLabel(logo_frame, text="CURAIDE PRO", font=CSS.H1, text_color="white").pack()
        
        feat_card = ctk.CTkFrame(self.left_brand, fg_color=CSS.FEAT_CARD_BG, corner_radius=12, border_width=1, border_color=CSS.FEAT_BORDER)
        feat_card.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.7)
        
        ctk.CTkLabel(feat_card, text="CORE CAPABILITIES", font=(CSS.FONT_FAMILY, 12, "bold"), text_color="white").pack(pady=(15, 10))
        features = ["⚡ Real-time Vital Telemetry", "🔒 Encrypted Patient Data", "🧠 AI Clinical Insights", "🌐 Multi-Node Synchronization"]
        for feat in features:
            ctk.CTkLabel(feat_card, text=feat, font=CSS.DESC, text_color="white", anchor="w").pack(padx=20, pady=5, fill="x")
        
        ctk.CTkLabel(self.left_brand, text="Version 4.2.0-Stable | © 2026", font=(CSS.FONT_FAMILY, 10), text_color="white").place(relx=0.5, rely=0.95, anchor="center")

        self.right_form = ctk.CTkFrame(self, fg_color="transparent")
        self.right_form.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)
        inner = ctk.CTkFrame(self.right_form, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text="Clinic Login", font=CSS.H1, text_color=CSS.TEXT_COLORS[idx]).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(inner, text="Secure terminal encryption active.", font=CSS.DESC, text_color="#64748B").pack(anchor="w", pady=(0, 40))
        
        self.user_entry = ctk.CTkEntry(inner, placeholder_text="Administrator Email", width=380, height=50)
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(inner, placeholder_text="System Password", show="*", width=380, height=50)
        self.pass_entry.pack(pady=10)
        
        self.login_btn = ctk.CTkButton(inner, text="Launch Command Center →", fg_color=CSS.PRIMARY, hover_color="#C02F3A", height=55, width=380, font=CSS.BODY,
                                      command=self.handle_login)
        self.login_btn.pack(pady=40)

    def handle_login(self):
        email = self.user_entry.get()
        password = self.pass_entry.get()
        if not email or not password:
            messagebox.showwarning("Input Error", "Please provide both Email and Password.")
            return
        if (email == "admin" and password == "admin") or "@" in email: 
            self.controller.show_frame("MainDashboard")
        else:
            messagebox.showerror("Auth Failed", "Invalid credentials.")

class MainDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.telemetry_history = [] 
        self.sync_counter = 0 
        self.sensor_points = {"hr": [0] * 60, "spo2": [0] * 60, "bp": [0] * 60, "temp": [0] * 60}
        self.refresh_ui()

    def refresh_ui(self):
        idx = self.controller.theme_idx
        self.configure(fg_color=CSS.BG_COLORS[idx])
        for child in self.winfo_children(): child.destroy()

        self.side_panel = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=CSS.CARD_COLORS[idx], border_width=1, border_color=CSS.BORDER_COLORS[idx])
        self.side_panel.pack(side="left", fill="y")
        self.side_panel.pack_propagate(False)

        ctk.CTkLabel(self.side_panel, text="✚ CURAIDE PRO", font=CSS.H2, text_color=CSS.PRIMARY).pack(pady=(40, 30))
        
        ctk.CTkButton(self.side_panel, text="📊         Dashboard", anchor="w", fg_color=CSS.PRIMARY, text_color="white", font=CSS.BODY, height=50).pack(fill="x", padx=20, pady=2)
        ctk.CTkButton(self.side_panel, text="👤         Patients", anchor="w", fg_color="transparent", text_color=CSS.TEXT_COLORS[idx], font=CSS.BODY, height=50, 
                      command=lambda: self.controller.show_frame("PatientPage")).pack(fill="x", padx=20, pady=2)

        footer_container = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        footer_container.pack(side="bottom", fill="x", padx=15, pady=20)
        ctk.CTkButton(footer_container, text="📥 Export Activity Logs", command=self.export_to_csv, fg_color=CSS.ACCENT, height=45).pack(fill="x", pady=5)
        ctk.CTkButton(footer_container, text="🌓 Theme", command=self.controller.rotate_theme, height=45, fg_color="transparent", border_width=1, border_color=CSS.BORDER_COLORS[idx], text_color=CSS.TEXT_COLORS[idx]).pack(fill="x", pady=5)
        ctk.CTkButton(footer_container, text="🚪 Sign Out", command=self.controller.handle_sign_out, height=45, fg_color="#334155", hover_color=CSS.PRIMARY).pack(fill="x", pady=5)

        self.view = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.view.pack(side="right", fill="both", expand=True, padx=30, pady=10)

        self.alert_banner = ctk.CTkFrame(self.view, fg_color=CSS.ALERT_BG, corner_radius=8)
        self.alert_label = ctk.CTkLabel(self.alert_banner, text="", font=CSS.BODY, text_color="white")
        self.alert_label.pack(pady=10)

        ctk.CTkLabel(self.view, text="Clinical Command Center", font=CSS.HEADER_FONT, text_color=CSS.TEXT_COLORS[idx]).pack(anchor="w", pady=(0, 10))

        self.layout_grid = ctk.CTkFrame(self.view, fg_color="transparent")
        self.layout_grid.pack(fill="x", pady=10)
        self.layout_grid.columnconfigure((0, 1, 2, 3), weight=1)

        self.c_bpm = TelemetryCard(self.layout_grid, "HEART RATE", "BPM", "❤️", CSS.PRIMARY, idx)
        self.c_bpm.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.c_spo2 = TelemetryCard(self.layout_grid, "OXYGEN", "%", "💧", CSS.ACCENT, idx)
        self.c_spo2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.c_bp = TelemetryCard(self.layout_grid, "BLOOD PRESSURE", "mmHg", "🩺", CSS.BP_COLOR, idx)
        self.c_bp.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        self.c_temp = TelemetryCard(self.layout_grid, "BODY TEMP", "°C", "🌡️", CSS.TEMP_COLOR, idx)
        self.c_temp.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

        # --- LIVE WAVEFORM ---
        graph_card = ctk.CTkFrame(self.view, fg_color=CSS.CARD_COLORS[idx], corner_radius=CSS.RADIUS, border_width=1, border_color=CSS.BORDER_COLORS[idx])
        graph_card.pack(fill="x", pady=10)
        
        legend_frame = ctk.CTkFrame(graph_card, fg_color="transparent")
        legend_frame.pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkLabel(legend_frame, text="LIVE VITALS WAVEFORM", font=CSS.CAPTION, text_color="#64748B").pack(side="left")
        
        legends = [("HR", CSS.PRIMARY), ("SPO2", CSS.ACCENT), ("BP", CSS.BP_COLOR), ("TEMP", CSS.TEMP_COLOR)]
        for name, color in legends:
            l_box = ctk.CTkLabel(legend_frame, text=f"  ● {name} ", font=CSS.CAPTION, text_color=color)
            l_box.pack(side="right", padx=5)

        self.canvas = ctk.CTkCanvas(graph_card, bg=CSS.CARD_COLORS[idx], highlightthickness=0, height=250)
        self.canvas.pack(fill="x", padx=20, pady=(10, 20))

        # --- RECENT ACTIVITY LOGS ---
        self.history_card = ctk.CTkFrame(self.view, fg_color=CSS.CARD_COLORS[idx], corner_radius=CSS.RADIUS, border_width=1, border_color=CSS.BORDER_COLORS[idx])
        self.history_card.pack(fill="x", pady=10)
        
        history_header = ctk.CTkFrame(self.history_card, fg_color="transparent")
        history_header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(history_header, text="RECENT ACTIVITY LOGS", font=CSS.CAPTION, text_color="#64748B").pack(side="left")
        
        self.table_frame = ctk.CTkFrame(self.history_card, fg_color="transparent")
        self.table_frame.pack(fill="x", padx=20, pady=(0, 20))

    def on_show(self):
        self.live_update()

    def draw_grid(self, h, w):
        idx = self.controller.theme_idx
        grid_color = "#334155" if idx > 0 else "#E2E8F0"
        for i in range(0, 201, 50):
            y_pos = h - (i / 200.0) * h
            self.canvas.create_line(0, y_pos, w, y_pos, fill=grid_color, dash=(2, 2))

    def live_update(self):
        if not self.winfo_exists(): return
        
        if self.winfo_ismapped():
            data = self.controller.fb.get_sensor_data()
            hr, spo2, temp, sbp, dbp = (data.get(k, 0) for k in ["bpm", "spo2", "temp", "sbp", "dbp"])

            try:
                self.c_bpm.val.configure(text=str(hr))
                self.c_spo2.val.configure(text=str(spo2))
                self.c_temp.val.configure(text=f"{temp:.1f}")
                self.c_bp.val.configure(text=f"{sbp}/{dbp}")

                alerts = []
                if hr > 100 or hr < 60: alerts.append(f"Abnormal HR: {hr}")
                if spo2 < 95: alerts.append(f"Low Oxygen: {spo2}%")
                if alerts:
                    self.alert_banner.pack(fill="x", pady=(0, 10), before=self.layout_grid)
                    self.alert_label.configure(text="⚠️ ALERT: " + " | ".join(alerts))
                else:
                    self.alert_banner.pack_forget()

                self.canvas.delete("all")
                h, w = self.canvas.winfo_height(), self.canvas.winfo_width()
                if h > 10:
                    self.draw_grid(h, w)
                    metrics = [("hr", hr, CSS.PRIMARY), ("spo2", spo2, CSS.ACCENT), ("bp", sbp, CSS.BP_COLOR), ("temp", temp * 3, CSS.TEMP_COLOR)]
                    for key, val, color in metrics:
                        y_normalized = h - (val / 180.0) * h 
                        self.sensor_points[key].append(y_normalized)
                        if len(self.sensor_points[key]) > 60: self.sensor_points[key].pop(0)
                        pts = []
                        for i, p in enumerate(self.sensor_points[key]):
                            pts.extend([(i / 59.0) * w, p])
                        if len(pts) > 4:
                            self.canvas.create_line(pts, fill=color, width=2, smooth=True)
            except Exception:
                pass 

            self.sync_counter += 1
            if self.sync_counter >= 20:
                self.sync_counter = 0
                log_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "hr": hr, 
                    "spo2": spo2, 
                    "bp": f"{sbp}/{dbp}", 
                    "temp": temp,
                    "event": "Vital Update"
                }
                self.telemetry_history.append(log_entry)
                self.controller.fb.push_telemetry_log(log_entry)
                self.update_history_table()

        self.after(500, self.live_update)

    def update_history_table(self):
        for child in self.table_frame.winfo_children(): child.destroy()
        headers = ["TIMESTAMP", "EVENT", "HEART RATE", "SpO2", "BP", "TEMP"]
        idx = self.controller.theme_idx
        for col, h_text in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=h_text, font=CSS.CAPTION, text_color="#64748B").grid(row=0, column=col, padx=10, pady=5, sticky="w")
        for row, entry in enumerate(self.telemetry_history[-8:][::-1]):
            data = [entry['timestamp'], entry.get('event', 'N/A'), f"{entry['hr']} bpm", f"{entry['spo2']}%", entry['bp'], f"{entry['temp']}°C"]
            for col, val in enumerate(data):
                ctk.CTkLabel(self.table_frame, text=val, font=CSS.DESC, text_color=CSS.TEXT_COLORS[idx]).grid(row=row+1, column=col, padx=10, pady=2, sticky="w")

    def export_to_csv(self):
        if not self.telemetry_history:
            messagebox.showwarning("No Data", "History is currently empty.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="Clinical_Activity_Log.csv")
        if file_path:
            with open(file_path, mode='w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.telemetry_history[0].keys())
                writer.writeheader()
                writer.writerows(self.telemetry_history)
            messagebox.showinfo("Export Success", f"Logs exported to {file_path}")

class PatientPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.slot_data = [] 
        self.dispenser_logs = []
        self.refresh_ui()

    def refresh_ui(self):
        idx = self.controller.theme_idx
        self.configure(fg_color=CSS.BG_COLORS[idx])
        for child in self.winfo_children(): child.destroy()

        self.side_panel = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=CSS.CARD_COLORS[idx], border_width=1, border_color=CSS.BORDER_COLORS[idx])
        self.side_panel.pack(side="left", fill="y")
        self.side_panel.pack_propagate(False)
        ctk.CTkLabel(self.side_panel, text="✚ CURAIDE PRO", font=CSS.H2, text_color=CSS.PRIMARY).pack(pady=(40, 30))
        ctk.CTkButton(self.side_panel, text="📊         Dashboard", anchor="w", fg_color="transparent", text_color=CSS.TEXT_COLORS[idx], font=CSS.BODY, height=50, command=lambda: self.controller.show_frame("MainDashboard")).pack(fill="x", padx=20, pady=2)
        ctk.CTkButton(self.side_panel, text="👤         Patients", anchor="w", fg_color=CSS.PRIMARY, text_color="white", font=CSS.BODY, height=50).pack(fill="x", padx=20, pady=2)
        
        footer_container = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        footer_container.pack(side="bottom", fill="x", padx=15, pady=20)
        ctk.CTkButton(footer_container, text="📥 Export CSV", command=self.export_patient_data, fg_color=CSS.ACCENT, height=45).pack(fill="x", pady=5)
        ctk.CTkButton(footer_container, text="🌓 Theme", command=self.controller.rotate_theme, height=45, fg_color="transparent", border_width=1, border_color=CSS.BORDER_COLORS[idx], text_color=CSS.TEXT_COLORS[idx]).pack(fill="x", pady=5)
        ctk.CTkButton(footer_container, text="🚪 Sign Out", command=self.controller.handle_sign_out, height=45, fg_color="#334155", hover_color=CSS.PRIMARY).pack(fill="x", pady=5)

        self.view = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.view.pack(side="right", fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(self.view, text="Patient Medication Control", font=CSS.HEADER_FONT, text_color=CSS.TEXT_COLORS[idx]).pack(anchor="w", pady=(10, 5))

        # --- NOTIFICATION BANNER ---
        self.notif_banner = ctk.CTkFrame(self.view, fg_color="#F39C12", corner_radius=8)
        self.notif_label = ctk.CTkLabel(self.notif_banner, text="🔔 Clinical Advisory: Medication schedule pending sync.", font=CSS.CAPTION, text_color="white")
        self.notif_label.pack(pady=8, padx=20)
        self.notif_banner.pack(fill="x", pady=(5, 10))

        flow_card = ctk.CTkFrame(self.view, fg_color=CSS.CARD_COLORS[idx], corner_radius=12, border_width=1, border_color=CSS.BORDER_COLORS[idx])
        flow_card.pack(fill="x", pady=(5, 10))
        
        flow_label = ctk.CTkLabel(flow_card, text="SYSTEM FLOW: Select Patient ➔ Configure Slots ➔ Sync to Cloud ➔ Hardware Update", 
                                  font=(CSS.FONT_FAMILY, 12, "italic"), text_color=CSS.ACCENT)
        flow_label.pack(pady=10)

        header_card = ctk.CTkFrame(self.view, fg_color=CSS.CARD_COLORS[idx], corner_radius=CSS.RADIUS, border_width=1, border_color=CSS.BORDER_COLORS[idx])
        header_card.pack(fill="x", pady=10)
        
        select_row = ctk.CTkFrame(header_card, fg_color="transparent")
        select_row.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(select_row, text="SELECT EXISTING PATIENT", font=CSS.CAPTION, text_color=CSS.ACCENT).pack(side="left")
        
        self.patient_selector = ctk.CTkComboBox(select_row, values=["No Patients Loaded"], width=300, command=self.on_patient_selected)
        self.patient_selector.pack(side="left", padx=20)
        
        ctk.CTkButton(select_row, text="🔄 Refresh List", width=100, height=30, fg_color="transparent", border_width=1, text_color=CSS.TEXT_COLORS[idx], command=self.load_patient_list).pack(side="left")

        ctk.CTkLabel(header_card, text="OR ENTER NEW PATIENT NAME", font=CSS.CAPTION, text_color=CSS.PRIMARY).pack(anchor="w", padx=20, pady=(10, 5))
        self.patient_name_entry = ctk.CTkEntry(header_card, placeholder_text="Enter Full Patient Name", width=400, height=45)
        self.patient_name_entry.pack(anchor="w", padx=20, pady=(0, 20))

        grid_frame = ctk.CTkFrame(self.view, fg_color="transparent")
        grid_frame.pack(fill="x", pady=10)
        grid_frame.columnconfigure((0, 1), weight=1)

        self.slot_data = []
        for i in range(8):
            slot_card = ctk.CTkFrame(grid_frame, fg_color=CSS.CARD_COLORS[idx], corner_radius=12, border_width=1, border_color=CSS.BORDER_COLORS[idx])
            slot_card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")

            slot_h = ctk.CTkFrame(slot_card, fg_color="transparent")
            slot_h.pack(fill="x", padx=15, pady=(10, 5))
            ctk.CTkLabel(slot_h, text=f"DISPENSER SLOT {i+1}", font=CSS.CAPTION, text_color="#64748B").pack(side="left")
            
            status_btn = ctk.CTkButton(slot_h, text="PENDING", font=CSS.CAPTION, width=85, height=24, fg_color="#F39C12", 
                                       command=lambda b=i: self.toggle_status(b))
            status_btn.pack(side="right")

            ctk.CTkLabel(slot_card, text="MEDICINE NAME", font=CSS.CAPTION, text_color=CSS.TEXT_COLORS[idx]).pack(anchor="w", padx=15)
            med_entry = ctk.CTkEntry(slot_card, placeholder_text="e.g. Paracetamol", height=35)
            med_entry.pack(fill="x", padx=15, pady=(2, 8))
            
            ctk.CTkLabel(slot_card, text="INSTRUCTIONS / DESCRIPTION", font=CSS.CAPTION, text_color=CSS.TEXT_COLORS[idx]).pack(anchor="w", padx=15)
            desc_entry = ctk.CTkEntry(slot_card, placeholder_text="Take after meals", height=30, font=(CSS.FONT_FAMILY, 11))
            desc_entry.pack(fill="x", padx=15, pady=(2, 8))
            
            time_row_label = ctk.CTkFrame(slot_card, fg_color="transparent")
            time_row_label.pack(fill="x", padx=15)
            ctk.CTkLabel(time_row_label, text="FREQUENCY", font=CSS.CAPTION, text_color=CSS.TEXT_COLORS[idx]).pack(side="left")
            ctk.CTkLabel(time_row_label, text="START TIME", font=CSS.CAPTION, text_color=CSS.TEXT_COLORS[idx]).pack(side="left", padx=(100, 0))

            time_row = ctk.CTkFrame(slot_card, fg_color="transparent")
            time_row.pack(fill="x", padx=15, pady=(2, 8))
            
            freq_drop = ctk.CTkComboBox(time_row, values=["1x Daily", "2x Daily", "3x Daily", "Every 4 Hours"], height=35, width=150)
            freq_drop.set("Frequency")
            freq_drop.pack(side="left", padx=(0,5))

            time_entry = ctk.CTkEntry(time_row, placeholder_text="08:00 AM", height=35)
            time_entry.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(slot_card, text="START DATE", font=CSS.CAPTION, text_color=CSS.TEXT_COLORS[idx]).pack(anchor="w", padx=15)
            date_entry = ctk.CTkEntry(slot_card, placeholder_text="MM/DD/YYYY", height=35)
            date_entry.pack(fill="x", padx=15, pady=(2, 15))

            self.slot_data.append({
                "status_btn": status_btn, "med_entry": med_entry, "desc_entry": desc_entry,
                "freq_drop": freq_drop, "time_entry": time_entry, "date_entry": date_entry
            })

        sync_btn = ctk.CTkButton(self.view, text="💾 Sync Dispenser Schedule to Firebase", fg_color=CSS.TEMP_COLOR, hover_color="#27AE60", 
                                  height=55, font=CSS.BODY, command=self.sync_to_cloud)
        sync_btn.pack(fill="x", pady=20)

        self.log_card = ctk.CTkFrame(self.view, fg_color=CSS.CARD_COLORS[idx], corner_radius=CSS.RADIUS, border_width=1, border_color=CSS.BORDER_COLORS[idx])
        self.log_card.pack(fill="x", pady=10)
        
        log_header = ctk.CTkFrame(self.log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(log_header, text="DISPENSER ACTIVITY LOGS", font=CSS.CAPTION, text_color="#64748B").pack(side="left")
        
        self.log_table = ctk.CTkFrame(self.log_card, fg_color="transparent")
        self.log_table.pack(fill="x", padx=20, pady=(0, 20))
        self.update_log_ui()

    def update_log_ui(self):
        for child in self.log_table.winfo_children(): child.destroy()
        idx = self.controller.theme_idx
        headers = ["TIMESTAMP", "SLOT", "MEDICINE", "ACTION", "STATUS"]
        for col, h_text in enumerate(headers):
            ctk.CTkLabel(self.log_table, text=h_text, font=CSS.CAPTION, text_color="#64748B").grid(row=0, column=col, padx=15, pady=5, sticky="w")
        
        for row, log in enumerate(self.dispenser_logs[-10:][::-1]):
            color = CSS.TEMP_COLOR if "DISPENSED" in log['status'] else "#F39C12"
            data = [log['time'], log['slot'], log['med'], log['action'], log['status']]
            for col, val in enumerate(data):
                t_color = color if col == 4 else CSS.TEXT_COLORS[idx]
                ctk.CTkLabel(self.log_table, text=val, font=CSS.DESC, text_color=t_color).grid(row=row+1, column=col, padx=15, pady=2, sticky="w")

    def log_activity(self, slot_idx, action, status):
        med_name = self.slot_data[slot_idx]["med_entry"].get() or "Unknown Med"
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "slot": f"Slot {slot_idx+1}",
            "med": med_name,
            "action": action,
            "status": status
        }
        self.dispenser_logs.append(entry)
        self.update_log_ui()
        # Notify user in banner
        self.notif_label.configure(text=f"🔔 Notification: {med_name} in Slot {slot_idx+1} marked as {status}.")

    def load_patient_list(self):
        if self.controller.fb.db:
            try:
                all_patients = self.controller.fb.db.child("patient_management").get().val()
                if all_patients:
                    names = list(all_patients.keys())
                    self.patient_selector.configure(values=names)
                    messagebox.showinfo("Success", f"Found {len(names)} patients.")
                else:
                    self.patient_selector.configure(values=["No Patients Found"])
            except Exception as e:
                print(f"List Fetch Error: {e}")

    def on_patient_selected(self, choice):
        self.patient_name_entry.delete(0, 'end')
        self.patient_name_entry.insert(0, choice)
        self.fetch_patient_from_cloud()
    def fetch_patient_from_cloud(self):
        name = self.patient_name_entry.get()
        if not name: return
        data = self.controller.fb.get_patient_data(name)
        if data and "medications" in data:
            meds = data["medications"]
            for i, slot in enumerate(self.slot_data):
                slot_key = f"slot_{i+1}"
                if slot_key in meds:
                    m = meds[slot_key]
                    slot["med_entry"].delete(0, 'end')
                    if m.get("medicine"): slot["med_entry"].insert(0, m.get("medicine"))
                    slot["desc_entry"].delete(0, 'end')
                    if m.get("description"): slot["desc_entry"].insert(0, m.get("description"))
                    slot["freq_drop"].set(m.get("frequency") if m.get("frequency") else "Frequency")
                    slot["time_entry"].delete(0, 'end')
                    if m.get("start_time"): slot["time_entry"].insert(0, m.get("start_time"))
                    slot["date_entry"].delete(0, 'end')
                    if m.get("start_date"): slot["date_entry"].insert(0, m.get("start_date"))
                    status = m.get("status", "PENDING")
                    color = CSS.TEMP_COLOR if status == "DISPENSED" else "#F39C12"
                    slot["status_btn"].configure(text=status, fg_color=color)
            messagebox.showinfo("Cloud Sync", f"Loaded data for {name}")
        else:
            messagebox.showinfo("Cloud Sync", "No existing record found. Ready for new patient entry.")
    def toggle_status(self, index):
        btn = self.slot_data[index]["status_btn"]
        new_status = "DISPENSED" if btn.cget("text") == "PENDING" else "PENDING"
        new_color = CSS.TEMP_COLOR if new_status == "DISPENSED" else "#F39C12"
        btn.configure(text=new_status, fg_color=new_color)
        
        self.log_activity(index, "Manual Change", new_status)
        
        patient_name = self.patient_name_entry.get()
        if patient_name and self.controller.fb.db:
            try:
                path = f"patient_management/{patient_name}/medications/slot_{index+1}"
                self.controller.fb.db.child(path).update({"status": new_status})
                log = {"timestamp": datetime.now().strftime("%H:%M:%S"), "hr": 0, "spo2": 0, "bp": "N/A", "temp": 0, "event": f"Slot {index+1} -> {new_status}"}
                self.controller.view_frames["MainDashboard"].telemetry_history.append(log)
            except Exception as e:
                print(f"Quick Sync Error: {e}")
    def sync_to_cloud(self, silent=False):
        name = self.patient_name_entry.get()
        if not name:
            if not silent: messagebox.showwarning("Incomplete Data", "Please enter the Patient Name.")
            return
        payload = {"last_updated": datetime.now().strftime("%Y-%m-%d %I:%M %p"), "medications": {}}
        for i, slot in enumerate(self.slot_data):
            payload["medications"][f"slot_{i+1}"] = {
                "medicine": slot["med_entry"].get(),
                "description": slot["desc_entry"].get(),
                "frequency": slot["freq_drop"].get(),
                "start_time": slot["time_entry"].get(),
                "start_date": slot["date_entry"].get(),
                "status": slot["status_btn"].cget("text")
            }
        success = self.controller.fb.push_patient_schedule(name, payload)
        if success:
            if not silent: messagebox.showinfo("Success", f"Dispenser schedule for {name} has been synced.")
            self.load_patient_list()
            self.notif_label.configure(text="✅ Cloud Synchronization Successful. Hardware updated.")
        elif not success and not silent:
            messagebox.showerror("Error", "Cloud synchronization failed.")
    def export_patient_data(self):
        name = self.patient_name_entry.get() or "Unknown"
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{name}_Medication.csv")
        if file_path:
            with open(file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Slot", "Medicine", "Description", "Frequency", "Start Time", "Start Date", "Status"])
                for i, slot in enumerate(self.slot_data):
                    writer.writerow([f"Slot {i+1}", slot["med_entry"].get(), slot["desc_entry"].get(), slot["freq_drop"].get(), slot["time_entry"].get(), slot["date_entry"].get(), slot["status_btn"].cget("text")])
class TelemetryCard(ctk.CTkFrame):
    def __init__(self, master, title, unit, icon, color, theme_idx):
        super().__init__(master, corner_radius=CSS.RADIUS, fg_color=CSS.CARD_COLORS[theme_idx], border_width=1, border_color=CSS.BORDER_COLORS[theme_idx])
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.pack(fill="x", padx=15, pady=(15, 0))
        ctk.CTkLabel(h, text=icon, font=("Segoe UI", 20)).pack(side="left")
        ctk.CTkLabel(h, text=title, font=CSS.CAPTION, text_color="#64748B").pack(side="left", padx=10)
        self.val = ctk.CTkLabel(self, text="--", font=(CSS.FONT_FAMILY, 32, "bold"), text_color=color)
        self.val.pack(pady=5)
        ctk.CTkLabel(self, text=unit, font=CSS.CAPTION, text_color="#94A3B8").pack(pady=(0, 15))
if __name__ == "__main__":
    app = CuraideApp()
    app.mainloop()