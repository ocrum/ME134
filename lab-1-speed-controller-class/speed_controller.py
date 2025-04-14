from XRPLib.board import Board
from XRPLib.encoder import Encoder
from XRPLib.motor import Motor
import time
import math
import gc

gc.collect()

board = Board.get_default_board()

# Define pins
LEFT_ENCODER_A = 4  
LEFT_ENCODER_B = 5  
RIGHT_ENCODER_A = 12
RIGHT_ENCODER_B = 13

LEFT_MOTOR_A = 6
LEFT_MOTOR_B = 7
RIGHT_MOTOR_A = 14
RIGHT_MOTOR_B = 15

# Instantiate Encoder class
left_motor_encoder = Encoder(index=0, encAPin=LEFT_ENCODER_A, encBPin=LEFT_ENCODER_B)
right_motor_encoder = Encoder(index=1, encAPin=RIGHT_ENCODER_A, encBPin=RIGHT_ENCODER_B)

# Instantiate Motor class
left_motor = Motor(LEFT_MOTOR_A, LEFT_MOTOR_B,flip_dir=True)
right_motor = Motor(RIGHT_MOTOR_A, RIGHT_MOTOR_B)
left_motor.set_effort(0)
right_motor.set_effort(0)

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.error_sum = 0
        self.error_delta = 0
        self.prev_error = 0
        
    def update(self, error):
        if wait_time == 0:
            print("WARNING: zero time has passed (cannot find derivative term)")
            return 0

        self.error_delta = (error - self.prev_error) / wait_time
        self.error_sum += error * wait_time
        self.prev_error = error

        effort = error * self.Kp + self.error_delta * self.Kd + self.error_sum * self.Ki

        return effort

# Parameters for speed control
counts_per_wheel_revolution = (30/14) * (28/16) * (36/9) * (26/8) * 12 # 585
wheel_diameter = 60 #mm
circumference_wheel = math.pi*wheel_diameter #188.49mm

speed_left_target = 100 #mm/s
speed_right_target = 100 #mm/s

test_duration = 10 #s
sampling_time = 0.05 #s, choose your sampling time
Kp_left = 0.001 # find your Kp
Ki_left = 0.01  # find your Ki
Kd_left = 0 # find your Kd
Kp_right = Kp_left
Ki_right = Ki_left
Kd_right = Kd_left
    
speed_left_controller = PIDController(Kp_left, Ki_left, Kd_left)
speed_right_controller = PIDController(Kp_right, Ki_right, Kd_right)


prev_l_enc_count = 0
prev_r_enc_count = 0

def calculate_speed():
    """
    Calculates the tangential velocity
    """
    global prev_l_enc_count, prev_r_enc_count

    curr_l_enc_count = left_motor_encoder.get_position_counts()
    curr_r_enc_count = right_motor_encoder.get_position_counts()
    
    # print(curr_l_enc_count - prev_l_enc_count, wait_time)

    if wait_time != 0:
        speed_left = (curr_l_enc_count - prev_l_enc_count) / counts_per_wheel_revolution * circumference_wheel / wait_time
        speed_right = (curr_r_enc_count - prev_r_enc_count) / counts_per_wheel_revolution * circumference_wheel / wait_time
    else:
        speed_left = 0
        speed_right = 0
        print("WARNING: zero time has passed (speed cannot be calculated)")

    prev_l_enc_count = curr_l_enc_count
    prev_r_enc_count = curr_r_enc_count

    return speed_left, speed_right


def update_effort(speed_left, speed_right):
    l_error = speed_left_target - speed_left
    r_error = speed_right_target - speed_right
    
    l_effort = speed_left_controller.update(l_error)
    r_effort = speed_right_controller.update(r_error)

    print(f'{l_error},{l_effort},{r_error},{r_effort}')

    left_motor.set_effort(l_effort)
    right_motor.set_effort(r_effort)
    # left_motor.set_effort(1)
    # right_motor.set_effort(1)


print("Waiting for start button...")
board.wait_for_button()  # Wait for the button to start
print("Started! Press the button again to stop.")

init_time = time.ticks_ms()
last_time = init_time
current_time = time.ticks_ms()

data = []

print('time,l speed,r speed,l error,l effort,r error,r effort')
while (current_time - init_time)/1000 < test_duration:
    if board.is_button_pressed():  # Check if the button is pressed to stop
        print("Stopped!")
        left_motor.set_effort(0)
        right_motor.set_effort(0)
        board.wait_for_button()  # Wait for button release to avoid immediate restart
        break
    
    current_time = time.ticks_ms()
    wait_time = (current_time - last_time)/1000 # convert from ms to s
    if wait_time > sampling_time:
        speed_left, speed_right = calculate_speed()
        speed_left = -speed_left
        print(f"{current_time - init_time},{speed_left},{speed_right},", end='')
        update_effort(speed_left, speed_right)

        last_time = current_time



left_motor.set_effort(0)
right_motor.set_effort(0)


# with open("output.csv", "w") as f:
#     f.write('time,l speed,r speed\n')
#     for row in data:
#         f.write(f"{row[0]},{row[1]},{row[2]}\n")