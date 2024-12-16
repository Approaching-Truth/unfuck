class Print:
    @staticmethod
    def print_error(message):
        """
        Print an error message.
        """
        print(f"Error: {message}")

    @staticmethod
    def print_info(message):
        """
        Print an informational message.
        """
        print(f"Info: {message}")

    @staticmethod
    def print_debug(message):
        """
        Print a debug message.
        """
        print(f"Debug: {message}")

    @staticmethod
    def print_behavior_detected(frame_count, behavior, pig_id=None):
        """
        Print a message when a behavior is detected.
        """
        if pig_id is not None:
            print(f"Frame {frame_count}: {behavior} detected for Pig ID {pig_id}.")
        else:
            print(f"Frame {frame_count}: {behavior} detected.")

    @staticmethod
    def print_detection_requirements(iou, dot_product, is_standing, pig_confidence):
        """
        Print the detection criteria for pig behavior.
        """
        print(f"IoU: {iou}")
        print(f"Dot Product: {dot_product}")
        print(f"Is Standing: {is_standing}")
        print(f"Pig Confidence: {pig_confidence}")
