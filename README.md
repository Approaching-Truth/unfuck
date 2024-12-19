
# Pig Movement Detection with YOLO

This project leverages a pre-trained YOLOv8 model to analyze pig behavior (such as drinking or pooping) in video footage by examining the proximity between pigs and objects like water faucets or feces. The system processes video frames to detect objects, draw bounding boxes around them, and annotate the behaviors observed.

## Features
- Detects pigs, water faucets, and feces within video streams or files.
- Identifies behaviors like drinking and pooping based on the spatial relationship between objects.
- Provides customization options:
  - Adjust the processing frame rate with `--fps`.
  - Convert video output to grayscale using `--grayscale`.
  - Apply a heatmap overlay with `--heatmap`.
- Supports both live video streams and local video files.
- Uses the YOLOv8 model for object detection.

## Requirements

- Python 3.x
- OpenCV
- NumPy
- Ultralytics for YOLOv8
- argparse

Install the necessary libraries with:

```bash
pip install opencv-python-headless numpy ultralytics argparse
```

## Usage
Command-Line Arguments

    video_source: Path to the video file or URL for a live stream.
    --fps: Frames per second to process. Defaults to 1 (every frame).
    --grayscale: Flag to convert the output to grayscale.
    --heatmap: Flag to add a heatmap overlay to the video.
    --live: Indicates if the video source is a live stream.
    --headless: Run without displaying video (useful for background processing).


## Example
To process a video file:

```bash

python main.py video.mp4 --fps 2 --heatmap
```

For a live stream:

```bash

python main.py "rtsp://your_stream_url" --live --fps 1
```

## How It Works

    Loading the YOLO Model: The YOLOv8 model (Model_20_02_2024_V17Nano.pt) is loaded for object detection.
    Frame Acquisition: For video files, frames are read sequentially; for streams, frames are captured as they come.
    Prediction: The model detects objects in each frame (pigs, faucets, feces).
    Behavior Analysis: Calculates proximity, movement vectors, and uses these to determine if behaviors like drinking or pooping are occurring.
    Visualization: Draws bounding boxes, labels behaviors, and optionally applies overlays like heatmaps.
    Output: Displays or saves frames with annotations depending on command-line options.


## File Structure
```bash
├── src/
│   ├── PigMaps.py
│   ├── Overlay.py
│   ├── FrameHandler.py
│   ├── ComputerVision.py
│   ├── UsefulMath.py
│   ├── mqtt.py
│   ├── CSV.py
│   ├── config.yaml
│   ├── mediaHandler.py
│   ├── main.py
│   └── pigParser.py
└── Model_20_02_2024_V17Nano.pt
```




License
This project is licensed under the MIT License.
