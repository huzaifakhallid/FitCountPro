import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import csv
import os
from datetime import datetime

from tracker.pose_detector import PoseDetector
from exercises.squats import Squats
from exercises.curls import BicepCurls
from exercises.pushups import Pushups

class FitCountProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FitCount Pro")
        self.geometry("1280x720")
        self.configure(bg="#2E2E2E")
        self.is_running = False
        self.set_counter = 1
        self.session_data = []
        self.cap = cv2.VideoCapture(0)
        self.detector = PoseDetector()
        self.exercises = {
            "Bicep Curls": BicepCurls(),
            "Squats": Squats(),
            "Pushups": Pushups()
        }
        self.current_exercise = self.exercises["Squats"]
        self.create_widgets()
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
        
        exercise_label = tk.Label(panel_content, text="Select Exercise:", font=("Arial", 14), fg="white", bg="#3C3C3C")
        exercise_label.pack(anchor="w", pady=(0, 5))
        self.exercise_var = tk.StringVar(value=self.current_exercise.name)
        exercise_menu = ttk.Combobox(panel_content, textvariable=self.exercise_var, values=list(self.exercises.keys()), state="readonly", font=("Arial", 12))
        exercise_menu.pack(fill="x", pady=(0, 20))
        exercise_menu.bind("<<ComboboxSelected>>", self.on_exercise_change)
        
        title_label = tk.Label(panel_content, text="Live Stats", font=("Arial", 18, "bold"), fg="white", bg="#3C3C3C")
        title_label.pack(pady=(0, 20))
        self.reps_label = tk.Label(panel_content, text="REPS: 0", font=("Arial", 32, "bold"), fg="#4CAF50", bg="#3C3C3C")
        self.reps_label.pack(pady=10)
        self.sets_label = tk.Label(panel_content, text=f"SETS: 1", font=("Arial", 20), fg="white", bg="#3C3C3C")
        self.sets_label.pack(pady=10)
        self.stage_label = tk.Label(panel_content, text="STAGE: IDLE", font=("Arial", 20), fg="cyan", bg="#3C3C3C")
        self.stage_label.pack(pady=20)
        
        self.start_stop_button = tk.Button(panel_content, text="Start Session", command=self.toggle_session, font=("Arial", 14), bg="#4CAF50", fg="white", relief=tk.FLAT, padx=10, pady=5)
        self.start_stop_button.pack(fill='x', pady=10)

        self.next_set_button = tk.Button(panel_content, text="Next Set", command=self.next_set, font=("Arial", 14), bg="#FFC107", fg="black", relief=tk.FLAT, padx=10, pady=5, state=tk.DISABLED)
        self.next_set_button.pack(fill='x', pady=10)

    def on_exercise_change(self, event):
        # Log the completed set before switching exercises
        if self.is_running:
            self.log_current_set() 
        
        selected_exercise_name = self.exercise_var.get()
        self.current_exercise = self.exercises[selected_exercise_name]
        print(f"Changed exercise to: {self.current_exercise.name}")
        
        # Reset counters for the new exercise
        self.current_exercise.reset()
        self.update_ui()


    def toggle_session(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_stop_button.config(text="Stop Session", bg="#F44336")
            self.next_set_button.config(state=tk.NORMAL) # Enable next set button
            self.current_exercise.reset()
            self.set_counter = 1
            self.session_data = []
            self.update_ui()
        else:
            self.start_stop_button.config(text="Start Session", bg="#4CAF50")
            self.next_set_button.config(state=tk.DISABLED) # Disable next set button
            
            # Log the final set, save, and show summary
            self.log_current_set()
            self.save_session_log()
            self.show_summary()

    def next_set(self):
        """Logs the current set and prepares for the next one."""
        if not self.is_running:
            return

        # Log the set that was just completed
        self.log_current_set()

        # Increment set counter
        self.set_counter += 1

        # Reset the rep counter for the current exercise
        self.current_exercise.reset()

        # Update the UI to reflect the new set and zero reps
        self.update_ui()
        print(f"Starting Set {self.set_counter}")
        
    def show_summary(self):
        """Displays a summary of the completed session in a message box."""
        if not self.session_data:
            messagebox.showinfo("Session Over", "No workout data was recorded.")
            return
        
        summary_text = "Session Summary:\n\n"
        total_reps = 0
        for entry in self.session_data:
            summary_text += f"- {entry['Exercise']} | Set {entry['Set']}: {entry['Reps']} reps\n"
            total_reps += entry['Reps']
        
        summary_text += f"\nGreat work! You completed a total of {total_reps} reps."
        
        messagebox.showinfo("Session Over", summary_text)

    def update_frame(self):
        success, frame = self.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return
        frame = cv2.flip(frame, 1)
        if self.is_running:
            frame = self.detector.find_pose(frame, draw=True)
            landmarks = self.detector.get_landmarks(frame)
            if landmarks:
                self.current_exercise.process_landmarks(landmarks)
            self.update_ui()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)
        self.after(10, self.update_frame)
        
    def update_ui(self):
        self.reps_label.config(text=f"REPS: {self.current_exercise.get_counter()}")
        self.sets_label.config(text=f"SETS: {self.set_counter}")
        stage = self.current_exercise.get_stage() if self.is_running else "IDLE"
        self.stage_label.config(text=f"STAGE: {stage}")

    def log_current_set(self):
        if self.is_running and self.current_exercise.get_counter() > 0:
            self.session_data.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Exercise": self.current_exercise.name,
                "Set": self.set_counter,
                "Reps": self.current_exercise.get_counter()
            })
            print(f"Logged Set: {self.session_data[-1]}")

    def save_session_log(self):
        if not self.session_data: return
        log_dir = 'logs'
        log_file = os.path.join(log_dir, 'session_log.csv')
        os.makedirs(log_dir, exist_ok=True)
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='') as f:
            fieldnames = ["Timestamp", "Exercise", "Set", "Reps"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists: writer.writeheader()
            writer.writerows(self.session_data)
        print(f"Session successfully saved to {log_file}")

    def on_closing(self):
        if self.is_running:
            if messagebox.askyesno("Quit", "A session is running. Do you want to stop and save it before quitting?"):
                self.toggle_session()
        print("Closing application...")
        self.cap.release()
        self.destroy()