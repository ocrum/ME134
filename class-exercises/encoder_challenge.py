import math
from XRPLib.encoder import Encoder
import time

running = True
encoder = Encoder(0, 4, 5)

gear_ratio = (30/14) * (28/16) * (36/9) * (26/8)
enc_counts_per_rev = 12
resolution = gear_ratio * enc_counts_per_rev
wheel_diameter = 6 # cm

while running:
    time.sleep(0.05)
    enc_count = encoder.get_position_counts()
    distance = enc_count / resolution * math.pi * wheel_diameter

    print(enc_count)
    print(distance)

