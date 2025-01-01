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
        Print the detection criteria for pig behavior from _detect_pig_behavior function.
        """
        print(f"Behavior Detection Criteria:")
        print(f"  IoU: {iou:.4f}")
        print(f"  Dot Product: {dot_product:.4f}")
        print(f"  Is Standing: {is_standing}")
        print(f"  Pig Confidence: {pig_confidence:.4f}")
    @staticmethod
    def print_do_detection_requirements(iou, is_standing, pig_confidence, faucet_confidence):
        """
        Print the detection criteria for pig behavior from do_drinking_detection function.
        """
        print(f"Do Detection Criteria:")
        print(f"  IoU: {iou:.4f}")
        print(f"  Is Standing: {is_standing}")
        print(f"  Pig Confidence: {pig_confidence:.4f}")
        print(f"  Faucet Confidence: {faucet_confidence:.4f}")