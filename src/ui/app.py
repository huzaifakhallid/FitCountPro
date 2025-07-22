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

# ===================================================================
# STYLING AND CUSTOM WIDGETS
# ===================================================================

# -- Color Palette --
COLOR_PRIMARY_BG = "#1E1E1E"
COLOR_SECONDARY_BG = "#2D2D2D"
COLOR_WIDGET_BG = "#3C3C3C"
COLOR_TEXT = "#E0E0E0"
COLOR_PRIMARY_ACCENT = "#00A67E" #teal/green
COLOR_SECONDARY_ACCENT = "#FFB400" # yellow/orange
COLOR_DANGER = "#F44336" # red

# -- Fonts --
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_NORMAL = ("Segoe UI", 12)
FONT_H1 = ("Segoe UI", 28, "bold")
FONT_H2 = ("Segoe UI", 20, "bold")

class HoverButton(tk.Button):
    """A custom button that changes color on hover."""
    def __init__(self, master, hover_bg, hover_fg, **kw):

        if 'pady' not in kw:
            kw['pady'] = 5
        tk.Button.__init__(self, master=master, **kw)
        self.default_bg = self["background"]
        self.default_fg = self["foreground"]
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self.hover_bg
        self['foreground'] = self.hover_fg

    def on_leave(self, e):
        self['background'] = self.default_bg
        self['foreground'] = self.default_fg


# ===================================================================
# MAIN APPLICATION
# ===================================================================
class FitCountProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FitCount Pro")
        self.geometry("1090x590")
        self.configure(bg=COLOR_PRIMARY_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_styles()
        self.is_running = False
        self.workout_plan = []
        self.current_plan_index = 0
        self.current_set_in_plan = 1
        self.session_data = []
        self.cap = cv2.VideoCapture(0)
        self.detector = PoseDetector()
        self.exercises = {
            "Bicep Curls": BicepCurls(), "Squats": Squats(), "Pushups": Pushups()
        }
        self.current_exercise = None
        self.container = tk.Frame(self, bg=COLOR_PRIMARY_BG)
        self.container.pack(fill="both", expand=True)
        self.frames = {}
        self.create_frames()
        self.show_frame("StartupScreen")

    def setup_styles(self):
        """Configures the styles for ttk widgets."""
        style = ttk.Style(self)
        style.theme_use('clam') 

        # Style for Combobox (Dropdown)
        style.configure('TCombobox', 
                        selectbackground=COLOR_WIDGET_BG,
                        fieldbackground=COLOR_WIDGET_BG,
                        background=COLOR_WIDGET_BG,
                        foreground=COLOR_TEXT,
                        arrowcolor=COLOR_TEXT,
                        padding=5)
        # Remove the border from the dropdown
        style.map('TCombobox',
                  fieldbackground=[('readonly', COLOR_WIDGET_BG)],
                  selectforeground=[('readonly', COLOR_TEXT)],
                  bordercolor=[('!focus', COLOR_WIDGET_BG), ('focus', COLOR_PRIMARY_ACCENT)],
                  lightcolor=[('!focus', COLOR_WIDGET_BG)],
                  darkcolor=[('!focus', COLOR_WIDGET_BG)])
        # For the dropdown list itself
        self.option_add('*TCombobox*Listbox.background', COLOR_WIDGET_BG)
        self.option_add('*TCombobox*Listbox.foreground', COLOR_TEXT)
        self.option_add('*TCombobox*Listbox.selectBackground', COLOR_PRIMARY_ACCENT)
        self.option_add('*TCombobox*Listbox.selectForeground', 'white')

        # Style for Spinbox
        style.configure('TSpinbox',
                        background=COLOR_WIDGET_BG,
                        foreground=COLOR_TEXT,
                        fieldbackground=COLOR_WIDGET_BG,
                        arrowcolor=COLOR_TEXT,
                        arrowsize=20)
        style.map('TSpinbox',
                  background=[('readonly', COLOR_WIDGET_BG), ('disabled', COLOR_WIDGET_BG)])

    def create_frames(self):
        for F in (StartupScreen, PlannerScreen, WorkoutScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "WorkoutScreen": frame.start_video()
        else: self.frames["WorkoutScreen"].stop_video()
    def start_workout(self, plan):
        self.workout_plan = [item for item in plan if item['sets'] > 0 and item['reps'] > 0]
        if not self.workout_plan:
            messagebox.showwarning("Empty Plan", "Please set reps and sets for at least one exercise.")
            return
        self.is_running = True
        self.session_data = []
        self.current_plan_index = -1
        self.load_next_exercise()
        self.show_frame("WorkoutScreen")
    def load_next_exercise(self):
        self.current_plan_index += 1
        if self.current_plan_index >= len(self.workout_plan):
            self.end_workout()
            return
        plan_item = self.workout_plan[self.current_plan_index]
        exercise_name = plan_item["exercise"]
        self.current_exercise = self.exercises[exercise_name]
        self.current_set_in_plan = 1
        self.current_exercise.reset()
        self.frames["WorkoutScreen"].update_exercise_info()
    def end_workout(self):
        self.is_running = False
        self.save_session_log()
        self.show_summary()
        self.show_frame("StartupScreen")
    def on_closing(self):
        self.cap.release()
        self.destroy()
    def log_current_set(self):
        if not self.current_exercise or self.current_exercise.get_counter() == 0: return
        plan_item = self.workout_plan[self.current_plan_index]
        self.session_data.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Exercise": plan_item["exercise"],
            "Set": self.current_set_in_plan,
            "Reps": self.current_exercise.get_counter()
        })
    def save_session_log(self):
        if not self.session_data: return
        log_dir = 'logs'; log_file = os.path.join(log_dir, 'session_log.csv')
        os.makedirs(log_dir, exist_ok=True)
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='') as f:
            fieldnames = ["Timestamp", "Exercise", "Set", "Reps"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists: writer.writeheader()
            writer.writerows(self.session_data)
    def show_summary(self):
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

# ===================================================================
# UI Screen Classes 
# ===================================================================

class HoverButton(tk.Button):
    """A custom button that changes color on hover."""
    def __init__(self, master, hover_bg, hover_fg, **kw):

        if 'pady' not in kw:
            kw['pady'] = 5

        tk.Button.__init__(self, master=master, **kw)
        self.default_bg = self["background"]
        self.default_fg = self["foreground"]
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self.hover_bg
        self['foreground'] = self.hover_fg

    def on_leave(self, e):
        self['background'] = self.default_bg
        self['foreground'] = self.default_fg
        

# ===================================================================
# UI Screen Classes 
# ===================================================================

class StartupScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLOR_PRIMARY_BG)
        self.controller = controller

        center_frame = tk.Frame(self, bg=COLOR_PRIMARY_BG)

        label = tk.Label(center_frame, text="FitCount Pro", font=("Segoe UI", 48, "bold"), fg="white", bg=COLOR_PRIMARY_BG)
        label.pack(pady=(10, 10))
        
        sub_label = tk.Label(center_frame, text="Your AI-Powered Desktop Fitness Tracker", font=("Segoe UI", 16), fg=COLOR_TEXT, bg=COLOR_PRIMARY_BG)
        sub_label.pack(pady=(0, 60))

        plan_button = HoverButton(center_frame, text="Plan New Workout", font=("Segoe UI", 18), bg=COLOR_PRIMARY_ACCENT, fg="white", relief=tk.FLAT,
                                  hover_bg=COLOR_TEXT, hover_fg=COLOR_PRIMARY_BG,
                                  padx=20, pady=15, command=lambda: controller.show_frame("PlannerScreen"))
        plan_button.pack(pady=10)
        
        quick_start_button = HoverButton(center_frame, text="Quick Start (3x10 Squats)", font=FONT_NORMAL, bg=COLOR_WIDGET_BG, fg=COLOR_TEXT, relief=tk.FLAT,
                                         hover_bg=COLOR_SECONDARY_ACCENT, hover_fg="black",
                                         padx=20, pady=10, command=self.quick_start)
        quick_start_button.pack(pady=10)
        
        center_frame.pack(expand=True)

    def quick_start(self):
        default_plan = [{"exercise": "Squats", "sets": 3, "reps": 10}]
        self.controller.start_workout(default_plan)



class PlannerScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLOR_PRIMARY_BG)
        self.controller = controller
        self.entries = {}
        
        label = tk.Label(self, text="Plan Your Workout", font=FONT_H1, fg="white", bg=COLOR_PRIMARY_BG)
        label.pack(pady=(40, 30))

        for exercise_name in controller.exercises.keys():
            frame = tk.Frame(self, bg=COLOR_SECONDARY_BG, padx=15, pady=15)
            tk.Label(frame, text=exercise_name, font=("Segoe UI", 16), fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG, width=15, anchor="w").pack(side="left", padx=10)
            
            tk.Label(frame, text="Reps:", font=FONT_NORMAL, fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG).pack(side="left")
            reps_entry = ttk.Spinbox(frame, from_=0, to=100, width=4, font=FONT_NORMAL, style='TSpinbox')
            reps_entry.pack(side="left", padx=(5, 15))
            reps_entry.set(0)

            tk.Label(frame, text="Sets:", font=FONT_NORMAL, fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG).pack(side="left")
            sets_entry = ttk.Spinbox(frame, from_=0, to=10, width=4, font=FONT_NORMAL, style='TSpinbox')
            sets_entry.pack(side="left", padx=5)
            sets_entry.set(0)

            self.entries[exercise_name] = {"reps": reps_entry, "sets": sets_entry}
            frame.pack(fill="x", padx=300, pady=8)

        button_frame = tk.Frame(self, bg=COLOR_PRIMARY_BG)
        start_button = HoverButton(button_frame, text="Start Workout", font=("Segoe UI", 16), bg=COLOR_PRIMARY_ACCENT, fg="white", relief=tk.FLAT, command=self.create_plan_and_start, hover_bg=COLOR_TEXT, hover_fg=COLOR_PRIMARY_BG)
        start_button.pack(side="left", padx=10, pady=40, ipady=5, ipadx=10)
        
        back_button = HoverButton(button_frame, text="Back", font=("Segoe UI", 16), bg=COLOR_WIDGET_BG, fg=COLOR_TEXT, relief=tk.FLAT, command=lambda: controller.show_frame("StartupScreen"), hover_bg=COLOR_TEXT, hover_fg="black")
        back_button.pack(side="left", padx=10, pady=40, ipady=5, ipadx=10)
        button_frame.pack()
        
    def create_plan_and_start(self):
        plan = []
        for name, entry_dict in self.entries.items():
            try:
                reps = int(entry_dict["reps"].get()); sets = int(entry_dict["sets"].get())
                if sets > 0 and reps > 0: plan.append({"exercise": name, "sets": sets, "reps": reps})
            except ValueError: continue
        self.controller.start_workout(plan)

class WorkoutScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLOR_PRIMARY_BG)
        self.controller = controller
        self.video_loop_active = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=1) 

        # Video Frame
        video_frame = tk.Frame(self, bg="black")
        video_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        self.video_label = tk.Label(video_frame, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Control Panel Frame
        control_frame = tk.Frame(self, bg=COLOR_SECONDARY_BG)
        control_frame.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
        control_frame.grid_propagate(False) 

        panel_container = tk.Frame(control_frame, bg=COLOR_SECONDARY_BG)
        panel_container.pack(expand=True)

        self.exercise_label = tk.Label(panel_container, text="EXERCISE", font=FONT_H2, fg="white", bg=COLOR_SECONDARY_BG)
        self.exercise_label.pack(pady=(0, 40))
        
        self.reps_label = tk.Label(panel_container, text="0 / 10", font=("Segoe UI", 64, "bold"), fg=COLOR_PRIMARY_ACCENT, bg=COLOR_SECONDARY_BG)
        self.reps_label.pack(pady=10)
        tk.Label(panel_container, text="REPS", font=FONT_BOLD, fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG).pack()
        
        self.sets_label = tk.Label(panel_container, text="Set 1 of 3", font=FONT_H2, fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG)
        self.sets_label.pack(pady=30)
        
        self.stage_label = tk.Label(panel_container, text="STAGE: -", font=("Segoe UI", 16), fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG)
        self.stage_label.pack(pady=20)
        
        # Another sub-frame for the buttons at the bottom
        button_frame = tk.Frame(panel_container, bg=COLOR_SECONDARY_BG)
        button_frame.pack(side="bottom", fill="x", pady=(20,0))

        next_set_button = HoverButton(button_frame, text="Next Set / Skip", command=self.next_set, font=FONT_BOLD, bg=COLOR_SECONDARY_ACCENT, fg="black", relief=tk.FLAT, hover_bg=COLOR_TEXT, hover_fg="black", pady=10)
        next_set_button.pack(fill='x', pady=(0,5))
        
        end_button = HoverButton(button_frame, text="End Workout", command=self.confirm_end_workout, font=FONT_BOLD, bg=COLOR_DANGER, fg="white", relief=tk.FLAT, hover_bg=COLOR_TEXT, hover_fg="black", pady=10)
        end_button.pack(fill='x')

    def update_frame(self):
        if not self.video_loop_active: return
        success, frame = self.controller.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            if self.controller.is_running and self.controller.current_exercise:
                frame = self.controller.detector.find_pose(frame, draw=True)
                landmarks = self.controller.detector.get_landmarks(frame)
                if landmarks:
                    prev_reps = self.controller.current_exercise.get_counter()
                    self.controller.current_exercise.process_landmarks(landmarks)
                    new_reps = self.controller.current_exercise.get_counter()
                    target_reps = self.controller.workout_plan[self.controller.current_plan_index]['reps']
                    if new_reps > prev_reps and new_reps >= target_reps: self.next_set()
                self.update_exercise_info()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = img_tk
            self.video_label.configure(image=img_tk)
        self.after(10, self.update_frame)
    def next_set(self):
        self.controller.log_current_set()
        plan_item = self.controller.workout_plan[self.controller.current_plan_index]
        if self.controller.current_set_in_plan < plan_item['sets']:
            self.controller.current_set_in_plan += 1
            self.controller.current_exercise.reset()
            self.update_exercise_info()
        else: self.controller.load_next_exercise()
    def update_exercise_info(self):
        if not self.controller.is_running or not self.controller.current_exercise:
            self.exercise_label.config(text="DONE"); return
        plan_item = self.controller.workout_plan[self.controller.current_plan_index]
        self.exercise_label.config(text=plan_item['exercise'].upper())
        self.reps_label.config(text=f"{self.controller.current_exercise.get_counter()} / {plan_item['reps']}")
        self.sets_label.config(text=f"Set {self.controller.current_set_in_plan} of {plan_item['sets']}")
        self.stage_label.config(text=f"STAGE: {self.controller.current_exercise.get_stage()}")
    def confirm_end_workout(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to end this workout?"):
            self.controller.end_workout()
    def start_video(self):
        if not self.video_loop_active: self.video_loop_active = True; self.update_frame()
    def stop_video(self):
        self.video_loop_active = False