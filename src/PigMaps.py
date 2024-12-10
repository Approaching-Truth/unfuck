import cv2

from ultralytics import YOLO
import math
class PigMaps:
    classes = {0: 'Keeper', 1: 'Pig-laying', 2: 'Pig-standing', 3: 'Water-faucets', 4: 'feces'}
    chosen_model = YOLO("Model_20_02_2024_V17Nano.pt")  # Replace with the actual model path

<<<<<<< Updated upstream

    def predict(self,chosen_model, img, conf=0.30):
=======
    def detect_behavior(self, img):
        self.frame_count += 1
>>>>>>> Stashed changes
        """
        Predict the classes of objects in an image using the YOLO model.
        """
        results = chosen_model.predict(img, conf=conf)
        return results

    def get_center(self,detection):
        """Compute the center of a bounding box."""
        x_center = (detection[0] + detection[2]) // 2
        y_center = (detection[1] + detection[3]) // 2
        return int(x_center), int(y_center)

    def distance_2d(self,point1, point2):
        """Compute the Euclidean distance between two points."""
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y1 - y2) ** 2)

    def calculate_iou(self,box1, box2):
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area_box2 = (box2[2] - box2[0]) * (box2[3] - box1[1])
        union = area_box1 + area_box2 - intersection

        return intersection / union if union > 0 else 0

    def draw_bounding_and_behavior_box(self,img, bbox, label, behavior=None, color=(0, 255, 0)):
        """
        Draw a bounding box and annotate it with a label and optional behavior.
        
        Args:
            img: The image to draw on.
            bbox: Bounding box coordinates (x1, y1, x2, y2).
            label: Text label for the object.
            behavior: Optional behavior to annotate (e.g., "Drinking").
            color: Color for the bounding box and text.
        """
        x1, y1, x2, y2 = map(int, bbox)

        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

<<<<<<< Updated upstream
        # Draw label above the bounding box
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # If behavior is provided, annotate it
        if behavior:
            cv2.putText(img, behavior, (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    def detect_behavior(self, img, detections, frame_number,logger):

        """
        Detect pig behaviors like drinking or pooping based on proximity (distance) between pigs and water faucets/feces.
        """
        pigs = [det for det in detections if det[0] in ["Pig-laying", "Pig-standing"]]
        faucets = [det for det in detections if det[0] == "Water-faucets"]
        feces = [det for det in detections if det[0] == "feces"]

        # Draw bounding boxes and labels for all detected objects
        for det in detections:
            class_name, bbox = det
            color = (0, 255, 0) if class_name in ["Pig-laying", "Pig-standing"] else (0, 0, 255)
            self.draw_bounding_and_behavior_box(img, bbox, class_name, color=color)

        # Detect behaviors based on proximity (distance threshold)
        for pig in pigs:
            pig_box = pig[1]  # Get the bounding box for the pig
            pig_center = self.get_center(pig_box)

            for faucet in faucets:
                faucet_box = faucet[1]
                faucet_center = self.get_center(faucet_box)
                # If the pig and faucet are close enough, consider it as "Drinking"
                if self.calculate_iou(pig_box, faucet_box) > 0:
                    # Behavior detected: Drinking
                    behavior_text = "Behavior: Drinking"
                    # Log the behavior with frame number and timestamp
                    logger.log_behavior(frame_number, "Drinking", pig_center)
                    # Annotate the bounding box with behavior
                    self.draw_bounding_and_behavior_box(img, pig_box, "Pig", behavior=behavior_text)

        return img
=======
        movement_vector = (0, 0)  # Default movement vector if no pigs are detected

        # Process each pig detection
        if top_pig:  # Only process if there are pigs detected
            for pig in top_pig:  # Only process the pig with the highest confidence
                pig_id, pig_box, pig_confidence = pig
                pig_center = self.umath.get_center(pig_box)

                prev_center = self.umath.get_prev_center(pig_id)
                movement_vector = self.umath._calculate_movement_vector(pig_id, prev_center, pig_center)
                print("conf: " , pig_confidence)
                # Detect behaviors based on interaction with faucets
                self._detect_pig_behavior(pig_center, pig_box, movement_vector, top_faucets, pig_confidence, pig_id)
                self.umath.update_prev_movement_vector(movement_vector,pig_center, pig_id)

        # Return filtered detections and behavior details
        return top_faucets, top_feces, top_pig, movement_vector, self.behavior

>>>>>>> Stashed changes


    def get_detections(self, img):
        """
        Extract and filter pig detections from model results.

        Args:
            results (list): List of results from the model prediction.
            model (YOLO model): The trained YOLO model to extract class names.
            target_classes (list): List of classes to filter, defaults to ["Pig-laying", "Pig-standing"].

<<<<<<< Updated upstream
        Returns:
            list: A list of detections for the specified pig classes.
        """
        results = self.predict(self.chosen_model,img)
        detections = [
            (self.chosen_model.names[int(box.cls[0])], box.xyxy[0].tolist())
            for result in results
            for box in result.boxes
        ]
        return detections

    def get_pig_detection(self,detections,target_classes=["Pig-laying", "Pig-standing"]):
        # Filter detections for pigs
        pigs = [det for det in detections if det[0] in target_classes]
        
        return pigs
=======
    def _detect_pig_behavior(self, pig_center, pig_box, movement_vector, faucets, pig_confidence, pig_id):
        """Detect drinking and pooping behavior by checking IoU and movement angle with faucets."""
        for i, faucet in enumerate(faucets):
            faucet_box = faucet[1]
            faucet_center = self.umath.get_center(faucet_box)
            # Calculate behavior criteria for drinking
            iou = self.umath.calculate_iou(pig_box, faucet_box)
            dot_product = self.umath.calculate_dot_product(
                movement_vector, (faucet_center[0] - pig_center[0], faucet_center[1] - pig_center[1])
            )
            area = self.umath.calculate_area_of_bbox(pig_box)
            is_standing = self.umath.is_standing(pig_id, movement_vector)
            print(self.umath.calculate_area_of_bbox(pig_box))
            print(f"center: {pig_center} dot: {dot_product} iou: {iou} is standing: {is_standing} faucet_{i} conf: {faucet[2]} " )

            if iou > 0.0001 and dot_product >= 600 and is_standing and area < 16900 and pig_confidence > 0.75:

                self.behavior = "Drinking"
                break  # No need to check other faucets once drinking behavior is detected
            self.behavior = None
>>>>>>> Stashed changes
