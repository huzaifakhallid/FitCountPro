class BaseExercise:

    def __init__(self):
        self.counter = 0
        self.stage = None # Can be 'up', 'down', etc. depending on exercise
        self.name = "Base Exercise" # Should be overridden by subclasses

    def process_landmarks(self, landmarks):

        raise NotImplementedError("This method should be overridden by a subclass.")

    def get_counter(self):
        return self.counter

    def get_stage(self):
        return self.stage if self.stage is not None else "START"

    def reset(self):
        """Resets the counter and stage for a new set."""
        self.counter = 0
        self.stage = None