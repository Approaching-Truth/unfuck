
from pigParser import Parser
import mediaHandler

# Parse the command line arguments
args = Parser().parse_args()

# Extract the video path and other arguments
input_path = args.video_path

# Handle video input (either folder or single video)
mediaHandler.handle_video_input(input_path, args)
