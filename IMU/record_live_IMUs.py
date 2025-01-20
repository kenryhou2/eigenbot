#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.animation import FuncAnimation
from multiprocessing import Process
import sys
import os

def handle_device(port, test_dir):
    try:
        # Set up the serial line
        ser = serial.Serial(port, 9600)

        # Set up the figure for plotting
        fig, ax = plt.subplots()
        lines = [ax.plot([], [])[0] for _ in range(6)]  # Create a line object for each index
        index_name = ['Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y', 'Gyro Z']
        # indices = [2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16]  # Indices to print
        indices = [1, 2, 3, 4, 5, 6]
        # Hall effect #1 xyz, Hall effect #2 xyz, Hall effect #3 xyz, Hall effect #4 xyz
        # indices = [10, 15, 2, 7]
        data_buffer = [[] for _ in indices]  # Initialize a list of lists to store the latest 100 data points for each index

        # Set up the file for saving data
        npz_filename = os.path.join(test_dir, f"data_{port.replace('/', '_')}.npz")
        # data_dict = {f"{i}" for i in index_name}
        data_dict = {key: [] for key in index_name}
        data_dict["time"] = []

        def init():
            ax.set_xlim(0, 40)
            ax.set_ylim(-30000, 30000)  # Adjust these limits based on your data range
            ax.legend([f"{i}" for i in index_name])  # Add legend with index numbers
            #name figure the device name
            ax.set_title(f"Device {port}")
            return lines

        def update(frame):
            try:
                line = ser.readline().decode('utf-8').strip()
                data = list(map(float, line.split('\t')))
                
                selected_data = [data[i] for i in indices]
                # selected_data = [-data[i] if i in [2, 7] else data[i] for i in indices]
                print(selected_data)

                timestamp = data[0]
                data_dict["time"].append(timestamp)

                for i, value in enumerate(selected_data):
                    data_buffer[i].append(value)
                    data_dict[index_name[i-1]].append(value)
                    # data_dict[f"index_{indices[i]}"].append(value)
                    if len(data_buffer[i]) > 40:
                        data_buffer[i].pop(0)
                    lines[i].set_data(range(len(data_buffer[i])), data_buffer[i])

                # Save the data to the npz file
                np.savez(npz_filename, **data_dict)

                return lines
            except serial.SerialException:
                print(f"Serial connection lost on port {port}. Closing connection and terminating process.")
                ser.close()
                np.savez(npz_filename, **data_dict)
                sys.exit(1)

        ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1)

        plt.show()

    except KeyboardInterrupt:
        ser.close()
        np.savez(npz_filename, **data_dict)
        print("Interrupted and serial connection closed.")
    except serial.SerialException:
        print(f"Failed to connect to port {port}. Terminating process.")
        np.savez(npz_filename, **data_dict)
        sys.exit(1)

def main():
    # Create a folder with the current timestamp within the /test directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    test_dir = os.path.join(os.getcwd(), 'test', timestamp)
    os.makedirs(test_dir, exist_ok=True)

    # List of serial ports for the 6 devices
    ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']

    # Create and start a process for each device
    processes = []
    for port in ports:
        p = Process(target=handle_device, args=(port, test_dir))
        p.start()
        processes.append(p)

    # Wait for all processes to finish
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()