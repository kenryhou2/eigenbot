#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.animation import FuncAnimation

# Set up the serial line
ser = serial.Serial('/dev/ttyACM0', 9600)

# Set up the figure for plotting
fig, ax = plt.subplots()
lines = [ax.plot([], [])[0] for _ in range(12)]  # Create a line object for each index
indices = [1, 2, 3, 4, 5, 6]
# indices = [2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16]  # Indices to print
data_buffer = [[] for _ in indices]  # Initialize a list of lists to store the latest 100 data points for each index

def init():
    ax.set_xlim(0, 40)
    ax.set_ylim(-28000, 28000)  # Adjust these limits based on your data range
    return lines

def update(frame):
    line = ser.readline().decode('utf-8').strip()
    data = list(map(float, line.split('\t')))
    selected_data = [data[i] for i in indices]
    print(selected_data)
    # print(data)

    for i, value in enumerate(selected_data):
        data_buffer[i].append(value)
        if len(data_buffer[i]) > 40:
            data_buffer[i].pop(0)
        lines[i].set_data(range(len(data_buffer[i])), data_buffer[i])

    return lines

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1)

plt.show()

if __name__ == "__main__":
    try:
        plt.show()
    except KeyboardInterrupt:
        ser.close()
        print("Interrupted and serial connection closed.")