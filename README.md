```markdown
# Pig Movement Detection with YOLO

This project uses a pre-trained YOLOv8 model to detect pig behavior (e.g., drinking, pooping) in videos by analyzing the proximity between pigs and other objects such as water faucets or feces. The program processes video frames to identify objects, draw bounding boxes, and label the detected behaviors.

## Features
- Detects pigs, water faucets, and feces in the video.
- Identifies pig behaviors like drinking and pooping based on proximity to specific objects.
- Provides options to:
  - Adjust the number of frames per second to process (`--fps`).
  - Convert the output video to grayscale (`--grayscale`).
- Uses the YOLOv5 object detection model for predictions.

## Requirements

- Python 3.x
- OpenCV
- NumPy
- Ultralitycs YOLOv5
- argparse

You can install the required libraries using the following:

```bash
pip install opencv-python-headless numpy ultralytics argparse
```

## Usage

### Command-Line Arguments

- `video_path`: Path to the video file that you want to process (e.g., `video.mp4`).
- `--fps`: Number of frames per second to process. Default is 1 (process every frame).
- `--grayscale`: Optional flag to convert the output video to grayscale.
- `--heatmap`: Optional flag to overlay a heatmap on the output video.g

### Example

To run the program, use the following command:

```bash
python PigMaps.py video.mp4 --fps 2 --heatmap
```

This will process the `video.mp4`, process every 2nd frame, and convert the output to grayscale.

## How It Works

1. **Loading the YOLO Model**: The model (`Model_20_02_2024_V17Nano.pt`) is loaded using the `YOLO` class from the `ultralytics` library.
   
2. **Prediction**: The model predicts objects (such as pigs, water faucets, and feces) within each video frame.
   
3. **Behavior Detection**: The proximity between pigs and water faucets or feces is calculated. If the distance is below a specified threshold, it is classified as "Drinking" or "Pooping."

4. **Bounding Boxes & Labels**: Bounding boxes are drawn around the detected objects, and behavior labels like "Behavior: Drinking" or "Behavior: Pooping" are added to the frames.

5. **Output**: The processed video is displayed frame-by-frame with the annotations.

## File Structure

```plaintext
├── PigMaps.py  # Main script for processing the video
├── Model_20_02_2024_V17Nano.pt  # Pre-trained YOLOv5 model
└── README.md               # This documentation
```

## Example Output

While running, the program will show the video with bounding boxes around detected objects and behavior annotations such as:

- **Pig-laying**: Bounding box around a pig that is laying down.
- **Pig-standing**: Bounding box around a pig that is standing.
- **Behavior: Drinking**: Label when the pig is close to a water faucet.
- **Behavior: Pooping**: Label when the pig is near feces.

## Troubleshooting

- **Error: Could not open video**: Ensure the path to the video file is correct.
- **Slow performance**: Try lowering the FPS using the `--fps` argument to process fewer frames.

## License

This project is licensed under the MIT License.

```

