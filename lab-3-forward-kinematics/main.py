import asyncio
from XRPLib.differential_drive import DifferentialDrive
from XRPLib.board import Board
from mqttconnect import *
import time


class Robot:
    # This class runs experiments and logs encoder data via MQTT

    def __init__(self):
        self.drive = DifferentialDrive.get_default_differential_drive()
        self.mqtt = connect_mqtt()
        self.mqtt.ping()

        self.forward_speed = 10  # speed in cm/s
        self.exp_done = False

    # Experiment 1: drive forward, turn 180, drive back
    async def exp_1(self):
        print("move forward")
        self.drive.set_speed(self.forward_speed, self.forward_speed)
        await asyncio.sleep(10)
        self._clear_motor_history()
        self.drive.stop()

        print("turn")
        await self.drive.async_turn(180, max_effort=0.5, use_imu=False, timeout=5)
        self._clear_motor_history()
        self.drive.stop()

        print("move forward")
        self.drive.set_speed(self.forward_speed, self.forward_speed)
        await asyncio.sleep(10)
        self._clear_motor_history()
        self.drive.stop()

        self.exp_done = True
        print("done")

    # Experiment 2: drive straight, then arc (left slower)
    async def exp_2(self):
        self.drive.set_speed(self.forward_speed, self.forward_speed)
        await asyncio.sleep(5)
        self._clear_motor_history()
        self.drive.stop()

        self.drive.set_speed(self.forward_speed, self.forward_speed / 2)
        await asyncio.sleep(5)
        self._clear_motor_history()
        self.drive.stop()

        self.exp_done = True

    # Experiment 3: drive in a circle for 30s
    async def exp_3(self):
        factor = 0.72
        self.drive.set_speed(self.forward_speed * factor, self.forward_speed / 2 * factor)
        await asyncio.sleep(30)
        self._clear_motor_history()
        self.drive.stop()

        self.exp_done = True

    # Log wheel encoder data while experiment is running
    async def log_exp(self):
        start_time = time.time_ns()
        while not self.exp_done:
            message = f"{(time.time_ns() - start_time)/1000:.0f},{self.drive.left_motor.get_position_counts()},{self.drive.right_motor.get_position_counts()}"
            self.mqtt.publish("epic-topic/data", message)
            await asyncio.sleep(0.1)

    # Run experiment and logger concurrently
    async def main(self):
        await asyncio.gather(
            # self.exp_1(),
            # self.exp_2(),
            self.exp_3(),
            self.log_exp()
        )

    # Entry point to start everything
    def run(self):
        asyncio.run(self.main())
        self.drive.stop()

    # Helper to clear motor controller logs
    def _clear_motor_history(self):
        self.drive.left_motor.speedController.clear_history()
        self.drive.right_motor.speedController.clear_history()


robot = Robot()
board = Board.get_default_board()
board.wait_for_button()  # wait for user to start
robot.run()
