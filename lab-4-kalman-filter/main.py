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

        self.forward_speed = 20  # speed in cm/s
        self.exp_done = False

    async def exp(self):
        self._clear_motor_history()
        self.drive.set_speed(self.forward_speed, self.forward_speed)
        await asyncio.sleep(4)

        self._clear_motor_history()
        self.drive.set_speed(-100, 100)
        await asyncio.sleep(5)

        self._clear_motor_history()
        self.drive.set_speed(self.forward_speed, self.forward_speed)
        await asyncio.sleep(4)

        self.drive.stop()

        self.exp_done = True

    # Log wheel encoder data while experiment is running
    async def log_exp(self):
        start_time = time.ticks_us()
        while not self.exp_done:
            message = f"{(time.ticks_diff(time.ticks_us(), start_time))},{self.drive.left_motor.get_position_counts()},{self.drive.right_motor.get_position_counts()},{self.drive.imu.get_acc_x()},{self.drive.imu.get_acc_y()},{self.drive.imu.get_gyro_z_rate()}"
            self.mqtt.publish("epic-topic/data", message)
            await asyncio.sleep(0.1)

    # Run experiment and logger concurrently
    async def main(self):
        await asyncio.gather(
            self.exp(),
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
