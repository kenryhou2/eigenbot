import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse

MODULE = '11'
offset = {'11': -np.pi/4, '05': -np.pi/4, '54': np.pi/4}

def process_data(lines):
    np_data = []
    ni_data = []
    for line in lines:
        parts = line.strip().split(',')
        timestamp = parts[0]
        node_type = parts[1][:2]
        data = ','.join(parts[1:])[2:]
        data = data.split(':')[0]
        split_regex = r'[, ]'
        data_elements = re.split(split_regex, data)
        if node_type == 'Np':
            if len(data_elements) != 15:
                continue
            for i in range(0, len(data_elements), 5):
                node_id = data_elements[i]
                joint_pos = str(float(data_elements[i + 1]) - offset[MODULE])
                joint_vel = data_elements[i + 2]
                load = data_elements[i + 3]
                contact = data_elements[i + 4]
                np_data.append([timestamp, node_id, joint_pos, joint_vel, load, contact])
        elif node_type == 'Ni':
            if len(data_elements) != 12:
                continue
            for i in range(0, len(data_elements), 4):
                node_id = data_elements[i]
                phase = data_elements[i + 1]
                cpg_info1 = data_elements[i + 2]
                cpg_info2 = data_elements[i + 3]
                ni_data.append([timestamp, node_id, phase, cpg_info1, cpg_info2])

    return np_data, ni_data

# Argument parser
parser = argparse.ArgumentParser(description='Plotting Neural Data')
parser.add_argument('--start', type=int, action="store", dest='start', default=0, help='starting time desired for plotting')
parser.add_argument('--file_name', action="store", dest='file_name', default='neural_data.txt', help='file name to be processed for plotting')
parser.add_argument('--speed', type=float, action="store", dest='speed', default=1.0, help='speed of the animation')
args = parser.parse_args()

# Process the data
with open(args.file_name, 'r') as file:
    data = file.readlines()
np_data, ni_data = process_data(data)

# Filter the data for the selected module
module_np_time, module_np_pos, module_np_load = [], [], []
module_ni_time, module_ni_cpg_info1, module_ni_cpg_info2, module_ni_phase = [], [], [], []

for data in np_data:
    if data[1] == MODULE:
        module_np_time.append(data[0])
        module_np_pos.append(data[2])
        module_np_load.append(data[4])

for data in ni_data:
    if data[1] == MODULE:
        module_ni_time.append(data[0])
        module_ni_cpg_info1.append(data[3])
        module_ni_cpg_info2.append(data[4])
        module_ni_phase.append(data[2])

module_np_time = np.array(module_np_time, dtype=float)
module_np_time = (module_np_time - module_np_time[0]) / 1E9
module_ni_time = np.array(module_ni_time, dtype=float)
module_ni_time = (module_ni_time - module_ni_time[0]) / 1E9
idx_start = np.argwhere(module_ni_time > args.start).flatten()[0]

# Set up the figure and subplots
fig, axs = plt.subplots(2, 1, figsize=(12, 30))
plt.subplots_adjust(hspace=0.5)

# Initialize plots
line1, = axs[0].plot([], [], color='blue', linewidth=3)
line2, = axs[0].plot([], [], color='orange', linewidth=3)
# line3, = axs[2].plot([], [], color='blue')
# line4, = axs[3].plot([], [], color='green')

# Set up the subplots with fixed limits
axs[0].set_title(f'CPG Activity for ThC Module', fontsize=20)
axs[0].set_xlabel('Time (s)', fontsize=20)
axs[0].set_ylabel('CPG Signals', fontsize=20)
# axs[0].set_facecolor((226 / 255, 253 / 255, 249 / 255))
axs[0].set_xlim(module_ni_time[idx_start], module_ni_time[-1])
# axs[0].set_ylim(min(min(module_ni_cpg_info1), min(module_ni_cpg_info2)),
                # max(max(module_ni_cpg_info1), max(module_ni_cpg_info2)))
axs[0].set_ylim(-8, 8)
axs[0].legend(['CPG Protractor Activity (Swing)', 'CPG Retractor Activity (Stance)'], fontsize=20)

# axs[2].set_title(f'Load vs. Timestamp for Module {MODULE}')
# axs[2].set_xlabel('Timestamp')
# axs[2].set_ylabel('Load')
# axs[2].set_xlim(module_np_time[idx_start], module_np_time[-1])
# axs[2].set_ylim(min(module_np_load), max(module_np_load))

# axs[3].set_title(f'Phase vs. Timestamp for Module {MODULE}')
# axs[3].set_xlabel('Timestamp')
# axs[3].set_ylabel('Phase')
# axs[3].set_xlim(module_ni_time[idx_start], module_ni_time[-1])
# axs[3].set_ylim(min(module_ni_phase), max(module_ni_phase))


# Initialize animation
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    # line3.set_data([], [])
    # line4.set_data([], [])
    # return line1, line2, line3, line4
    return line1, line2

# Update function for the animation
def update(frame):
    time_slice = module_ni_time[idx_start:idx_start+frame]
    cpg_info1_slice = np.array(module_ni_cpg_info1[idx_start:idx_start+frame], dtype=float)
    cpg_info2_slice = np.array(module_ni_cpg_info2[idx_start:idx_start+frame], dtype=float)
    load_slice = np.array(module_np_load[idx_start:idx_start+frame], dtype=float)
    phase_slice = np.array(module_ni_phase[idx_start:idx_start+frame], dtype=float)

    line1.set_data(time_slice, cpg_info1_slice)
    line2.set_data(time_slice, cpg_info2_slice)
    # line3.set_data(module_np_time[idx_start:idx_start+frame], load_slice)
    # line4.set_data(time_slice, phase_slice)

    # return line1, line2, line3, line4
    return line1, line2

plt.pause(5)
# Create animation
ani = FuncAnimation(fig, update, frames=len(module_ni_time) - idx_start, init_func=init, interval=5 / args.speed, blit=True)

plt.show()