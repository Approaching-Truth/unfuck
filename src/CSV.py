import os
import csv

class CSVLogger:
    def __init__(self, output_folder, filename, log_full_day=False):
        self.filename = os.path.join(output_folder, filename)  # Ensure full path
        self.init = True
        self.inBehavior = False
        self.loggerMessage = {}
        
        # If the flag is set, also log to full day CSV
        self.log_full_day = log_full_day
        self.fullday_initialized = False  # Track whether full-day CSV is initialized
        
        if self.log_full_day:
            # Set the path for the full-day CSV
            self.fullday_filename = os.path.join(output_folder, "fullday.csv")

    def initialize_csv(self, classes, is_full_day=False):
        """Create or reset the CSV file with headers, only if the file doesn't exist."""
        try:
            # Define the columns for the individual video CSV
            header = ["Start-frame", "End-Frame", "start-time-min", "end-time-min", "Behavior", 
                      "Pig-Center",  "Pig Conf","Faucet-1-Center", "Faucet-1-conf", "Faucet-2-Center", "Faucet-2-conf", 
                      "Feces-Center", "Feces-conf"]
            
            # Choose the appropriate filename
            filename = self.fullday_filename if is_full_day else self.filename

            # Check if the file exists and if it contains the header
            if not os.path.exists(filename):
                # Initialize the file if it doesn't exist
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                print(f"CSV initialized at: {filename}")
            else:
                # Check if it already has the header
                with open(filename, mode='r') as file:
                    first_line = file.readline()
                    if first_line.strip() != ",".join(header):
                        # If no header or different header, write the header
                        with open(filename, mode='w', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(header)
                        print(f"CSV header initialized or reset at: {filename}")

            # Initialize only if the full-day file hasn't been initialized yet
            if is_full_day and not self.fullday_initialized:
                self.fullday_initialized = True  # Mark full-day CSV as initialized

        except Exception as e:
            print(f"Error initializing CSV: {e}")

    def log_behavior(self, loggerMessage):
        """Log the behavior details from a loggerMessage to the CSV file."""
        start_frame = loggerMessage.get("start_frame", "")
        end_frame = loggerMessage.get("end_frame", "")
        behavior = loggerMessage.get("behavior", "")
        classes = loggerMessage.get("class", [])
        confidences = loggerMessage.get("confidence", [])
        coordinates = loggerMessage.get("coordinates", {})  # Added for faucet/feces centers

        # If the CSV file hasn't been initialized yet, initialize it
        if self.init:
            self.initialize_csv(classes)
            if self.log_full_day:
                self.initialize_csv(classes, is_full_day=True)
            self.init = False

        # Default empty values for each class
        pig_conf = ""
        pig_coord = ""  # Added for pig coordinates
        faucet1_coord, faucet1_conf = "", ""
        faucet2_coord, faucet2_conf = "", ""
        feces_coord, feces_conf = "", ""

        # Loop over each class and populate the respective coordinate and confidence values
        for i, cls in enumerate(classes):
            if cls == "pig" and len(confidences) > 0:
                pig_conf = confidences[0]
                pig_coord = f"({coordinates.get('pig', (0, 0))[0]},{coordinates.get('pig', (0, 0))[1]})"  # Store pig coordinates
            elif cls == "faucet1" and len(confidences) > 1:
                faucet1_coord = f"({coordinates.get('faucet1', (0, 0))[0]},{coordinates.get('faucet1', (0, 0))[1]})"
                faucet1_conf = confidences[1]
            elif cls == "faucet2" and len(confidences) > 2:
                faucet2_coord = f"({coordinates.get('faucet2', (0, 0))[0]},{coordinates.get('faucet2', (0, 0))[1]})"
                faucet2_conf = confidences[2]
            elif cls == "feces" and len(confidences) > 3:
                feces_coord = f"({coordinates.get('feces', (0, 0))[0]},{coordinates.get('feces', (0, 0))[1]})"
                feces_conf = confidences[3]

        # Calculate the drinking duration in minutes (assuming 24 FPS)
        if start_frame and end_frame:
            drinking_duration = (end_frame - start_frame) / 24.0 / 60.0  # Duration in minutes

        # Calculate the start time in minutes (start_frame / 24 FPS)
        start_time_minutes = start_frame / 24.0 / 60.0
        end_time_minutes = end_frame / 24.0 / 60.0


        # Write the behavior to the individual video CSV with separated values for each class
        try:
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([start_frame, end_frame, start_time_minutes, end_time_minutes, behavior,  drinking_duration, pig_coord, pig_conf] + 
                                [faucet1_coord, faucet1_conf, 
                                faucet2_coord, faucet2_conf, feces_coord, feces_conf])
            print(f"Logged behavior at frame {start_frame} to CSV.")
            
            # If logging full day, also append to the full-day CSV
            if self.log_full_day:
                with open(self.fullday_filename, mode='a', newline='') as full_file:
                    writer = csv.writer(full_file)
                    writer.writerow([start_frame, end_frame, start_time_minutes, end_time_minutes, behavior, drinking_duration, pig_coord, pig_conf] + 
                                    [faucet1_coord, faucet1_conf, 
                                    faucet2_coord, faucet2_conf, feces_coord, feces_conf])
                print(f"Logged behavior at frame {start_frame} to Full-day CSV.")

        except Exception as e:
            print(f"Error logging behavior: {e}")
