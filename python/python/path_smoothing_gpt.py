import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Function to read the CSV data and convert it into a path
def read_csv_data(csv_data):
    path = []
    for line in csv_data.strip().split('\n'):
        x, y = map(int, line.split(','))
        path.append((y, x))
    return path

def smooth_path(path, min_turn_radius, smoothing_factor=0.5):
    def calculate_curvature(x, y):
        dx = np.gradient(x)
        dy = np.gradient(y)
        ddx = np.gradient(dx)
        ddy = np.gradient(dy)
        curvature = np.abs(dx * ddy - dy * ddx) / (dx * dx + dy * dy)**1.5
        return curvature

    def smooth_segment(x, y, max_curvature):
        t = np.linspace(0, 1, len(x))
        cs_x = CubicSpline(t, x)
        cs_y = CubicSpline(t, y)
        t_new = np.linspace(0, 1, len(x) * 10)
        smoothed_x = cs_x(t_new)
        smoothed_y = cs_y(t_new)

        curvature = calculate_curvature(smoothed_x, smoothed_y)
        while np.any(curvature > max_curvature):
            smoothed_x, smoothed_y = (smoothed_x[:-1] + smoothed_x[1:]) / 2, (smoothed_y[:-1] + smoothed_y[1:]) / 2
            curvature = calculate_curvature(smoothed_x, smoothed_y)

        return smoothed_x, smoothed_y

    x, y = zip(*path)
    x = np.array(x)
    y = np.array(y)
    max_curvature = 1 / min_turn_radius

    smoothed_x, smoothed_y = smooth_segment(x, y, max_curvature)
    smoothed_x, smoothed_y = smoothed_x[::int(1/smoothing_factor)], smoothed_y[::int(1/smoothing_factor)]

    return list(zip(smoothed_x, smoothed_y))

csv_data = """14,14
15,15
16,16
17,17
18,17
19,17
20,18
21,19
22,20
23,21
24,21
25,21
26,21
27,21
28,21
29,21
30,21
31,21
32,21
33,21
34,21
35,21
36,21
37,21
38,21
39,21
40,22
41,22
42,22
43,22
44,22
45,22
46,22
47,23
48,23
49,23
50,23
51,23
52,23
53,23
54,23
55,24
55,25
56,26
56,27
56,28
56,29
56,30
56,31
56,32
56,33
56,34
56,35
56,36
56,37
56,38
56,39
56,40
56,41
56,42
56,43
56,44
56,45
55,46
54,46
53,45
52,44
51,43
50,43
49,43
48,42
47,42
46,42
45,41
46,40
47,39
48,38
49,37
50,36
51,35
51,34
50,33
49,33
48,32
47,31
46,30
45,29
44,28
43,27
42,26
41,27
40,28
39,29
38,30
37,31
36,32
35,33
34,34
34,35
34,36"""

# Example usage
path = read_csv_data(csv_data)
min_turn_radius = 0.4

smoothed_path = smooth_path(path, min_turn_radius)

# Plot the original and smoothed paths
original_x, original_y = zip(*path)
smoothed_x, smoothed_y = zip(*smoothed_path)

plt.plot(original_x, original_y, 'ro-', label='Original Path')
plt.plot(smoothed_x, smoothed_y, 'bo-', label='Smoothed Path')
plt.legend()
plt.show()
