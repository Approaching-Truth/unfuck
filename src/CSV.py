import csv
import time

class CSVLogger:
    def __init__(self, filename="behavior_log.csv"):
        self.filename = filename
        self.initialize_csv()

    def initialize_csv(self):
        """Create or reset the CSV file with headers."""
        try:
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Frame", "Behavior", "Center(x,y)"])
        except Exception as e:
            print(f"Error initializing CSV: {e}")

    def log_behavior(self, frame, behavior, distance=None):
        """Log a detected behavior to the CSV file."""
        # Get the current timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # If distance is not provided, set it to an empty string or a default value
        distance = distance if distance is not None else ""

        # Log behavior details to the CSV file
        try:
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, frame, behavior, distance])
        except Exception as e:
            print(f"Error logging behavior: {e}")

# Usage example:
# logger = CSVLogger()
# logger.log_behavior(42, "Drinking", 75.2)
