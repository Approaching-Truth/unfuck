import cv2
import numpy as np
import argparse
from collections import deque
from ultralytics import YOLO
import math
import os
import CSV  # Import the CSV logging module
import Graph  # Import Graph module for behavior visualization

# Parser for command-line arguments
parser = argparse.ArgumentParser(description='Process a video for pig movement detection.')
parser.add_argument('video_path', type=str, help='Path to the video file.')
parser.add_argument('--fps', type=int, default=1, help='Number of frames per second to process.')
parser.add_argument('--grayscale', action='store_true', help='Convert the output video to grayscale.')
parser.add_argument('--heatmap', action='store_true', help='Enable heatmap generation for pig movement.')
args = parser.parse_args()

# Define classes for detection
classes = {0: 'Keeper', 1: 'Pig-laying', 2: 'Pig-standing', 3: 'Water-faucets', 4: 'feces'}

# Load model (ensure the model is loaded once)
chosen_model = YOLO("Model_20_02_2024_V17Nano.pt")  # Replace with the actual model path

# Initialize CSV logger
csv_logger = CSV.CSVLogger("behavior_log.csv")  # Adjust the log file name if needed
graph = Graph.BehaviourGraph(csv_file="behavior_log.csv")


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


def detect_behavior(img, detections, frame_number, distance_threshold=90):
    """
    Detect pig behaviors like drinking or pooping based on proximity (distance) between pigs and water faucets/feces.
    Also draw bounding boxes around the detected objects.
    """
    pigs = [det for det in detections if det[0] in ["Pig-laying", "Pig-standing"]]
    faucets = [det for det in detections if det[0] == "Water-faucets"]
    feces = [det for det in detections if det[0] == "feces"]

    # Draw bounding boxes and labels for all detected objects
    for det in detections:
        class_name, bbox = det
        x1, y1, x2, y2 = map(int, bbox)  # Convert coordinates to integers for drawing

        # Draw bounding box
        color = (0, 255, 0) if class_name in ["Pig-laying", "Pig-standing"] else (0, 0, 255)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        # Add text label
        cv2.putText(img, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Detect behaviors based on proximity (distance threshold)
    for pig in pigs:
        pig_box = pig[1]  # Get the bounding box for the pig
        pig_center = get_center(pig_box)

        for faucet in faucets:
            faucet_box = faucet[1]
            faucet_center = get_center(faucet_box)

            # Calculate Euclidean distance between the centers of the pig and faucet
            distance = distance_2d(pig_center, faucet_center)

            # If the pig and faucet are close enough, consider it as "Drinking"
            if distance < distance_threshold:
                # Behavior detected: Drinking
                text = "Behavior: Drinking"
                # Log the behavior with frame number and timestamp
                csv_logger.log_behavior(frame_number, "Drinking", pig_center)
                # Display the behavior text inside the bounding box or just above it
                cv2.putText(img, text, (int(pig_box[0]), int(pig_box[1] - 25)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        for feces_box in feces:
            if calculate_iou(pig_box, feces_box[1]) > 0.5:
                # Behavior detected: Pooping
                text = "Behavior: Pooping"
                # Log the behavior with frame number and timestamp
                csv_logger.log_behavior(frame_number, "Pooping", pig_center)
                # Display the behavior text inside the bounding box or just above it
                cv2.putText(img, text, (int(pig_box[0]), int(pig_box[1] - 25)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return img


if __name__ == "__main__":
    # Open the video file
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {args.video_path}")
        exit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    process_interval = int(fps / args.fps)  # Only process every Nth frame

    # Initialize heatmap if --heatmap argument is passed
    heatmap = None
    if args.heatmap:
        # Create an empty frame for the heatmap (same size as the video frames)
        _, first_frame = cap.read()
        heatmap = np.zeros_like(first_frame, dtype=np.float32)

    frame_count = 0
    while cap.isOpened():
        frame_count += 1
        ret, frame = cap.read()
        if not ret:
            break

        # Skip frames based on --fps argument
        if frame_count % process_interval != 0:
            continue

        # Perform prediction
        results = predict(chosen_model, frame)
        detections = [(chosen_model.names[int(box.cls[0])], box.xyxy[0].tolist())
                      for result in results for box in result.boxes]

        # Detect behaviors based on the predictions and draw bounding boxes
        frame = detect_behavior(frame, detections, frame_count)

        # Heatmap logic
        if args.heatmap:
            for pig in [det for det in detections if det[0] in ["Pig-laying", "Pig-standing"]]:
                x1, y1, x2, y2 = map(int, pig[1])
                pig_center = get_center(pig[1])

                # Define the size of the area to increment (e.g., a 10x10 region around the center)
                heatmap_radius = 10  # You can adjust this value to make the dots larger or smaller
                for dx in range(-heatmap_radius, heatmap_radius + 1):
                    for dy in range(-heatmap_radius, heatmap_radius + 1):
                        # Ensure the coordinates are within the frame dimensions
                        cx, cy = pig_center[0] + dx, pig_center[1] + dy
                        if 0 <= cx < heatmap.shape[1] and 0 <= cy < heatmap.shape[0]:
                            heatmap[cy, cx] += 1

        # Normalize the heatmap to a range of 0-255 for better visualization
        if args.heatmap:
            heatmap_display = np.uint8(np.clip(heatmap / np.max(heatmap) * 255, 0, 255))
            frame = cv2.addWeighted(frame, 0.7, cv2.applyColorMap(heatmap_display, cv2.COLORMAP_JET), 0.3, 0)

        # Convert to grayscale if required
        if args.grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Show the frame with the detected behaviors
        cv2.imshow("Pig Behavior Detection", frame)

        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    graph.show_plots_separately()