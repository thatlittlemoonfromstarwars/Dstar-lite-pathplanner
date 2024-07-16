import numpy as np
import matplotlib.pyplot as plt
import math
import copy

ARC_DENSITY = 1 # number of points along each arc for every 10 degrees (or 0.1745 radians)

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
    print("Center: " + str((a,b)) + " Rad: " + str(rad))

    return (a, b), rad

def get_points_along_rad(circle, p1, p2, arc_density):
    # draws points along the given section of the circle

    points = [p1]

    center = circle.center
    rad = circle.rad

    cx = center[0]
    cy = center[1]

    # find angle from p1 to p2
    angle = angle_between_points(p1, center, p2)

    # determine the number of points based on the specified arc density
    num_points = round(angle * arc_density / 0.1745) # 0.1745 radians ≈ 10 degrees

    # calculate the incremental angle between each point
    sub_angle = angle / num_points
    temp_angle = sub_angle

    angle_from_p1_to_y_axis = angle_between_points(p1, center, (center[0], 1))
    if angle_from_p1_to_y_axis > np.pi / 2:
        angle_from_p1_to_y_axis = np.pi - angle_from_p1_to_y_axis
    
    angle_from_p1_to_x_axis = np.pi / 4 - angle_from_p1_to_y_axis

    # iterate to calculate each point along the arc
    while temp_angle < angle:
        # calculate x coordinate relative to center
        delta_x = rad * math.cos(temp_angle)
        if p1[0] > cx and p2[0] > cx: # fully in quadrant 1 or 4 (where origin is center)
            x = cx + delta_x
        elif p1[0] < cx and p2[0] < cx: # fully in quadrant 2 or 3 
            x = cx - delta_x
        else: # starts and ends on different sides of the y-axis
            if temp_angle < angle_from_p1_to_y_axis: # point left of y-axis
                x = cx - delta_x
            else: # point right of x-axis
                x = cx + delta_x

        # calculate y coordinate relative to center
        delta_y = rad * math.sin(temp_angle)
        if p1[1] > cy and p2[1] > cy: # fully in quadrant 1 or 2
            y = cy + delta_y
        elif p1[1] < cy and p2[1] < cy: # fully in quadrant 3 or 4
            y = cy - delta_y
        else: # starts and ends on different sides of the x-axis
            if temp_angle < angle_from_p1_to_x_axis: # point below x-axis
                y = cy - delta_y
            else: # point above y-axis
                y = cy + delta_y
        
        # add points to list
        points.append((x, y))

        temp_angle += sub_angle
    
    return points
    

        
def adjust_path_for_turn_radius(input_path, min_turn_radius):
    og_path = copy.deepcopy(input_path)

    altered_path = [og_path[0]]
    circles = []
    for i in range(1, len(og_path) - 1):
        p1 = og_path[i - 1]
        p2 = og_path[i]
        p3 = og_path[i + 1]

        angle = angle_between_points(p1, p2, p3)
        print(angle)
        if angle != 0 and angle < np.pi / 2:  # Detect sharp turns
            # find a circle that includes all three points
            center, radius = find_center_and_rad(p1, p2, p3)
            if center is not None and radius < min_turn_radius:
                temp_circle = Circle(center, radius)
                print("Circle at: " + str(temp_circle.center) + " with rad: " + str(temp_circle.rad))
                circles.append(temp_circle)

                # find new points along circle to connect p1 to p3
                new_points = get_points_along_rad(temp_circle, p1, p3, ARC_DENSITY)
                og_path[i] = new_points[-2]

                altered_path.extend(new_points)

            else:
                altered_path.append(p2)

        else:
            altered_path.append(p2)

    altered_path.append(og_path[-1])
    return altered_path, circles

# Example usage
# csv_data = """41,54
# 40,55
# 39,55
# 38,56
# 37,57
# 36,58
# 35,58
# 34,58
# 33,58
# 32,58
# 31,58
# 30,59
# 31,60
# 32,60
# 33,60
# 34,60
# 35,60
# 36,60
# 37,61
# 38,62
# 39,63
# 40,63
# 41,63
# 42,63
# """

csv_data = """51,51
51,52
51,53
51,54
51,55
51,56
51,57
51,58
51,59
50,60
49,61
48,62
48,63
48,64
48,65
"""

# Example usage
input_path = read_csv_data(csv_data)
min_turn_radius = 5

figure, axes = plt.subplots()

altered_path, circles = adjust_path_for_turn_radius(input_path, min_turn_radius)

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
plt.legend()
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Path Adjustment for Minimum Turn Radius')
plt.show()