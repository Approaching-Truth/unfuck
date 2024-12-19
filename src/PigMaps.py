
from UsefulMath import UMath
from ModelHandler import ModelHandler
from Print import Print

class PigMaps:
    def __init__(self):
        self.umath = UMath()
        self.model_handler = ModelHandler()  # Use ModelHandler instance for detections
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

        # Select top detections
        top_pig = pigs[:1]  # Highest confidence pig
        top_faucets = faucets[:2]  # Up to 2 faucets with highest confidence
        top_feces = feces[:1]  # Highest confidence feces

        movement_vector = (0, 0)  # Default movement vector if no pigs are detected


        # Code to overwrite top_faucets using set_bbox_parameters (uncomment if needed)
        # config_path = "src/config.yaml"  # Path to your YAML configuration file

        # # Fetch bounding boxes from config
        # left_faucet_bbox = self.umath.set_bbox_parameters(config_path, "faucet_left")
        # right_faucet_bbox = self.umath.set_bbox_parameters(config_path, "faucet_right")

        # left_faucet_bbox = self.umath.resize_bbox(10, left_faucet_bbox)
        # right_faucet_bbox = self.umath.resize_bbox(10,right_faucet_bbox)

        # # Replace top_faucets with the new values
        # top_faucets = [
        #     ("Water-faucets", left_faucet_bbox, 99),
        #     ("Water-faucets", right_faucet_bbox, 99)
        # ]


        # Process each pig detection
        if top_pig:  # Only process if there are pigs detected
            for pig in top_pig:  # Only process the pig with the highest confidence
                pig_id, pig_box, pig_confidence = pig
                pig_center = self.umath.get_center(pig_box)

                prev_center = self.umath.get_prev_center(pig_id)
                movement_vector = self.umath._calculate_movement_vector(pig_id, prev_center, pig_center)
                #print("conf: " , pig_confidence)
                # Detect behaviors based on interaction with faucets
                self._detect_pig_behavior(pig_center, pig_box, movement_vector, top_faucets, pig_confidence, pig_id)
                self.umath.update_prev_movement_vector(movement_vector, pig_center, pig_id)

        # Return filtered detections and behavior details
        return top_faucets, top_feces, top_pig, movement_vector, self.behavior




    

    def _detect_pig_behavior(self, pig_center, pig_box, movement_vector, faucets, pig_confidence,pig_id):
        """Detect drinking and pooping behavior by checking IoU and movement angle with faucets."""
        for faucet in faucets:
            faucet_box = faucet[1]
            faucet_center = self.umath.get_center(faucet_box)
            # Calculate behavior criteria for drinking
            iou = self.umath.calculate_iou(pig_box, faucet_box)
            dot_product = self.umath.calculate_dot_product(
                movement_vector, (faucet_center[0] - pig_center[0], faucet_center[1] - pig_center[1])
            )
            area = self.umath.calculate_area_of_bbox(pig_box)
            is_standing = self.umath.is_standing(pig_id, movement_vector)
            #print(self.umath.calculate_area_of_bbox(pig_box))
            #print(f"center: {pig_center} dot: {dot_product} iou: {iou} is standing: {is_standing}" )
            Print.print_detection_requirements(iou, dot_product, is_standing, pig_confidence)
            if iou > 0.0035  and is_standing and pig_confidence > 0.45 and dot_product >= 600 :
                
                self.behavior = "Drinking"
                break  # No need to check other faucets once drinking behavior is detected
            self.behavior = None


