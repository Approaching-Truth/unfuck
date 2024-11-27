import cv2

def convert_to_grayscale(frame):
    """
    Convert a video frame to grayscale.

    Args:
        frame (np.ndarray): The input video frame.

    Returns:
        np.ndarray: The grayscale version of the input frame.
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)