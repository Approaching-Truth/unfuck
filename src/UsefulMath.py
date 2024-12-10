import math

class UMath:
    def __init__(self, movement_threshold=22, standing_threshold=10):
        self.MOVEMENT_THRESHOLD = movement_threshold
        self.STANDING_THRESHOLD = standing_threshold  # Threshold for standing still
        self.prev_movement_vector = {}
        self.pig_prev_centers = {}

    def distance_2d(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y1 - y2) ** 2)

    def calculate_iou(self, box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area_box1 + area_box2 - intersection

        return intersection / union if union > 0 else 0

    def _calculate_movement_vector(self, pig_id, prev_center, pig_center):
        distance = self.distance_2d(prev_center, pig_center)
        if distance > self.MOVEMENT_THRESHOLD:
            movement_vector = (pig_center[0] - prev_center[0], pig_center[1] - prev_center[1])
        else:
            movement_vector = self.prev_movement_vector.get(pig_id, (0, 0))
        return movement_vector 

    def calculate_dot_product(self, vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def calculate_angle(self, vector1, vector2):
        dot_product = self.calculate_dot_product(vector1, vector2)
        magnitude_v1 = math.sqrt(vector1[0]**2 + vector1[1]**2)
        magnitude_v2 = math.sqrt(vector2[0]**2 + vector2[1]**2)
        if magnitude_v1 * magnitude_v2 == 0:
            return 0
        return math.acos(dot_product / (magnitude_v1 * magnitude_v2))

    def get_center(self, detection):
        x_center = (detection[0] + detection[2]) // 2
        y_center = (detection[1] + detection[3]) // 2
        return int(x_center), int(y_center)

    def get_prev_center(self, pig_id):
        # Initialize tracking if not already done for this pig
        if pig_id not in self.pig_prev_centers:
            self.pig_prev_centers[pig_id] = (0, 0)  # Default value for pigs that are not being tracked yet
        return self.pig_prev_centers.get(pig_id, (0, 0))

    def calculate_movement_magnitude(self, movement_vector):
        """Calculate the magnitude (length) of the movement vector."""
        return math.sqrt(movement_vector[0]**2 + movement_vector[1]**2)

    def is_standing(self, pig_id, movement_vector):
        """Check if the pig is standing still based on the comparison of current and previous movement vectors."""
        
        prev_vector = self.prev_movement_vector.get(pig_id, (0, 0))  # Get previous movement vector
        prev_magnitude = self.calculate_movement_magnitude(prev_vector)  # Magnitude of the previous vector
        current_magnitude = self.calculate_movement_magnitude(movement_vector)  # Magnitude of the current vector

        # Check if the difference in magnitudes is below a certain threshold
        print(f"Prev Magnitude: {prev_magnitude}, Current Magnitude: {current_magnitude}")

        if abs(prev_magnitude - current_magnitude) < self.STANDING_THRESHOLD:
            return True  # Standing still if the change in magnitude is small
        return False

    def calculate_area_of_bbox(self, bbox):
        """
        Calculate the area of a bounding box.

        Args:
            bbox (list or tuple): A bounding box represented by [x_min, y_min, x_max, y_max].        
        Returns:
            float: The area of the bounding box.
        """
        x_min, y_min, x_max, y_max = bbox
        width = x_max - x_min
        height = y_max - y_min
        return width * height
    def update_prev_movement_vector(self, movement_vector, pig_center, pig_id):
        """Update the previous movement vector after checking for standing."""
        self.prev_movement_vector[pig_id] = movement_vector
        self.pig_prev_centers[pig_id] = pig_center


