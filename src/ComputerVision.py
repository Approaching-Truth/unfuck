import cv2
import numpy as np

class Draw:
    def __init__(self):
        # Define standardized colors and font properties
        self.colors = {
            "Pig-standing": (0, 255, 0),
            "Pig-laying": (100,100,100),
            "Water-faucets": (0, 0, 255),
            "feces": (100, 0, 255),
            "behavior": (255, 0, 0),
            "vector": (0, 255, 0),
            "dot_product": (255, 0, 255),
            "movement_cone": (255, 255, 0),
        }
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_thickness = 2

    def draw_movement_cone(self, img, pig_center, direction_angle, radius=70, angle_range=(-55, 55)):
        """
        Visualizes a movement cone originating from the pig's center.
        
        Args:
            img: The image to draw on.
            pig_center: Coordinates (x, y) of the pig's center.
            direction_angle: The orientation angle of the cone in degrees.
            radius: The radius of the cone's ellipse.
            angle_range: Start and end angles of the cone's arc relative to the direction_angle.
        """
        axes = (radius, radius)
        start_angle, end_angle = angle_range
        cv2.ellipse(
            img, pig_center, axes, direction_angle, start_angle, end_angle, self.colors["movement_cone"], 2

        )
    def draw_movement_vector(self, img, pig_center, movement_vector, scale=1):
        """
        Draws an arrow representing the movement vector originating from the pig's center.
        
        Args:
            img: The image to draw on.
            pig_center: Coordinates (x, y) of the pig's center.
            movement_vector: The movement vector as a tuple (dx, dy) representing the movement direction.
            scale: A factor to scale the vector's length for better visualization.
        """
        # Scale the movement vector
        vector_end = (int(pig_center[0] + movement_vector[0] * scale), 
                      int(pig_center[1] + movement_vector[1] * scale))
        
        # Draw the arrow on the image
        cv2.arrowedLine(img, pig_center, vector_end, self.colors["vector"], 3)
        
        return img

    def visualize_vectors(self, img, pig_center, faucet_center, dot_product):
        """
        Depicts the vector from a pig to a faucet and annotates it with the dot product.
        
        Args:
            img: The image to draw on.
            pig_center: Coordinates (x, y) of the pig's center.
            faucet_center: Coordinates (x, y) of the faucet's center.
            dot_product: The computed dot product to be displayed.
        """
        # Ensure the pig and faucet centers are not the same
        if pig_center != faucet_center:
            cv2.arrowedLine(img, pig_center, faucet_center, self.colors["vector"], 2)
            text_position = (faucet_center[0] + 10, faucet_center[1] - 10)
            cv2.putText(
                img, f"Dot Product: {dot_product:.2f}", text_position,
                self.font, self.font_scale, self.colors["dot_product"], self.font_thickness
            )
        return img  # Return the modified image


    def draw_detection_box(self, img, detections, behavior=None):
        """
        Draws bounding boxes on the image for each detection.
        
        Args:
            img (ndarray): The image to draw on.
            detections (list): A list of detections where each detection is a tuple (class_name, bbox, confidence).
            behavior (str): Optional string describing the object's behavior (e.g., "Drinking").
        
        Returns:
            img (ndarray): The image with bounding boxes drawn.
        """
        for detection in detections:  # Iterate over all detections
            class_name, bbox, conf = detection  # Unpack the detection tuple
            color = self.colors[class_name] 
            x1, y1, x2, y2 = map(int, bbox)  # Convert bounding box coordinates to integers

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # Annotate with class name and confidence
            label = f"{class_name} ({conf:.2f})"
            cv2.putText(
                img, label, (x1, y1 - 10),
                self.font, self.font_scale, color, self.font_thickness
            )

            # Annotate behavior if specified
            if class_name in ["Pig-laying", "Pig-standing"]:
                if behavior:
                    cv2.putText(
                        img, behavior, (x1, y1 - 25),
                        self.font, self.font_scale, self.colors["behavior"], self.font_thickness
                    )
        
        return img
    def draw_lucas_kanade_flow(self, img, prev_img, detections):
        """
        Draws Lucas-Kanade optical flow for detected pigs with reduced arrow density.

        Args:
            img (ndarray): Current frame image.
            prev_img (ndarray): Previous frame image for optical flow calculation.
            detections (list): List of pig detections where each detection is a tuple (class_name, bbox, confidence).

        Returns:
            ndarray: Image with smoother optical flow vectors drawn.
        """
        # Convert images to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.cvtColor(prev_img, cv2.COLOR_BGR2GRAY)

        # Parameters for Lucas-Kanade optical flow, adjusted for smoother results
        lk_params = dict(winSize=(21, 21), maxLevel=2, 
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        feature_params = dict(maxCorners=30, qualityLevel=0.3, minDistance=15, blockSize=7)  # Fewer points, more spread out

        # Only process 'Pig-standing' for now, assuming these are moving
        pigs = [detection for detection in detections if detection[0] == "Pig-standing"]

        for pig in pigs:
            bbox = pig[1]
            x1, y1, x2, y2 = map(int, bbox)
            pig_center = ((x1 + x2) // 2, (y1 + y2) // 2)

            # Define ROI for optical flow around the pig
            roi_padding = 75
            x1_roi, y1_roi = max(0, pig_center[0] - roi_padding), max(0, pig_center[1] - roi_padding)
            x2_roi, y2_roi = min(img.shape[1], pig_center[0] + roi_padding), min(img.shape[0], pig_center[1] + roi_padding)

            # Get ROI in grayscale
            roi_gray = gray[y1_roi:y2_roi, x1_roi:x2_roi]
            prev_roi_gray = prev_gray[y1_roi:y2_roi, x1_roi:x2_roi]

            # Find corners in the ROI for tracking with fewer, better quality points
            p0 = cv2.goodFeaturesToTrack(roi_gray, mask=None, **feature_params)

            if p0 is not None and len(p0) > 0:
                p0 = np.float32(p0).reshape(-1, 1, 2)
                p0[:, :, 0] += x1_roi  # Adjust coordinates to full image space
                p0[:, :, 1] += y1_roi

                # Calculate optical flow
                p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, p0, None, **lk_params)

                # Select good points and apply some smoothing
                good_new = p1[st == 1]
                good_old = p0[st == 1]

                # Draw optical flow tracks with reduced density
                for i, (new, old) in enumerate(zip(good_new, good_old)):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    # Scale down the vector length for visualization
                    scale = 0.5
                    vector_end = (int(a + (a - c) * scale), int(b + (b - d) * scale))
                    cv2.arrowedLine(img, (int(a), int(b)), vector_end, self.colors["vector"], 1)

        return img