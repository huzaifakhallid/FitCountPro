from tracker.angle_utils import calculate_angle

class SquatCounter:
    def __init__(self, angle_threshold_down=90, angle_threshold_up=160):
        self.counter = 0
        self.stage = "up"  # Initial stage
        self.angle = 0
        
        self.angle_threshold_down = angle_threshold_down
        self.angle_threshold_up = angle_threshold_up
        
        print(f"SquatCounter initialized with thresholds: DOWN < {self.angle_threshold_down}, UP > {self.angle_threshold_up}")

    def process(self, landmarks):

        try:
            # MediaPipe landmarks for right leg: 24 (hip), 26 (knee), 28 (ankle)
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]

            # Calculate the angle of the knee
            self.angle = calculate_angle(hip, knee, ankle)
            
            # State machine for squat counting
            if self.stage == "up" and self.angle < self.angle_threshold_down:
                # Transition from UP to DOWN
                self.stage = "down"
            
            elif self.stage == "down" and self.angle > self.angle_threshold_up:
                # Transition from DOWN to UP, completing a rep
                self.stage = "up"
                self.counter += 1
                print(f"Squat Count: {self.counter}") # Debugging
        
        except (IndexError, TypeError):
            # This can happen if landmarks are not visible or are None
            self.stage = "no_person"