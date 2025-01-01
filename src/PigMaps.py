from UsefulMath import UMath
from ModelHandler import ModelHandler
from Print import Print
import cv2  # Import cv2 for image manipulation and display

class PigMaps:
    def __init__(self):
        self.umath = UMath()
        self.model_handler = ModelHandler()  # Use ModelHandler instance for detections
        self.model_handler_behavior = ModelHandler("yolo11.pt")
        self.behavior = None
        self.frame_count = 0  # Initialize frame count

    def detect_behavior(self, img):
        self.frame_count += 1
        """
        Detect pig behaviors like drinking or pooping based on proximity (IoU) and movement angle.
        Returns detections and behavior information, along with coordinates for drawing.
        """
        # Get detections from the YOLO model
        detections = self.model_handler.get_detections(img)
        
        # Filter and sort detections based on confidence and center (if needed)
        pigs = sorted(self.model_handler.get_pig_detection(detections), key=lambda x: x[2], reverse=True)
        faucets = sorted(self.model_handler.get_faucet_detection(detections), key=lambda x: (x[2], x[1]), reverse=True)  # Sort by confidence, then by center
        feces = sorted(self.model_handler.get_feces_detection(detections), key=lambda x: (x[2], x[1]), reverse=True)  # Sort by confidence, then by center
        
        # Resize the bounding boxes for faucets
        resized_faucets = []
        for faucet in faucets:
            class_name, bbox, confidence = faucet
            resized_bbox = self.umath.resize_bbox(160, bbox)  # 100% increase in size
            resized_faucets.append((class_name, resized_bbox, confidence))
        
        # Use the resized faucets for further processing
        faucets = resized_faucets

        print("resized faucets: " , faucets)

        # Select top detections
        top_pig = pigs[:1]  # Highest confidence pig
        top_faucets = faucets[:2]  # Up to 2 faucets with highest confidence
        top_feces = feces[:1]  # Highest confidence feces

        movement_vector = (0, 0)  # Default movement vector if no pigs are detected
        # self.do_drinking_detection(img,top_pig,faucet)

        # Process each pig detection
        if top_pig:  # Only process if there are pigs detected
            for pig in top_pig:  # Only process the pig with the highest confidence
                pig_id, pig_box, pig_confidence = pig
                pig_center = self.umath.get_center(pig_box)

                prev_center = self.umath.get_prev_center(pig_id)
                movement_vector = self.umath._calculate_movement_vector(pig_id, prev_center, pig_center)
                
                # Detect behaviors based on interaction with faucets
                self._detect_pig_behavior(img, pig_center, pig_box, movement_vector, top_faucets, pig_confidence, pig_id)
                # self.umath.update_prev_movement_vector(movement_vector, pig_center, pig_id)

        # Return filtered detections and behavior details
        return top_faucets, top_feces, top_pig, movement_vector, self.behavior

    def _detect_pig_behavior(self, img, pig_center, pig_box, movement_vector, faucets, pig_confidence, pig_id):
        """Detect drinking behavior by checking IoU, movement vector magnitude, and using the behavior model."""
        for faucet in faucets:
            faucet_box = faucet[1]
            faucet_center = self.umath.get_center(faucet_box)
            # Calculate behavior criteria for drinking
            iou = self.umath.calculate_iou(pig_box, faucet_box)
            dot_product = self.umath.calculate_dot_product(
                movement_vector, (faucet_center[0] - pig_center[0], faucet_center[1] - pig_center[1])
            )
            is_standing = self.umath.is_standing(pig_id, movement_vector)
            
            Print.print_detection_requirements(iou, dot_product, is_standing, pig_confidence)
            if iou > 0.0035 and is_standing == True and pig_confidence > 0.45:
                # Crop the image to the pig's bounding box for behavior detection
                results = self.model_handler_behavior.get_detections(img)
                
                # # Annotate the cropped image with detection results
                # annotated_img = img.copy()
                # for result in results:
                #     class_name, bbox, confidence = result
                #     x1, y1, x2, y2 = map(int, bbox)
                #     color = (0, 255, 0) if class_name == "Drinking" else (0, 0, 255)  # Green for Drinking, Red for others
                #     cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)
                #     cv2.putText(annotated_img, f"{class_name}: {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # # Show the annotated image and wait for input
                # cv2.imshow('Cropped Pig Behavior Detection', annotated_img)
                # cv2.waitKey(0)  # Wait indefinitely for a key press
                # cv2.destroyAllWindows()
                
                # Check if drinking is detected with sufficient confidence
                drinking_detected = False
                for result in results:
                    class_name, _, confidence = result
                    if class_name == "Drinking" and confidence > 0.85:
                        drinking_detected = True
                    elif class_name == "Idle" and confidence >= 0.5:  # If idle is detected with equal or higher confidence, we don't consider it drinking
                        drinking_detected = False
                        break
                
                if drinking_detected:
                    self.behavior = "Drinking"
                    break  # No need to check other faucets once drinking behavior is detected
               
            self.behavior = "Idle"
            # print(self.behavior)
            # cv2.waitKey(0)


    def do_drinking_detection(self, img, best_pig_detection, best_faucet_detection):
        model1_drinking_detected = False
        model2_drinking_detected = False

        print("do_drinking: best pig: ", best_pig_detection)
        for faucet in best_faucet_detection:
            faucet_name, faucet_box, faucet_confidence = faucet

            for pig in best_pig_detection:
                pig_id, pig_box, pig_confidence = pig

                # Calculate IOU and Movement vector magnitude
                iou = self.umath.calculate_iou(pig_box, faucet_box)
                prev_center = self.umath.get_prev_center(pig_id)
                pig_center = self.umath.get_center(pig_box)
                movement_vector = self.umath._calculate_movement_vector(pig_id, prev_center, pig_center)
                is_standing = self.umath.is_standing(pig_id, movement_vector)

                # Print.print_do_detection_requirements(iou, is_standing, pig_confidence, faucet_confidence)
                
                # Model 1 check
                if iou > 0.0035 and is_standing == True and pig_confidence > 0.45 and faucet_confidence > 0.80:
                    model1_drinking_detected = True

                    results = self.model_handler_behavior.get_detections(img)
                    
                    # Check if model 2 drinking is detected with sufficient confidence
                    model2_drinking_detected = False
                    for result in results:
                        class_name, _, confidence = result
                        if class_name == "Drinking" and confidence > 0.85:
                            model2_drinking_detected = True
                        elif class_name == "Idle" and confidence >= 0.5:  # If idle is detected with equal or higher confidence, we don't consider it drinking
                            model2_drinking_detected = False
                            break
                    
                    if model2_drinking_detected:
                        self.behavior = "Drinking"
                        break  # No need to check other pigs for this faucet if drinking is detected

                self.umath.update_prev_movement_vector(movement_vector, pig_center, pig_id)

            # If we've broken out of the inner loop due to drinking detection, we don't need to continue checking other faucets
            if self.behavior == "Drinking":
                break

        # If no drinking was detected, set behavior to Idle
        if self.behavior != "Drinking":
            self.behavior = "Idle"

        print("Model 1:", model1_drinking_detected, "  Model2:", model2_drinking_detected)
        cv2.waitKey(0)

        # Assuming you want to return the last pig and faucet checked or the one where drinking was detected
        print(self.behavior)
        return model1_drinking_detected, model2_drinking_detected, pig_confidence, faucet_confidence, self.behavior