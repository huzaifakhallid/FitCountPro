from .base_exercise import BaseExercise
from tracker.angle_utils import calculate_angle

class Pushups(BaseExercise):
    def __init__(self):
        super().__init__()
        self.name = "Pushups"
        self.stage = "up" # Start in the 'up' position

    def process_landmarks(self, landmarks):
        try:
            # Landmarks for right arm: 12 (shoulder), 14 (elbow), 16 (wrist)
            shoulder = landmarks[12]
            elbow = landmarks[14]
            wrist = landmarks[16]

            angle = calculate_angle(shoulder, elbow, wrist)
            
            # Pushup logic
            if self.stage == 'up' and angle < 90:
                self.stage = "down"
            elif self.stage == 'down' and angle > 160:
                self.stage = "up"
                self.counter += 1

        except (IndexError, TypeError):
            self.stage = "NO PERSON"