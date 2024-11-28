import cv2
# Video Processor Class: Manages video capture and display
class FrameHandler:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Error: Could not open video {video_path}")

    def get_frame(self, process_interval, frame_count):
        ret, frame = self.cap.read()
        if not ret:
            return None, frame_count
        return frame, frame_count + 1

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


    def showFrame(self, frame, headless):
        if(not headless):
            cv2.imshow("Pig Behavior Detection", frame)

    def check_for_exit_key(self):
        """
        Check if the 'q' key has been pressed to exit the loop.
        Returns:
            bool: True if 'q' key is pressed, otherwise False.
        """
        return cv2.waitKey(1) & 0xFF == ord('q')
    def getFps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)  # Corrected to return the FPS value


    
            
        