import cv2
import numpy as np
import argparse
from collections import deque
from ultralytics import YOLO
import math
import os
import CSV  # Import the CSV logging module
import Graph  # Import Graph module for behavior visualization
import pigParser

csv_logger = CSV.CSVLogger()  # Adjust the log file name if needed
classes = {0: 'Keeper', 1: 'Pig-laying', 2: 'Pig-standing', 3: 'Water-faucets', 4: 'feces'}
chosen_model = YOLO("Model_20_02_2024_V17Nano.pt")  # Replace with the actual model path


def predict(chosen_model, img, conf=0.30):
    """
    Predict the classes of objects in an image using the YOLO model.
    """
    results = chosen_model.predict(img, conf=conf)
    return results

def get_center(detection):
    """Compute the center of a bounding box."""
    x_center = (detection[0] + detection[2]) // 2
    y_center = (detection[1] + detection[3]) // 2
    return int(x_center), int(y_center)

def distance_2d(point1, point2):
    """Compute the Euclidean distance between two points."""
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y1 - y2) ** 2)

def calculate_iou(box1, box2):
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

def draw_bounding_and_behavior_box(img, bbox, label, behavior=None, color=(0, 255, 0)):
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

    # Draw label above the bounding box
    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # If behavior is provided, annotate it
    if behavior:
        cv2.putText(img, behavior, (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

def detect_behavior(img, detections, frame_number, distance_threshold=90):

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
        draw_bounding_and_behavior_box(img, bbox, class_name, color=color)

    # Detect behaviors based on proximity (distance threshold)
    for pig in pigs:
        pig_box = pig[1]  # Get the bounding box for the pig
        pig_center = get_center(pig_box)

        for faucet in faucets:
            faucet_box = faucet[1]
            faucet_center = get_center(faucet_box)
            # If the pig and faucet are close enough, consider it as "Drinking"
            if calculate_iou(pig_box, faucet_box) > 0:
                # Behavior detected: Drinking
                behavior_text = "Behavior: Drinking"
                # Log the behavior with frame number and timestamp
                csv_logger.log_behavior(frame_number, "Drinking", pig_center)
                # Annotate the bounding box with behavior
                draw_bounding_and_behavior_box(img, pig_box, "Pig", behavior=behavior_text)

    return img


def get_detections(img):
    """
    Extract and filter pig detections from model results.

    Args:
        results (list): List of results from the model prediction.
        model (YOLO model): The trained YOLO model to extract class names.
        target_classes (list): List of classes to filter, defaults to ["Pig-laying", "Pig-standing"].

    Returns:
        list: A list of detections for the specified pig classes.
    """
    results = predict(chosen_model,img)
    detections = [
        (chosen_model.names[int(box.cls[0])], box.xyxy[0].tolist())
        for result in results
        for box in result.boxes
    ]
    return detections

def get_pig_detection(detections,target_classes=["Pig-laying", "Pig-standing"]):
    # Filter detections for pigs
    pigs = [det for det in detections if det[0] in target_classes]
    
    return pigs
