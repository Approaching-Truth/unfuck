import cv2
import numpy as np
import argparse
from collections import deque
from ultralytics import YOLO
import math
import os
import CSV  # Import the CSV logging module
import Graph  # Import Graph module for behavior visualization
import PigMaps

# Parser for command-line arguments
parser = argparse.ArgumentParser(description='Process a video for pig movement detection.')
parser.add_argument('video_path', type=str, help='Path to the video file.')
parser.add_argument('--fps', type=int, default=1, help='Number of frames per second to process.')
parser.add_argument('--grayscale', action='store_true', help='Convert the output video to grayscale.')
parser.add_argument('--heatmap', action='store_true', help='Enable heatmap generation for pig movement.')
parser.add_argument('--folder', type=str, help='Runs script on folder')
args = parser.parse_args()
graph = Graph.BehaviourGraph(csv_file="behavior_log.csv")

# Define classes for detection
classes = {0: 'Keeper', 1: 'Pig-laying', 2: 'Pig-standing', 3: 'Water-faucets', 4: 'feces'}

# Load model (ensure the model is loaded once)
chosen_model = YOLO("Model_20_02_2024_V17Nano.pt")  # Replace with the actual model path

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
        results = PigMaps.predict(chosen_model, frame)
        detections = [(chosen_model.names[int(box.cls[0])], box.xyxy[0].tolist())
                      for result in results for box in result.boxes]

        # Detect behaviors based on the predictions and draw bounding boxes
        frame = PigMaps.detect_behavior(frame, detections, frame_count)

        # Heatmap logic
        if args.heatmap:
            for pig in [det for det in detections if det[0] in ["Pig-laying", "Pig-standing"]]:
                x1, y1, x2, y2 = map(int, pig[1])
                pig_center = PigMaps.get_center(pig[1])

                # Define the size of the area to increment (e.g., a 10x10 region around the center)
                heatmap_radius = 5  # You can adjust this value to make the dots larger or smaller
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
            #cv2.imshow("heatmap",frame)


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