import numpy as np
import cv2

class Overlay:
    def __init__(self, first_frame):
        """
        Initialize the heatmap with the same dimensions as the video frames.
        Args:
            frame_shape (tuple): Shape of the video frame (height, width, channels).
        """
        self.heatmap = np.zeros_like(first_frame, dtype=np.float32)
    
    def get_center(self, box):
        """
        Calculate the center of a bounding box.
        Args:
            box (list): Bounding box in the format [x1, y1, x2, y2].
        Returns:
            tuple: Center of the bounding box (cx, cy).
        """
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return int(cx), int(cy)

    def updateHeatmap(self, pig_detections, radius=5):
        """
        Update the heatmap with new pig detections.
        Args:
            pig_detections (list): List of pig bounding boxes. Each detection is [x1, y1, x2, y2].
            radius (int): Radius around each detected pig's center to increment heatmap values.
        """
        for pig in [det for det in pig_detections if det[0] in ["Pig-laying", "Pig-standing"]]:
            x1, y1, x2, y2 = map(int, pig[1])
            pig_center = self.get_center(pig[1])

            # Define the size of the area to increment (e.g., a 10x10 region around the center)
            heatmap_radius = 10  # You can adjust this value to make the dots larger or smaller
            for dx in range(-heatmap_radius, heatmap_radius + 1):
                for dy in range(-heatmap_radius, heatmap_radius + 1):
                    # Ensure the coordinates are within the frame dimensions
                    cx, cy = pig_center[0] + dx, pig_center[1] + dy
                    if 0 <= cx < self.heatmap.shape[1] and 0 <= cy < self.heatmap.shape[0]:
                        self.heatmap[cy, cx] += 1

    def normalizeHeatmap(self):
        """
        Normalize the heatmap to the range 0-255 for visualization.
        Returns:
            np.ndarray: Normalized heatmap.
        """
        if np.max(self.heatmap) > 0:
            return np.uint8(np.clip(self.heatmap / np.max(self.heatmap) * 255, 0, 255))
        return np.zeros_like(self.heatmap, dtype=np.uint8)

    def apply_to_frame(self, frame, alpha=0.7):
        """
        Overlay the heatmap onto a video frame.
        Args:
            frame (np.ndarray): The video frame.
            alpha (float): Opacity of the heatmap overlay.
        Returns:
            np.ndarray: Frame with heatmap overlay.
        """
        heatmap_display = cv2.applyColorMap(self.normalizeHeatmap(), cv2.COLORMAP_JET)
        heatmap_display = cv2.resize(heatmap_display, (frame.shape[1], frame.shape[0]))

        return  cv2.addWeighted(frame, alpha, heatmap_display, 1 - alpha, 0)

    
    
    def convert_to_grayscale(self, frame):
        """
        Convert a video frame to grayscale.

        Args:
            frame (np.ndarray): The input video frame.

        Returns:
            np.ndarray: The grayscale version of the input frame.
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def apply_overlay(self, pigs, frame, args):
        if args.heatmap:
            self.updateHeatmap(pigs)
            frame = self.apply_to_frame(frame)
        if args.grayscale:
            frame = self.convert_to_grayscale(frame)
        return frame
