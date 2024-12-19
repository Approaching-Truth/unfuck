import argparse

class Parser:
    def __init__(self):
        # Store the ArgumentParser instance in an attribute
        self.parser = argparse.ArgumentParser(description='Process a video for pig movement detection.')
        
        # The video source can now be either a file or a stream URL
        self.parser.add_argument('video_source', type=str, help='Path to the video file or URL for live stream.')
        
        # Optional flag to indicate if the source is a live stream
        self.parser.add_argument('--live', action='store_true', help='Indicate that the video source is a live stream URL.')
        
        self.parser.add_argument('--fps', type=int, default=1, help='Number of frames per second to process.')
        self.parser.add_argument('--grayscale', action='store_true', help='Convert the output video to grayscale.')
        self.parser.add_argument('--heatmap', action='store_true', help='Enable heatmap generation for pig movement.')
        self.parser.add_argument('--headless', action='store_true', help='Run without video')

    def parse_args(self):
        # Call parse_args() on the ArgumentParser instance
        return self.parser.parse_args()