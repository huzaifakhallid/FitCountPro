# src/ui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import csv
import os
from datetime import datetime

from tracker.pose_detector import PoseDetector
from exercises.squats import SquatCounter

class FitCountProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FitCount Pro")
        self.geometry("1280x720")
        self.configure(bg="#2E2E2E")

        # --- Application State ---
        self.is_running = False  # Start in a "stopped" state
        self.set_counter = 1
        
        # --- Session Data ---
        self.session_data = []

        # --- Core Components ---
        self.cap = cv2.VideoCapture(0)
        self.detector = PoseDetector()
        self.squat_counter = SquatCounter()
        
        # --- UI Setup ---
        self.create_widgets()
        
        # --- Start the video loop ---
        self.update_frame()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        video_frame = tk.Frame(main_frame, bg="black")
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.video_label = tk.Label(video_frame, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        control_frame = tk.Frame(main_frame, width=300, bg="#3C3C3C")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_frame.pack_propagate(False)
        panel_content = tk.Frame(control_frame, bg="#3C3C3C", padx=20, pady=20)
        panel_content.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(panel_content, text="FitCount Pro", font=("Arial", 24, "bold"), fg="white", bg="#3C3C3C")
        title_label.pack(pady=(0, 20))
        self.reps_label = tk.Label(panel_content, text="REPS: 0", font=("Arial", 32, "bold"), fg="#4CAF50", bg="#3C3C3C")
        self.reps_label.pack(pady=10)
        self.sets_label = tk.Label(panel_content, text=f"SETS: {self.set_counter}", font=("Arial", 20), fg="white", bg="#3C3C3C")
        self.sets_label.pack(pady=10)
        self.stage_label = tk.Label(panel_content, text="STAGE: -", font=("Arial", 20), fg="cyan", bg="#3C3C3C")
        self.stage_label.pack(pady=20)
        
        self.start_stop_button = tk.Button(panel_content, text="Start Session", command=self.toggle_session, font=("Arial", 14), bg="#4CAF50", fg="white", relief=tk.FLAT, padx=10, pady=5)
        self.start_stop_button.pack(fill='x', pady=10)


    def toggle_session(self):
        """Starts or stops the exercise tracking session."""
        self.is_running = not self.is_running
        if self.is_running:
            self.start_stop_button.config(text="Stop Session", bg="#F44336")
            # Reset counters for the new session
            self.squat_counter.counter = 0
            self.set_counter = 1
            self.session_data = [] # Clear data from previous session
            self.update_ui()
        else:
            self.start_stop_button.config(text="Start Session", bg="#4CAF50")
            # When stopping, log the final set and save the whole session
            self.log_current_set()
            self.save_session_log()
            # Show a summary message
            messagebox.showinfo("Session Saved", f"Workout data saved to logs/session_log.csv")

    def update_frame(self):
        """Continuously updates the video feed. Processes poses only if session is running."""
        success, frame = self.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return

        frame = cv2.flip(frame, 1)

        if self.is_running:
            frame = self.detector.find_pose(frame, draw=True)
            landmarks = self.detector.get_landmarks(frame)

            if landmarks:
                self.squat_counter.process(landmarks)
            
            self.update_ui()
        else:
            # If not running, just show the plain webcam feed
            pass

        # Convert for Tkinter
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

        self.after(10, self.update_frame)
        
    def update_ui(self):
        """Updates the labels in the control panel."""
        self.reps_label.config(text=f"REPS: {self.squat_counter.counter}")
        self.sets_label.config(text=f"SETS: {self.set_counter}")
        # Only show stage if running
        stage = self.squat_counter.stage.upper() if self.is_running else "IDLE"
        self.stage_label.config(text=f"STAGE: {stage}")

    def log_current_set(self):
        """Adds the data for the current set to the session log."""
        if self.squat_counter.counter > 0:
            self.session_data.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Exercise": "Squats", # Hardcoded for now
                "Set": self.set_counter,
                "Reps": self.squat_counter.counter
            })
            print(f"Logged Set: {self.session_data[-1]}")

    def save_session_log(self):
        """Saves the entire session data to a CSV file."""
        if not self.session_data:
            print("No data to save.")
            return

        log_dir = 'logs'
        log_file = os.path.join(log_dir, 'session_log.csv')
        os.makedirs(log_dir, exist_ok=True)
        file_exists = os.path.isfile(log_file)

        with open(log_file, 'a', newline='') as f:
            fieldnames = ["Timestamp", "Exercise", "Set", "Reps"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader() # Write header only if file is new
            
            writer.writerows(self.session_data)
        
        print(f"Session successfully saved to {log_file}")

    def on_closing(self):
        """Handles window close event. Asks to save if a session is active."""
        if self.is_running:
            if messagebox.askyesno("Quit", "A session is running. Do you want to stop and save it before quitting?"):
                self.toggle_session() # This will handle saving the data
            else:
                # If user clicks "No", just close without saving
                pass
        
        print("Closing application...")
        self.cap.release()
        self.destroy()