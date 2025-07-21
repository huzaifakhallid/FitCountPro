from .base_exercise import BaseExercise
from tracker.angle_utils import calculate_angle

class Squats(BaseExercise):
    def __init__(self):
        super().__init__()
        self.name = "Squats"
        self.stage = "up" # Start in the 'up' position

    def process_landmarks(self, landmarks):
        try:
            # MediaPipe landmarks for right leg: 24 (hip), 26 (knee), 28 (ankle)
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]

            angle = calculate_angle(hip, knee, ankle)
            
            # State machine for squat counting
            if self.stage == "up" and angle < 90:
                self.stage = "down"
            elif self.stage == "down" and angle > 160:
                self.stage = "up"
                self.counter += 1
                print(f"Squat Count: {self.counter}")
        
        except (IndexError, TypeError):
            self.stage = "NO PERSON"