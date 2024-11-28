class Print:
    def print_error(message):
        """
        Print an error message.
        """
        print(f"Error: {message}")


    def print_info(message):
        """
        Print an informational message.
        """
        print(f"Info: {message}")


    def print_debug(message):
        """
        Print a debug message.
        """
        print(f"Debug: {message}")


    def print_behavior_detected(frame_count, behavior, pig_id=None):
        """
        Print a message when a behavior is detected.
        """
        if pig_id is not None:
            print(f"Frame {frame_count}: {behavior} detected for Pig ID {pig_id}.")
        else:
            print(f"Frame {frame_count}: {behavior} detected.")
