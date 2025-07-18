from tracker.angle_utils import calculate_angle

class SquatCounter:
    def __init__(self):
        self.counter = 0
        self.stage = "up"  # Initial stage

    def process(self, landmarks):
        """
        Processes landmarks to count squats.
        landmarks: A list of [id, x, y] coordinates.
        """
        try:
            # MediaPipe landmarks for right leg: 24 (hip), 26 (knee), 28 (ankle)
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]

            # Calculate the angle of the knee
            angle = calculate_angle(hip, knee, ankle)
            
            # Squat counting logic
            if angle > 160:
                self.stage = "up"
            
            # Check for a full rep: went from "up" to "down"
            if angle < 90 and self.stage == 'up':
                self.stage = "down"
                self.counter += 1
                print(f"Squat Count: {self.counter}") # For debugging
        
        except IndexError:
            # This can happen if a required landmark is not visible
            pass