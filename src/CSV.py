import csv
import time
import os

class CSVLogger:
    def __init__(self, output_folder, filename="behavior_log.csv"):
        self.filename = os.path.join(output_folder, filename)  # Ensure full path
        self.initialize_csv()

    def initialize_csv(self):
        """Create or reset the CSV file with headers."""
        try:
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Frame", "Behavior", "Center(x,y)"])
            print(f"CSV initialized at: {self.filename}")
        except Exception as e:
            print(f"Error initializing CSV: {e}")

    def log_behavior(self, frame_count, behavior, center=None):
        """Log a detected behavior to the CSV file."""
        # Get the current timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # If center is not provided, set it to an empty string or default
        center = center if center is not None else ""

        # Log behavior details to the CSV file
        try:
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, frame_count, behavior, center])
            print(f"Logged behavior at frame {frame_count} to CSV.")
        except Exception as e:
            print(f"Error logging behavior: {e}")
