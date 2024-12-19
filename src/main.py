
from pigParser import Parser
from mediaHandler import MediaHandler

# Parse the command line arguments
args = Parser().parse_args()

# Extract the video path and other arguments
input_path = args.video_source

# Handle video input (either folder or single video)
media = MediaHandler()
media.handle_video_input(input_path, args)
