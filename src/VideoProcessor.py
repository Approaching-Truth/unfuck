from PigMaps import PigMaps
from Overlay import Overlay
from FrameHandler import FrameHandler



class VideoProcessor:
    # Main processing function using the classes above
    def process_video(video_path, args, logger):
        frameHandler = FrameHandler(video_path)
        initialFrame = 0
        frame, _ = frameHandler.get_frame(args.fps, initialFrame)
        process_interval = int(frameHandler.getFps() / args.fps)  # Only process every Nth frame

        pigMaps = PigMaps()
        overlay_handler = Overlay(frame)
        frame_count = initialFrame
        while frameHandler.cap.isOpened():
            if frame is None:
                print("here")
                break
            frame, frame_count = frameHandler.get_frame(args.fps, frame_count)
                # Skip frames based on --fps argument
            if frame_count % process_interval != 0:
                continue

            detections = pigMaps.get_detections(frame)
            pigs = pigMaps.get_pig_detection(detections)
            frame = pigMaps.detect_behavior(frame, detections, frame_count, logger)

            frame = overlay_handler.apply_overlay(pigs, frame, args)

            frameHandler.showFrame(frame, args.headless)
            if frameHandler.check_for_exit_key():
                break
        
        frameHandler.release()
