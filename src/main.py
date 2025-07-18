import cv2
from tracker.pose_detector import PoseDetector
from exercises.squats import SquatCounter

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    detector = PoseDetector()
    squat_counter = SquatCounter()

    while True:
        success, img = cap.read()
        if not success:
            break
        
        img = cv2.flip(img, 1)
        img = detector.find_pose(img, draw=False) 
        landmarks = detector.get_landmarks(img)

        if landmarks:
            # Process squats
            squat_counter.process(landmarks)

            # Display Reps and Stage
            cv2.putText(img, f"Reps: {squat_counter.counter}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(img, f"Stage: {squat_counter.stage}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Draw the pose landmarks over the text
        img = detector.find_pose(img, draw=True)

        cv2.imshow("FitCount Pro - Squat Counter", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()