import math

def calculate_angle(p1, p2, p3):
    """
    Calculates the angle formed by three points (p1, p2, p3), where p2 is the vertex.
    Points are lists or tuples of [id, x, y].
    Returns angle in degrees.
    """
    # Get the coordinates
    x1, y1 = p1[1:]
    x2, y2 = p2[1:]
    x3, y3 = p3[1:]

    # Calculate the angle using atan2
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    # Ensure the angle is positive
    if angle < 0:
        angle += 360
    
    # Normalize to the smaller angle 
    if angle > 180:
        angle = 360 - angle
        
    return angle