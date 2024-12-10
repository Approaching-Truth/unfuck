import cv2
import os

# Video Processor Class: Manages video capture and display
class FrameHandler:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Error: Could not open video {video_path}")
        self.manual_control = False  # Flag to control whether to manually step through the video
        self.video_name = os.path.basename(video_path)  # Extract video name from the path

    def get_frame(self, process_interval, frame_count):
        ret, frame = self.cap.read()
        if not ret:
            return None, frame_count
        return frame, frame_count + 1

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def showFrame(self, frame, headless):
        if not headless:
            # Set the window title to the video name
            cv2.imshow(f"Pig Behavior Detection - {self.video_name}", frame)

    def check_for_key_press(self):
        """
        Check if 'q' key has been pressed to exit, or if 'b' key has been pressed to move to the next frame.
        Also checks for 'm' key to toggle manual control.
        Returns:
            bool: True if 'q' key is pressed to exit, False otherwise.
        """
        key = cv2.waitKey(1) & 0xFF
        if self.manual_control:
            key = cv2.waitKey(0) & 0xFF

        # Check for exit key (q)
        if key == ord('q'):
            return True  # Exit the loop

        # Toggle manual control with 'm' key
        if key == ord('m'):
            self.toggle_manual_control()
            print(f"Manual control {'enabled' if self.manual_control else 'disabled'}")
            return False  # Do not exit the loop

        # Check for manual control (b to go to next frame)
        if self.manual_control and key == ord('b'):
            return False  # Move to the next frame when 'b' is pressed
        
        return False

    def toggle_manual_control(self):
        """
        Toggle the manual control flag (enable/disable).
        """
        self.manual_control = not self.manual_control

    def get_fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)  # Corrected to return the FPS value
