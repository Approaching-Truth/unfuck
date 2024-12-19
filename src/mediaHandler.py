import os
from urllib.parse import urlparse
from CSV import CSVLogger
from VideoProcessor import VideoProcessor

class MediaHandler:

    def create_output_folder(self, input_path, output_base):
        """Create the output folder based on the input path."""
        # Use URL's netloc or file's basename for folder naming
        parsed_url = urlparse(input_path)
        if parsed_url.scheme:
            folder_name = parsed_url.netloc or "stream"
        else:
            folder_name = os.path.basename(input_path)
        
        output_folder = os.path.join(output_base, folder_name + "Data")
        os.makedirs(output_folder, exist_ok=True)
        print(f"Output folder created at: {output_folder}")
        return output_folder

    def process_video_files_in_directory(self, input_path, output_folder, args, log_full_day=True):
        """Process all video files in a given directory."""
        video_files = [f for f in os.listdir(input_path)
                       if os.path.isfile(os.path.join(input_path, f)) and f.lower().endswith(('.mp4', '.avi', '.mov'))]
        
        for i, video_file in enumerate(video_files):
            # Use the video file name (without extension) as the CSV filename
            csv_filename = f"{os.path.splitext(video_file)[0]}.csv"
            logger = CSVLogger(output_folder, csv_filename, log_full_day)
            video_path = os.path.join(input_path, video_file)
            
            # Initialize CSV logger for this video, with the log_full_day flag
            VideoProcessor.process_video(video_path, args, logger, i+300)

    def process_single_video(self, input_path, output_base, args):
        """Process a single video file or URL and create the output folder."""
        parsed_url = urlparse(input_path)
        if parsed_url.scheme:
            # For URLs, we use the netloc or a generic name
            file_name = parsed_url.netloc or "stream"
        else:
            # For local files, we use the file name without extension
            file_name = os.path.splitext(os.path.basename(input_path))[0]
        
        output_folder = self.create_output_folder(input_path, output_base)
        
        csv_filename = f"{file_name}.csv"
        logger = CSVLogger(output_folder, csv_filename, args.live)
        VideoProcessor.process_video(input_path, args, logger, i=0 if not args.live else 300)

    def handle_video_input(self, input_path, args):
        """Main function to handle input path (file, directory, or URL) and initiate video processing."""
        print(f"Handling input path: {input_path}")
        
        # No need to normalize URL paths with os.path.normpath
        output_base = os.getcwd()  # Get the current working directory 

        parsed_url = urlparse(input_path)
        if parsed_url.scheme:  # If it's a URL
            print("Processing video stream...")
            self.process_single_video(input_path, output_base, args)
        elif os.path.isdir(input_path):
            print("Processing directory...")
            output_folder = self.create_output_folder(input_path, output_base)
            self.process_video_files_in_directory(input_path, output_folder, args)
        elif os.path.isfile(input_path):
            print("Processing single video file...")
            self.process_single_video(input_path, output_base, args)
        else:
            print(f"Error: {input_path} is not a valid file, folder, or URL.")

