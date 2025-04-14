import random

from huskyLense import HuskyLensLibrary
from XRPLib.differential_drive import DifferentialDrive
from XRPLib.rangefinder import Rangefinder
from XRPLib.reflectance import Reflectance
from XRPLib.pid import PID
import time


class Robot:
    class State():
        RANDOM_WALK = "RANDOM_WALK"
        WALL_FOLLOWING = "WALL_FOLLOWING"
        LINE_FOLLOWING = "LINE_FOLLOWING"
        LINE_TO_WALL = "LINE_TO_WALL"
        WALL_TO_LINE = "WALL_TO_LINE"

    def __init__(self):
        # Initialize sensors, drive, and control systems
        self.differential_drive = DifferentialDrive.get_default_differential_drive()
        self.husky = HuskyLensLibrary("I2C")

        self.rangefinder = Rangefinder.get_default_rangefinder()
        self.reflectance = Reflectance.get_default_reflectance()

        # PID controllers
        self.wall_follow_PID = PID(kp=0.05, ki=0, kd=0)
        self.line_follow_PID = PID(kp=0.002, ki=0.0001, kd=0)

        # State and data
        self.state = self.State.RANDOM_WALK
        self.distances = [0] * 5
        self.random_walk_start_time = time.time()

        # Ensure line tracking mode is enabled
        if not self.husky.line_tracking_mode():
            self.husky.line_tracking_mode()

    def run(self):
        # Main loop
        while True:
            print(self.state, end=" ")
        
            if self.state == self.State.RANDOM_WALK:
                self.random_walk()
            elif self.state == self.State.WALL_FOLLOWING or self.state == self.State.LINE_TO_WALL:
                self.wall_follow()
            elif self.state == self.State.LINE_FOLLOWING or self.state == self.State.WALL_TO_LINE:
                self.line_follow()
            else:
                print("Uncaught state", end=" ")
        
            self.transition()
            print()
            time.sleep(0.1)


    def random_walk(self):
        # Drive randomly every second
        now = time.time()
        elapsed_time = now - self.random_walk_start_time

        if elapsed_time > 1:
            self.random_walk_start_time = now
            left_effort = 0.4 + random.uniform(-0.2, 0)
            right_effort = 0.4 + random.uniform(-0.2, 0)
            print(f"Random walk: {left_effort} {right_effort}", end=" ")
            self.differential_drive.set_effort(left_effort, right_effort)

    def wall_follow(self):
        # Follow wall using PID control and ultrasonic sensor
        target_dist = 15
        base_effort = 0.4

        dist = self.get_distance()

        some_variable = 0
        if dist < 40:
            error = dist - target_dist
            some_variable = self.wall_follow_PID.update(error)

            print(f"Wall follow: {dist} {some_variable}", end=" ")
        else:
            print("Wall not detected", end=" ")

        self.differential_drive.set_effort(base_effort + some_variable, base_effort - some_variable)


    def line_follow(self):
        # Follow line using HuskyLens arrows and PID
        base_effort = 0.4
        target_pos = 120

        state = self.husky.command_request_arrows()

        if len(state) > 0:
            state_vector = state[0]

            state_x1 = state_vector[0]
            state_x2 = state_vector[2]

            x = (state_x1 + state_x2) / 2
            error = x - target_pos

            some_variable = self.line_follow_PID.update(error)
            print(f"Line follow: {error} {some_variable}", end=" ")

            self.differential_drive.set_effort(base_effort + some_variable, base_effort - some_variable)

    def get_distance(self):
        # Median filter on recent distance readings
        curr_dist = self.rangefinder.distance()
        self.distances.append(curr_dist)
        self.distances.pop(0)

        mid_index = len(self.distances) // 2
        sorted_distances = sorted(self.distances)
        return sorted_distances[mid_index]

    def is_line_detected(self) -> bool:
        # CHeck if line is detected
        state = self.husky.command_request_arrows()
        num_arrows = len(state)
        print(f"Line detected {num_arrows}", end=" ")
        return len(state) > 0

    def is_wall_detected(self) -> bool:
        # Check if wall is close enough
        dist = self.get_distance()
        print(f"Wall detect: {dist}", end=" ")
        return dist < 20

    def transition(self):
        # State transition logic based on sensor input
        is_line_detected = self.is_line_detected()
        is_wall_detected = self.is_wall_detected()

        if self.state == self.State.RANDOM_WALK:
            if is_wall_detected:
                self.state = self.State.WALL_FOLLOWING
            elif is_line_detected:
                self.state = self.State.LINE_FOLLOWING
                self.line_follow_PID.clear_history()

        elif self.state == self.State.WALL_FOLLOWING:
            if is_line_detected:
                self.state = self.State.WALL_TO_LINE
            elif not (is_wall_detected or is_line_detected):
                self.state = self.State.RANDOM_WALK

        elif self.state == self.State.LINE_FOLLOWING:
            if is_wall_detected:
                self.state = self.State.LINE_TO_WALL
            elif not (is_line_detected or is_wall_detected):
                self.state = self.State.RANDOM_WALK

        elif self.state == self.State.LINE_TO_WALL:
            if is_wall_detected and not is_line_detected:
                self.state = self.State.WALL_FOLLOWING
            elif not is_wall_detected and is_line_detected:
                self.state = self.State.LINE_FOLLOWING
                self.line_follow_PID.clear_history()
            elif not (is_line_detected or is_wall_detected):
                self.state = self.State.RANDOM_WALK

        elif self.state == self.State.WALL_TO_LINE:
            if is_wall_detected and not is_line_detected:
                self.state = self.State.WALL_FOLLOWING
            elif not is_wall_detected and is_line_detected:
                self.state = self.State.LINE_FOLLOWING
                self.line_follow_PID.clear_history()
            elif not (is_line_detected or is_wall_detected):
                self.state = self.State.RANDOM_WALK

robot = Robot()
robot.run()