from .base_exercise import BaseExercise
from tracker.angle_utils import calculate_angle

class BicepCurls(BaseExercise):
    def __init__(self):
        super().__init__()
        self.name = "Bicep Curls"
        self.stage = "down" # Start with arm extended

    def process_landmarks(self, landmarks):
        try:
            # Landmarks for right arm: 12 (shoulder), 14 (elbow), 16 (wrist)
            shoulder = landmarks[12]
            elbow = landmarks[14]
            wrist = landmarks[16]

            angle = calculate_angle(shoulder, elbow, wrist)

            # Bicep curl logic
            if self.stage == 'down' and angle < 40:
                self.stage = "up"
            elif self.stage == 'up' and angle > 160:
                self.stage = "down"
                self.counter += 1
        
        except (IndexError, TypeError):
            self.stage = "NO PERSON"