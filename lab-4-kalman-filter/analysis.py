import matplotlib.pyplot as plt
import csv
import math
from svgpathtools import svg2paths
import numpy as np

d = 0.15    # distance between wheels (wheelbase)

# Compute coordinates from encoder data
def get_calc_coords(kalman = False):
    file = f'data.csv'

    # Constants for encoder resolution and wheel movement
    gear_ratio = (30/14) * (28/16) * (36/9) * (26/8)  # total gear ratio
    counts_per_motor_shaft_revolution = 12
    resolution = counts_per_motor_shaft_revolution * gear_ratio # 585
    wheel_d = 0.06
    meters_per_tick = (math.pi * wheel_d) / resolution

    states = [np.zeros((3, 1))]

    # Read and process CSV
    with open(file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        prev_ms, prev_l, prev_r, _, _, _ = next(reader)
        prev_dt = 0

        prev_ms = int(prev_ms)
        prev_l = int(prev_l)
        prev_r = int(prev_r)

        P = np.diag([0, 0, 0])
        Q = np.diag([0.0005, 0.0005, 1])
        R = np.diag([1, 1, 0.01])

        for ms, l, r, a_x, a_y, g_z in reader:
            ms = int(ms)
            l = int(l)
            r = int(r)
            a_x = float(a_x)
            a_y = float(a_y)
            g_z = float(g_z)

            prev_theta = float(states[-1][2])

            dt = (ms - prev_ms) / 1e6  # convert microseconds to seconds
            v_l = (l - prev_l) * meters_per_tick / dt
            v_r = (r - prev_r) * meters_per_tick / dt

            # Compute turning radius and angular velocity
            radius = 0
            if v_r - v_l != 0:
                radius = (d / 2) * (v_r + v_l) / (v_r - v_l)
            omega = (v_r - v_l) / d

            # update step
            pred_state= states[-1] + [[-radius * math.sin(prev_theta) + radius * math.sin(prev_theta + omega * dt)],
                                      [radius * math.cos(prev_theta) - radius * math.cos(prev_theta + omega * dt)],
                                      [omega * dt]]
            if kalman:
                P = P + Q

                # predict step
                v = np.array([[0],[0],[0]])
                if len(states) >= 2:
                    v = (states[-1] -states[-2]) / prev_dt

                measured_state = states[-1] + [[(v[0, 0] + a_x * 0.00980665 * dt) * dt], # mg to m/s^2
                                               [(v[1, 0] + a_y * 0.00980665 * dt) * dt], # mg to m/s^2
                                               [g_z * math.pi / 180000 * dt]] # mdps to rad/s

                K = P @ np.linalg.inv(P + R)
                update_state = pred_state + K @ (measured_state - pred_state)
                P = (np.eye(3) - K) @ P
                states.append(update_state)
            else:
                states.append(pred_state)

            prev_ms = ms
            prev_l = l
            prev_r = r
            prev_dt = dt

    x_arr = [float(s[0]) for s in states]
    y_arr = [float(s[1]) for s in states]
    theta_arr = [float(s[2]) for s in states]

    return x_arr, y_arr, theta_arr


# Load observed path from SVG file (traced from a photo with a ruler)
def get_obs_coords():
    svg_path = f'path.svg'
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


def plot():
    obs_x, obs_y = get_obs_coords()
    fk_x, fk_y, _ = get_calc_coords()
    kalman_x, kalman_y, _ = get_calc_coords(kalman = True)

    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    ax.plot(kalman_x, kalman_y, label='Kalman', color='blue')
    ax.scatter(kalman_x[0], kalman_y[0], marker='o', color='blue')
    ax.scatter(kalman_x[-1], kalman_y[-1], marker='x', color='blue')

    ax.plot(fk_x, fk_y, label='FK', color='red')
    ax.scatter(fk_x[0], fk_y[0], marker='o', color='red')
    ax.scatter(fk_x[-1], fk_y[-1], marker='x', color='red')

    ax.plot(obs_x, obs_y, label='Observed', color='green')
    ax.scatter(obs_x[0], obs_y[0], marker='o', color='green')
    ax.scatter(obs_x[-1], obs_y[-1], marker='x', color='green')

    ax.set_xlabel('x pos (m)')
    ax.set_ylabel('y pos (m)')
    ax.set_title(f'FK vs Kalman Estimates vs Ground Truth')
    ax.legend()
    plt.show()

plot()
