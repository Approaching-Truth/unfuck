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
import pigParser
from Heatmap import Heatmap
from pigParser import Parser
import Grayscale


args = Parser().parse_args()

graph = Graph.BehaviourGraph(csv_file="behavior_log.csv")

# Define classes for detection

# Load model (ensure the model is loaded once)

if __name__ == "__main__":
    # Open the video file
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {args.video_path}")
        exit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(fps)
    process_interval = int(fps / args.fps)  # Only process every Nth frame

    # Initialize heatmap directly if --heatmap argument is passed
    if args.heatmap:
        _, first_frame = cap.read()
        if not _:
            print("Error: Could not read the first frame of the video.")
            exit()
        _, first_frame = cap.read()
        heatmap = Heatmap(first_frame)
        
    frame_count = 0
    while cap.isOpened():
        frame_count += 1
        ret, frame = cap.read()
        if not ret:
            cv2.waitKey(0)
            break

        # Skip frames based on --fps argument
        if frame_count % process_interval != 0:
            continue

        # Perform prediction
        detections = PigMaps.get_detections(frame)
        pigs = PigMaps.get_pig_detection(detections)

        # Detect behaviors based on the predictions and draw bounding boxes
        frame = PigMaps.detect_behavior(frame, detections, frame_count)

        # Heatmap logic
        if args.heatmap:
           heatmap.update(pigs)
        # Normalize the heatmap to a range of 0-255 for better visualization
           heatmap.normalize()
           frame = heatmap.apply_to_frame(frame)


        # Convert to grayscale if required
        if args.grayscale:
            frame = Grayscale.convert_to_grayscale(frame)

        # Show the frame with the detected behaviors
        cv2.imshow("Pig Behavior Detection", frame)

        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    graph.show_plots_separately()