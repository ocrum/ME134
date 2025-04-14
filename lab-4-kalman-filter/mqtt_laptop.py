import paho.mqtt.client as mqtt
import csv
import os
from datetime import datetime

# MQTT connection info
broker = "10.247.137.92"
port = 1883
topic = "epic-topic/data"
client_id = "daniel_laptop"

# Output CSV file (timestamped)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"data_{timestamp}.csv"

# Create CSV file with header if it doesn't exist
if not os.path.exists(csv_filename):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ms", "l", "r","a_x","a_y","g_z"])

# Called when connected to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"\nConnected to {broker} on port {port}")
        client.subscribe(topic)
    else:
        print(f"\nFailed to connect, return code {rc}")

# Called when a message is received
def on_message(client, userdata, msg):
    decoded_msg = msg.payload.decode()
    print(decoded_msg)
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(decoded_msg.split(','))

# Called on disconnect
def on_disconnect(client, userdata, rc):
    print("\nDisconnected from the broker")

# Setup MQTT client and connect
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(broker, port, keepalive=60)
client.loop_start()

# Keep script running until manually interrupted
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Interrupted")
    client.loop_stop()
    client.disconnect()
