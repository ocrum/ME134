import matplotlib.pyplot as plt
import csv
import math
from svgpathtools import svg2paths

exp = 3     # experiment number (used to load corresponding CSV and SVG files)
d = 0.15    # distance between wheels (wheelbase)

# Compute coordinates from encoder data
def get_calc_coords():
    file = f'exp{exp}.csv'

    # Constants for encoder resolution and wheel movement
    gear_ratio = (30/14) * (28/16) * (36/9) * (26/8)  # total gear ratio
    counts_per_motor_shaft_revolution = 12
    resolution = counts_per_motor_shaft_revolution * gear_ratio # 585
    wheel_d = 0.06
    meters_per_tick = (math.pi * wheel_d) / resolution

    calc_x = [0]
    calc_y = [0]
    calc_theta = [0]

    # Read and process CSV
    with open(file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        prev_ms, prev_l, prev_r = next(reader)
        prev_ms = int(prev_ms)
        prev_l = int(prev_l)
        prev_r = int(prev_r)

        for ms, l, r in reader:
            ms = int(ms)
            l = int(l)
            r = int(r)

            x = calc_x[-1]
            y = calc_y[-1]
            theta = calc_theta[-1]

            dt = (ms - prev_ms) / 1e6  # convert microseconds to seconds
            v_l = (l - prev_l) * meters_per_tick / dt
            v_r = (r - prev_r) * meters_per_tick / dt

            # Compute turning radius and angular velocity
            R = 0
            if v_r - v_l != 0:
                R = (d / 2) * (v_r + v_l) / (v_r - v_l)
            omega = (v_r - v_l) / d

            # Integrate pose
            next_x = x - R * math.sin(theta) + R * math.sin(theta + omega * dt)
            next_y = y + R * math.cos(theta) - R * math.cos(theta + omega * dt)
            next_theta = (theta + omega * dt) % (2 * math.pi)

            calc_x.append(next_x)
            calc_y.append(next_y)
            calc_theta.append(next_theta)

            prev_ms = ms
            prev_l = l
            prev_r = r

    return calc_x, calc_y

# Return ground-truth path for different experiments
def get_theo_coords():
    theo_x = [0]
    theo_y = [0]

    # Helper to add a circular arc
    def add_circle(factor, time):
        v_r = 0.1 * factor
        v_l = v_r / 2
        R = (d / 2) * (v_r + v_l) / (v_r - v_l)
        omega = (v_r - v_l) / d
        start_x = theo_x[-1]
        start_y = theo_y[-1]
        for t in [i / 100 * time for i in range(100)]:
            theo_x.append(R * math.sin(t * omega) + start_x)
            theo_y.append(R * (math.cos(t * omega) - 1) + start_y)

    # Define path shapes by experiment
    if exp == 1:
        theo_x = [0, 0.1 * 10, 0]
        theo_y = [0, 0, 0]
    elif exp == 2:
        theo_x = [0, 0.1 * 5]
        theo_y = [0, 0]
        add_circle(1, 5)
    elif exp == 3:
        theo_x = [0]
        theo_y = [0]
        add_circle(0.72, 30)

    return theo_x, theo_y

# Load observed path from SVG file (traced from a photo with a ruler)
def get_obs_coords():
    svg_path = f'exp{exp}.svg'
    paths, _ = svg2paths(svg_path)

    obs_x = []
    obs_y = []

    # Sample evenly along the first SVG path
    for segment in paths[0]:
        for t in [i/100 for i in range(101)]:
            point = segment.point(t)
            obs_x.append(point.real / 1000)  # convert mm to m
            obs_y.append(point.imag / 1000)

    return obs_x, obs_y

# Plot theoretical, observed, and calculated paths
def plot():
    theo_x, theo_y = get_theo_coords()
    obs_x, obs_y = get_obs_coords()
    calc_x, calc_y = get_calc_coords()

    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    ax.plot(theo_x, theo_y, label='Theoretical', color='blue')
    ax.scatter(theo_x[0], theo_y[0], marker='o', color='blue')
    ax.scatter(theo_x[-1], theo_y[-1], marker='x', color='blue')

    ax.plot(calc_x, calc_y, label='Calculated', color='red')
    ax.scatter(calc_x[0], calc_y[0], marker='o', color='red')
    ax.scatter(calc_x[-1], calc_y[-1], marker='x', color='red')

    ax.plot(obs_x, obs_y, label='Observed', color='green')
    ax.scatter(obs_x[0], obs_y[0], marker='o', color='green')
    ax.scatter(obs_x[-1], obs_y[-1], marker='x', color='green')

    ax.set_xlabel('x pos (m)')
    ax.set_ylabel('y pos (m)')
    ax.set_title(f'Experiment {exp}: ')
    ax.legend()
    plt.show()

plot()
