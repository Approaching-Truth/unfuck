import os
from CSV import CSVLogger
from VideoProcessor import VideoProcessor



def create_output_folder(input_path, output_base):
    """Create the output folder based on the input path."""
    folder_name = os.path.basename(input_path) + "Data"
    output_folder = os.path.join(output_base, folder_name)
    os.makedirs(output_folder, exist_ok=True)
    print(f"Output folder created at: {output_folder}")
    return output_folder

def process_video_files_in_directory(input_path, output_folder, args):
    """Process all video files in a given directory."""
    video_files = [f for f in os.listdir(input_path)
                   if os.path.isfile(os.path.join(input_path, f)) and f.lower().endswith(('.mp4', '.avi', '.mov'))]
    
    for i, video_file in enumerate(video_files):
        csv_filename = f"{i + 1}_of_{len(video_files)}.csv"
        video_path = os.path.join(input_path, video_file)
        
        # Initialize CSV logger for this video
        logger = CSVLogger(output_folder, csv_filename)
        VideoProcessor.process_video(video_path, args, logger)

def process_single_video(input_path, output_base, args):
    """Process a single video file and create the output folder."""
    parent_folder = os.path.basename(os.path.dirname(input_path))
    file_name = os.path.splitext(os.path.basename(input_path))[0]
    output_folder = os.path.join(output_base, f"{parent_folder}-{file_name}Data")
    
    os.makedirs(output_folder, exist_ok=True)
    print(f"Output folder created at: {output_folder}")
    
    csv_filename = f"{file_name}.csv"
    logger = CSVLogger(output_folder, csv_filename)
    VideoProcessor.process_video(input_path, args, logger)
   

def handle_video_input(input_path, args):
    """Main function to handle input path (file or directory) and initiate video processing."""
    print(f"Handling input path: {input_path}")
    
    # Normalize the input path for consistent formatting
    input_path = os.path.normpath(input_path)
    output_base = os.getcwd()  # Get the current working directory 

    if os.path.isdir(input_path):
        # Handle directory of videos
        print("Processing directory...")
        output_folder = create_output_folder(input_path, output_base)
        process_video_files_in_directory(input_path, output_folder, args)

    elif os.path.isfile(input_path):
        # Handle single video file
        print("Processing single video file...")
        process_single_video(input_path, output_base, args)

    else:
        print(f"Error: {input_path} is not a valid file or folder.")
