import cv2

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