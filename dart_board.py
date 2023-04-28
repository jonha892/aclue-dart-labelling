import math

OUTER_DOUBLE = 170
INNER_DOUBLE = 162
OUTER_TRIPLE = 107
INNER_TRIPLE = 99
OUTER_BULLSEYE = 16
DOUBLE_BULLSEYE = 6.35

DOUBLE_MAX_THRESHOLD = 1
DOUBLE_MIN_THRESHOLD = INNER_DOUBLE / OUTER_DOUBLE

TRIPLE_MAX_THRESHOLD = INNER_TRIPLE / OUTER_DOUBLE
TRIPLE_MIN_THRESHOLD = INNER_TRIPLE / OUTER_DOUBLE

BULLSEYE_MAX_THRESHOLD = OUTER_BULLSEYE / OUTER_DOUBLE
BULLSEYE_MIN_THRESHOLD = DOUBLE_BULLSEYE / OUTER_DOUBLE
DOUBLE_BULLSEYE_MAX_THRESHOLD = DOUBLE_BULLSEYE / OUTER_DOUBLE

def angle_to_base_score(angle):
    """
    Calculates the base score based on the angle of the dart from the center of the board.
    Assumes 0 degrees is 12 o'clock and references the middle ot the 20 field.
    """
    shifted_angle = (angle + 9) % 360
    multiplier = math.floor(shifted_angle / 18)

    scores = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    return scores[multiplier % 20]

def score(p, center, max_radius):
    x, y = p
    # calc clockwise angle from 12 o'clock from center to p
    angle = math.atan2(y - center[1], x - center[0])
    # angle is in radians, convert to degrees
    angle = math.degrees(angle)

    # calc distance from center to p
    distance = math.sqrt((x - center[0])**2 + (y - center[1])**2)

    # normalize distance to max_radius
    normalized_distance = distance / max_radius

    # calc score
    if normalized_distance <= DOUBLE_BULLSEYE_MAX_THRESHOLD:
        return 50, "d25"
    elif normalized_distance <= BULLSEYE_MAX_THRESHOLD:
        return 25, "25"
    
    base_score = angle_to_base_score(angle)
    
    # normal
    if normalized_distance < TRIPLE_MIN_THRESHOLD or \
        normalized_distance > TRIPLE_MAX_THRESHOLD and normalized_distance < DOUBLE_MIN_THRESHOLD:
        return base_score, str(base_score)
    
    # triple
    if normalized_distance >= TRIPLE_MIN_THRESHOLD and normalized_distance <= TRIPLE_MAX_THRESHOLD:
        return base_score * 3, "t" + str(base_score)
    
    if normalized_distance >= DOUBLE_MIN_THRESHOLD and normalized_distance <= DOUBLE_MAX_THRESHOLD:
        return base_score * 2, "d" + str(base_score)
    
    if normalized_distance > DOUBLE_MAX_THRESHOLD:
        return 0, "miss"
    
    raise ValueError("Invalid dart position")
