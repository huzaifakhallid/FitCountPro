import cv2
from tracker.pose_detector import PoseDetector

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Initialize pose detector
    detector = PoseDetector()

    while True:
        success, img = cap.read()
        if not success:
            break

        # Flip the image horizontally 
        img = cv2.flip(img, 1)

        # Find and draw the pose
        img = detector.find_pose(img)
        
        #landmarks = detector.get_landmarks(img)
        #if landmarks:
        #    print(landmarks[0]) # Print the nose landmark coordinates

        # Display the image
        cv2.imshow("FitCount Pro - Pose Detection", img)

        # Break 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()