import numpy as np
import matplotlib.pyplot as plt
import math
import copy
import signal
import sys

ARC_DENSITY = 20 # points per unit length
MIN_TURN_RADIUS = 3
class Circle:
    def __init__(self, center, rad):
        self.center = center
        self.rad = rad

# Function to read the CSV data and convert it into a path
def read_csv_data(csv_data):
    path = []
    for line in csv_data.strip().split('\n'):
        x, y = map(int, line.split(','))
        path.append((y, x))
    return path

def distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def angle_between_points(p1, p2, p3):
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)
    ab = b - a
    bc = c - b
    cosine_angle = np.dot(ab, bc) / (np.linalg.norm(ab) * np.linalg.norm(bc))
    return np.arccos(np.clip(cosine_angle, -1.0, 1.0))

def find_midpoint(p1, p2):
    mid = (abs(p1[0] + p2[0]) / 2, abs(p1[1] + p2[1]) / 2)
    return mid

def find_center_and_rad(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # find equation of first line
    if x2-x1 == 0:
        # if vertical line
        m1 = float('inf')

    else:
        m1 = (y2-y1)/(x2-x1)
    
    # find midpoint
    xm1, ym1 = find_midpoint(p1, p2)

    # find equation of line perpendicular to first line
    if m1 == 0:
        # if horizontal slope, perpendicular line is vertical
        perpm1 = float('inf')
        perpb1 = None

    elif m1 == float('inf'):
        # if vertical slope, perpendicular line is horizontal
        perpm1 = 0
        perpb1 = ym1

    else:
        perpm1 = -1 / m1
        perpb1 = ym1 - perpm1 * xm1
    
    
    # do the same for the second line
    if x3-x2 == 0:
        m2 = float('inf')
    else:
        m2 = (y3-y2)/(x3-x2)

    xm2, ym2 = find_midpoint(p2, p3)

    if m2 == 0:
        perpm2 = float('inf')
        perpb2 = None
    elif m2 == float('inf'):
        perpm2 = 0
        perpb2 = ym2
    else:
        perpm2 = -1 / m2
        perpb2 = ym2 - perpm2 * xm2


    # find centerpoint
    if perpm2 - perpm1 == 0:
        return None, None
    
    elif perpm1 == float('inf'):
        # if first perpendicular is vertical
        a = xm1
        b = perpm2 * xm1 + perpb2

    elif perpm2 == float('inf'):
        # if second perpendicular is vertical
        a = xm2
        b = perpm1 * xm2 + perpb1

    else:
        # if both perpendicular lines are valid functions
        a = (perpb2 - perpb1) / (perpm1 - perpm2)
        b = perpm1 * a + perpb1

    # calculate radius
    rad = distance((a, b), p1)

    return (a, b), rad
        
def draw_points_on_circle(circle, point1, point2, point3, density):
    center = circle.center
    radius = circle.rad

    def angle_from_center(center, point):
        # Calculate the angle from the point to the positive x-axis
        return math.atan2(point[1] - center[1], point[0] - center[0])
    
    def interpolate_points(angle_start, angle_end, num_points):
        # Generate points along the arc between angle_start and angle_end
        return [(center[0] + radius * math.cos(angle_start + i * (angle_end - angle_start) / num_points),
                 center[1] + radius * math.sin(angle_start + i * (angle_end - angle_start) / num_points))
                for i in range(num_points + 1)]
    
    # Calculate angles for the three points relative to the center
    angle1 = angle_from_center(center, point1)
    angle2 = angle_from_center(center, point2)
    angle3 = angle_from_center(center, point3)

    # Ensure the angles are in the range [0, 2*pi]
    if angle1 < 0:
        angle1 += 2 * math.pi
    if angle2 < 0:
        angle2 += 2 * math.pi
    if angle3 < 0:
        angle3 += 2 * math.pi

    # Calculate the clockwise and counterclockwise paths
    clockwise_path = (angle2 - angle1) % (2 * math.pi)
    counterclockwise_path = (angle1 - angle2) % (2 * math.pi)

    # Check if point3 is in the clockwise path
    point3_in_clockwise = (angle1 < angle3 < (angle1 + clockwise_path)) or (angle1 + clockwise_path > 2 * math.pi and angle3 < (angle1 + clockwise_path) % (2 * math.pi))

    if point3_in_clockwise:
        num_points = int(clockwise_path * density / (2 * math.pi) * radius)
        points = interpolate_points(angle1, angle1 + clockwise_path, num_points)
    else:
        num_points = int(counterclockwise_path * density / (2 * math.pi) * radius)
        points = interpolate_points(angle2, angle2 + counterclockwise_path, num_points)
        points = points[::-1]  # Reverse to go from point1 to point2

    return points

def adjust_path_for_turn_radius(input_path, min_turn_radius): # TODO
    path = copy.deepcopy(input_path)

    altered_path = [path[0]]
    circles = []
    last_ind = 0
    for i in range(1, len(path) - 1):
        p1 = path[i - 1]
        p2 = path[i]
        p3 = path[i + 1]

        angle = angle_between_points(p1, p2, p3)
        if angle != 0 and angle < np.pi / 2:  # Detect sharp turns
            # find a circle that includes all three points
            center, radius = find_center_and_rad(p1, p2, p3)
            if center is not None and radius < min_turn_radius:
                temp_circle = Circle(center, radius)
                circles.append(temp_circle)
                print("Drawing arc from point: " + str(len(altered_path) - 1))
                # find new points along circle to connect p1 to p3
                new_points = draw_points_on_circle(temp_circle, p1, p3, p2, ARC_DENSITY)
                path[i] = new_points[-1]

                altered_path.extend(new_points)
            else:
                altered_path.append(p2)
        else:
            altered_path.append(p2)
        
        # search for and remove duplicate points
        i = last_ind
        while(i < len(altered_path) - 1):
            if altered_path[i] == altered_path[i+1]:
                altered_path.pop(i)
            else:
                i += 1
        last_ind = i - 1

    altered_path.append(path[-1])

    return altered_path, circles

# Example usage
csv_data = """41,54
40,55
39,55
38,56
37,57
36,58
35,58
34,58
33,58
32,58
31,58
30,59
31,60
32,60
33,60
34,60
35,60
36,60
37,61
38,62
39,63
40,63
41,63
42,63
41,64
"""

# csv_data = """51,57
# 51,59
# 50,60
# 49,61
# 48,62
# 48,63
# 48,64
# 48,65
# """

input_path = read_csv_data(csv_data)

figure, axes = plt.subplots()

altered_path, circles = adjust_path_for_turn_radius(input_path, MIN_TURN_RADIUS)

for circle in circles:
    temp_circle = plt.Circle(circle.center, circle.rad)
    axes.add_artist(temp_circle)

# print("Input Path:", input_path)
# print("Altered Path:", altered_path)

# Plotting for visualization
input_path = np.array(input_path)
altered_path = np.array(altered_path)

plt.plot(input_path[:, 0], input_path[:, 1], 'bo-', label='Input Path')
plt.plot(altered_path[:, 0], altered_path[:, 1], 'ro-', label='Altered Path')

# Annotate the input path points
# for i, (x, y) in enumerate(input_path):
#     plt.annotate(str(i), (x, y), textcoords="offset points", xytext=(5, 5), ha='center')

# Annotate the altered path points
for i, (x, y) in enumerate(altered_path):
    plt.annotate(str(i), (x, y), textcoords="offset points", xytext=(5, 5), ha='center')

plt.legend()
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Path Adjustment for Minimum Turn Radius')
plt.show()