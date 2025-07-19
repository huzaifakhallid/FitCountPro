import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

from tracker.pose_detector import PoseDetector
from exercises.squats import SquatCounter

class FitCountProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FitCount Pro - AI Fitness Tracker")
        self.geometry("1280x720")
        self.configure(bg="#2E2E2E")

        # --- State & Logic ---
        self.is_running = True # Start tracking immediately 
        self.cap = cv2.VideoCapture(0)
        self.pose_detector = PoseDetector()
        self.squat_counter = SquatCounter()

        # --- UI Layout ---
        self.create_widgets()

        # --- Main Loop ---
        self.update_frame()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Creates and lays out the UI elements."""
        # Main container
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel (Video Feed)
        video_frame = tk.Frame(main_frame, bg="black")
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        self.video_label = tk.Label(video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Right Panel (Controls & Stats)
        control_frame = tk.Frame(main_frame, width=300, bg="#3C3C3C", padx=20, pady=20)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        control_frame.pack_propagate(False) # Prevents resizing

        # -- Title --
        title_label = tk.Label(control_frame, text="FitCount Pro", font=("Arial", 24, "bold"), fg="white", bg="#3C3C3C")
        title_label.pack(pady=(0, 30))

        # -- Stats Display --
        self.reps_label = tk.Label(control_frame, text="REPS: 0", font=("Arial", 32, "bold"), fg="#4CAF50", bg="#3C3C3C")
        self.reps_label.pack(pady=20)
        
        self.stage_label = tk.Label(control_frame, text="STAGE: -", font=("Arial", 20), fg="cyan", bg="#3C3C3C")
        self.stage_label.pack(pady=20)

    def update_frame(self):
        """Main loop for video and logic updates."""
        success, frame = self.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return

        frame = cv2.flip(frame, 1)
        
        # Pose detection and exercise logic
        if self.is_running:
            frame = self.pose_detector.find_pose(frame)
            landmarks = self.pose_detector.get_landmarks(frame)
            
            if landmarks:
                self.squat_counter.process(landmarks)
                self.update_ui_feedback()

        # Convert for Tkinter display
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img)
        
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)
        
        self.after(10, self.update_frame)

    def update_ui_feedback(self):
        """Updates the feedback labels in the UI."""
        self.reps_label.config(text=f"REPS: {self.squat_counter.counter}")
        self.stage_label.config(text=f"STAGE: {self.squat_counter.stage.upper()}")

    def on_closing(self):
        print("Closing application...")
        self.cap.release()
        self.destroy()