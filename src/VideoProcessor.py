from PigMaps import PigMaps
from Overlay import Overlay
from FrameHandler import FrameHandler
from ComputerVision import Draw
from UsefulMath import UMath
from mqtt import MQTT
import yaml
import cv2  # Add this import for image processing

class VideoProcessor:
    def process_video(video_path, args, logger, i):
        frameHandler = FrameHandler(video_path)
        initialFrame = 0
        frame, _ = frameHandler.get_frame(args.fps, initialFrame)
        process_interval = int(frameHandler.get_fps() / args.fps)  # Only process every Nth frame
        pigMaps = PigMaps()
        overlay_handler = Overlay(frame)
        draw = Draw()
        umath = UMath()
        frame_count = initialFrame
        mqtt = MQTT()
        additionalSeconds = 0
        out_path = f"/home/aevery/Documents/unfuck/Potential_Drinking{i}"

        logger_initialized = False  # Flag to track if loggerMessage has been initialized
        config_file_path = 'src/config.yaml'  # Ensure this is the correct path

        # Load config
        try:
            with open(config_file_path, 'r') as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            # If the file doesn't exist, initialize with an empty list
            config = {'confusion': {'predicted': []}}
        
        # Ensure 'predicted' is always a list
        if 'confusion' not in config:
            config['confusion'] = {}
        if 'predicted' not in config['confusion']:
            config['confusion']['predicted'] = []
        elif not isinstance(config['confusion']['predicted'], list):
            # If 'predicted' is not a list, convert it to one
            config['confusion']['predicted'] = [config['confusion']['predicted']]
        
        # Append a new segment (0) to y_pred at the start of each video or segment
        config['confusion']['predicted'].append(0)
        
        # Save the updated config back to the file
        with open(config_file_path, 'w') as file:
            yaml.dump(config, file)

        prev_frame = None  # Keep track of the previous frame

        while frameHandler.cap.isOpened():
            frame, frame_count = frameHandler.get_frame(args.fps, frame_count)
         
            if frame is None:
                break

            # Skip frames based on --fps argument
            if frame_count % process_interval != 0:
                continue

            # Store current frame as previous frame for next iteration
            if prev_frame is None:
                prev_frame = frame.copy()
            else:
                # Assuming pigMaps.detect_behavior returns filtered top detections
                faucets, feces, pig, movement_vector, behavior2 = pigMaps.detect_behavior(frame)
                model1, model2, confpig, conffau, behavior =pigMaps.do_drinking_detection(frame,pig,faucets)
                
                # Get center coordinates
                pig_center = umath.get_center(pig[0][1]) if pig else None
                faucet_centers = [umath.get_center(f[1]) for f in faucets] if faucets else []

                # Safely unpack faucet centers with default values for missing entries
                faucet_1 = faucet_centers[0] if len(faucet_centers) > 0 else None
                faucet_2 = faucet_centers[1] if len(faucet_centers) > 1 else None
                feces_center = umath.get_center(feces[0][1]) if feces else None
                if movement_vector and faucet_1 and pig_center:
                    dot1 = umath.calculate_dot_product(
                        movement_vector, (faucet_1[0] - pig_center[0], faucet_1[1] - pig_center[1])
                    )
                else:
                    dot1 = None

                if movement_vector and faucet_2 and pig_center:
                    dot2 = umath.calculate_dot_product(
                        movement_vector, (faucet_2[0] - pig_center[0], faucet_2[1] - pig_center[1])
                    )
                else:
                    dot2 = None

                if behavior:
                    # Update the last entry in y_pred to 1 if drinking detected
                    config['confusion']['predicted'][-1] = 1
                    # Save the updated config to reflect the new value
                    config_file_path = 'src/config.yaml'  # Use the same path as when loading
                    with open(config_file_path, 'w') as file:
                        yaml.dump(config, file)
                    # frameHandler.save_img_to_folder(out_path,frame, frame_count)
                    additionalSeconds += 72

                # Initialize logger message only once when behavior starts
                if behavior and not logger_initialized:
                    logger.loggerMessage = {
                        "start_frame": frame_count,  # Set start frame when behavior starts
                        "end_frame": None,
                        "behavior": behavior,
                        "class": [],
                        "confidence": [],
                        "coordinates": {
                            "faucet1": faucet_1,  # Store faucet 1 center
                            "faucet2": faucet_2,  # Store faucet 2 center
                            "feces": feces_center,  # Store feces center
                            "pig": pig_center  # Store pig center
                        }
                    }
                    logger_initialized = True  # Mark loggerMessage as initialized

                    # Extract classes and confidence scores
                    if pig:
                        logger.loggerMessage["class"].append("pig")
                        logger.loggerMessage["confidence"].append(pig[0][2])  # Confidence of the top pig

                    # Append Faucet detections
                    for i, faucet in enumerate(faucets):
                        logger.loggerMessage["class"].append(f"faucet{i+1}")  # faucet1, faucet2, etc.
                        logger.loggerMessage["confidence"].append(faucet[2])  # Confidence of each faucet

                    # Append Feces detection
                    if feces:
                        logger.loggerMessage["class"].append("feces")
                        logger.loggerMessage["confidence"].append(feces[0][2])  # Confidence of the top feces

                # If behavior ends (i.e., pig stops drinking), log the behavior
                if logger_initialized and not behavior and logger.loggerMessage["start_frame"] is not None and frame_count > logger.loggerMessage["start_frame"] + additionalSeconds:
                    # Set the end frame when behavior stops and log the behavior
                    logger.loggerMessage["end_frame"] = frame_count
                    logger.log_behavior(logger.loggerMessage)
                    mqtt.publish_drinking(logger.loggerMessage.get("behavior"))
                    
                    # Reset logger initialization for the next behavior
                    logger_initialized = False
                    logger.loggerMessage["start_frame"] = None
                    logger.loggerMessage["end_frame"] = None
                    additionalSeconds = 0

                # Draw the detection boxes on the frame
                frame = draw.draw_detection_box(frame, faucets)
                frame = draw.draw_detection_box(frame, feces)
                frame = draw.draw_detection_box(frame, pig, behavior)

                # Draw Lucas-Kanade vectors
                if pig:  # Only draw vectors if there's at least one pig detected
                    frame = draw.draw_lucas_kanade_flow(frame, prev_frame, pig)
                # Apply overlay (if any)
                frame = overlay_handler.apply_overlay(pig, frame, args)

                # Show the processed frame
                frameHandler.showFrame(frame, args.headless)

                # Update prev_frame for next iteration
                prev_frame = frame.copy()

                # Check for exit key
                if frameHandler.check_for_key_press():
                    break

            # Update frame for next iteration
            prev_frame = frame.copy()
        
        # Release the frame handler after processing
        frameHandler.release()
        # overlay_handler.plot_3d_heatmap()
