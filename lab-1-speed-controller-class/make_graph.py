import matplotlib.pyplot as plt
import pandas as pd

# File name
csv_file = "ground_pid_400.csv"

# Read the CSV file
df = pd.read_csv(csv_file)

# Create figure with three subplots
plt.figure(figsize=(10, 12))

# Subplot 1: Left & Right Speed
plt.subplot(3, 1, 1)
plt.plot(df["time"], df["l speed"], label="Left Speed", linestyle="-")
plt.plot(df["time"], df["r speed"], label="Right Speed", linestyle="-")
plt.xlabel("Time (s)")
plt.ylabel("Speed")
plt.title("Left & Right Wheel Speed Over Time")
plt.legend()
plt.grid(True)

print(f'Left speed mean: {df["l speed"].mean()}')
print(f'Right speed mean: {df["r speed"].mean()}')
print(f'Left speed standard deviation: {df["l speed"].std()}')
print(f'Right speed standard deviation: {df["r speed"].std()}')

# Subplot 2: Left & Right Error
plt.subplot(3, 1, 2)
plt.plot(df["time"], df["l error"], label="Left Error", linestyle="-")
plt.plot(df["time"], df["r error"], label="Right Error", linestyle="-")
plt.xlabel("Time (s)")
plt.ylabel("Error")
plt.title("Left & Right Wheel Error Over Time")
plt.legend()
plt.grid(True)

# Subplot 3: Left & Right Effort
plt.subplot(3, 1, 3)
plt.plot(df["time"], df["l effort"], label="Left Effort", linestyle="-")
plt.plot(df["time"], df["r effort"], label="Right Effort", linestyle="-")
plt.xlabel("Time (s)")
plt.ylabel("Effort")
plt.title("Left & Right Effort Over Time")
plt.legend()
plt.grid(True)

plt.savefig(csv_file.replace(".csv", ".png"))

# Adjust layout and show plot
plt.tight_layout()
plt.show()

