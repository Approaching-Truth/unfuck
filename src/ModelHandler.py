from ultralytics import YOLO
import sys, os

class ModelHandler:
    def __init__(self):
        self.chosen_model = YOLO("Model_20_02_2024_V17Nano.pt")  # Replace with the actual model path
        self.conf = 0.30  # Confidence threshold

    def get_detections(self, img):
        """
        Extract and filter detections from the YOLO model, including confidence scores.

        Args:
            img (ndarray): Input image to be processed by the model.

        Returns:
            list: A list of tuples containing the class name, bounding box coordinates, and confidence score.
        """
        sys.stdout = open(os.devnull, 'w')

        results = self.chosen_model.predict(img, self.conf,verbose =False)
        sys.stdout = sys.__stdout__

        detections = [
            (self.chosen_model.names[int(box.cls[0])], box.xyxy[0].tolist(), box.conf[0].item())
            for result in results
            for box in result.boxes
        ]
        return detections

    def get_pig_detection(self, detections, target_classes=["Pig-laying", "Pig-standing"]):
        # Filter detections for pigs
        pigs = [det for det in detections if det[0] in target_classes]
        return pigs
    
    def get_faucet_detection(self, detections, target_classes=["Water-faucets"]):
        # Filter detections for pigs
        faucet = [det for det in detections if det[0] in target_classes]
        return faucet
    def get_feces_detection(self, detections, target_classes=["feces"]):
        # Filter detections for pigs
        faucet = [det for det in detections if det[0] in target_classes]
        return faucet
