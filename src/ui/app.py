import tkinter as tk
import cv2
from PIL import Image, ImageTk

class FitCountProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FitCount Pro - AI Fitness Tracker")
        self.geometry("1280x720")
        self.configure(bg="#2E2E2E")  # Dark background

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        #label to display the video feed
        self.video_label = tk.Label(self)
        self.video_label.pack(padx=10, pady=10)

        #video update loop
        self.update_frame()
        
        #window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_frame(self):
        """Continuously updates the video feed in the Tkinter label."""
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1) # Flip for selfie view

            # Convert the image from OpenCV BGR format to PIL RGB format
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            
            # Convert the PIL image to a PhotoImage object that Tkinter can display
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Update the video label with the new image
            self.video_label.imgtk = img_tk
            self.video_label.configure(image=img_tk)
        
        # Schedule the next update
        self.after(10, self.update_frame)

    def on_closing(self):
        """Release resources when the window is closed."""
        print("Closing application...")
        self.cap.release()
        self.destroy()