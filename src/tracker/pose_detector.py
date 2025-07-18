import cv2
import mediapipe as mp

class PoseDetector:
    """
    MediaPipe Pose detector class.
    Encapsulates finding and drawing pose landmarks.
    """
    def __init__(self, detection_con=0.5, track_con=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=detection_con, min_tracking_confidence=track_con)
        self.mp_draw = mp.solutions.drawing_utils

    def find_pose(self, img, draw=True):
        """Finds pose landmarks in an image and draws them."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return img

    def get_landmarks(self, img):
        """Extracts landmark coordinates from the detected pose."""
        landmarks = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                # Get pixel coordinates
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append([id, cx, cy])
        return landmarks