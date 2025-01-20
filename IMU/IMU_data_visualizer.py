import os
import numpy as np
import matplotlib.pyplot as plt

# Function to find the most recent timestamp directory
def find_most_recent_directory(base_dir):
    try:
        subdirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        latest_dir = max(subdirs, key=os.path.getmtime)
        return latest_dir
    except ValueError:
        raise FileNotFoundError("No directories found in the specified base directory.")

# Base directory containing the test folders
test_base_dir = os.path.join(os.getcwd(), 'test')

# Find the most recent directory
most_recent_dir = find_most_recent_directory(test_base_dir)

# List of filenames in the most recent directory
filenames = [
    os.path.join(most_recent_dir, "data__dev_ttyACM0.npz"),
    os.path.join(most_recent_dir, "data__dev_ttyACM1.npz"),
    os.path.join(most_recent_dir, "data__dev_ttyACM2.npz"),
    os.path.join(most_recent_dir, "data__dev_ttyACM3.npz")
]

# Initialize figure for subplots
fig, axs = plt.subplots(len(filenames), 1, figsize=(10, 12))
fig.tight_layout(pad=5.0)

# Data for additional plots
accel_data = {"Accel X": [], "Accel Y": [], "Accel Z": []}
gyro_data = {"Gyro X": [], "Gyro Y": [], "Gyro Z": []}
time_data = []

# Iterate through each file
for idx, filename in enumerate(filenames):
    try:
        # Load the .npz file
        data = np.load(filename)

        # Extract data
        accel_x = data['Accel X']
        accel_y = data['Accel Y']
        accel_z = data['Accel Z']
        gyro_x = data['Gyro X']
        gyro_y = data['Gyro Y']
        gyro_z = data['Gyro Z']
        time = data['time']

        # Store data for second and third figures
        accel_data["Accel X"].append((time, accel_x))
        accel_data["Accel Y"].append((time, accel_y))
        accel_data["Accel Z"].append((time, accel_z))
        gyro_data["Gyro X"].append((time, gyro_x))
        gyro_data["Gyro Y"].append((time, gyro_y))
        gyro_data["Gyro Z"].append((time, gyro_z))
        time_data.append(time)

        # Plot data
        axs[idx].plot(time, accel_x, label='Accel X')
        axs[idx].plot(time, accel_y, label='Accel Y')
        axs[idx].plot(time, accel_z, label='Accel Z')
        axs[idx].plot(time, gyro_x, label='Gyro X')
        axs[idx].plot(time, gyro_y, label='Gyro Y')
        axs[idx].plot(time, gyro_z, label='Gyro Z')

        axs[idx].set_title(f"Data from {filename}")
        axs[idx].set_xlabel("Time (s)")
        axs[idx].set_ylabel("Sensor Values")
        axs[idx].legend()
        axs[idx].grid(True)

    except Exception as e:
        print(f"Error processing file {filename}: {e}")

# Plot Acceleration Data
fig_accel, axs_accel = plt.subplots(3, 1, figsize=(10, 12))
fig_accel.suptitle("Acceleration Data")
for i, (key, ax) in enumerate(zip(accel_data.keys(), axs_accel)):
    for j, (time, data) in enumerate(accel_data[key]):
        ax.plot(time, data, label=f"ACM{j}")
    ax.set_title(key)
    ax.set_xlabel("Time (us)")
    ax.set_ylabel("Acceleration")
    ax.legend()
    ax.grid(True)

# Plot Angular Velocity Data
fig_gyro, axs_gyro = plt.subplots(3, 1, figsize=(10, 12))
fig_gyro.suptitle("Angular Velocity Data")
for i, (key, ax) in enumerate(zip(gyro_data.keys(), axs_gyro)):
    for j, (time, data) in enumerate(gyro_data[key]):
        ax.plot(time, data, label=f"ACM{j}")
    ax.set_title(key)
    ax.set_xlabel("Time (us)")
    ax.set_ylabel("Angular Velocity")
    ax.legend()
    ax.grid(True)

# Display the plots
plt.show()
