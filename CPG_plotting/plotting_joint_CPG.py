import re
import numpy as np
import matplotlib.pyplot as plt
import argparse

MODULE = '11'
offset = {'11': -np.pi/4, '05': -np.pi/4, '54': np.pi/4}
def process_data(lines):
    np_data = []  # For Np entries: [timestamp, node_id, joint pos, joint vel, load, contact]
    ni_data = []  # For Ni entries: [timestamp, node_id, phase, CPG info1, CPG info2]
    line_num = 0
    for line in lines:
        # Removing content after colon and splitting the line
        parts = line.strip().split(',')
        timestamp = parts[0]
        # print(parts[1][:2])
        line_num += 1
        # print(line_num)
        node_type = parts[1][:2]  # "Np" or "Ni"
        data = ','.join(parts[1:])[2:]
        data = data.split(':')[0]

        split_regex = r'[, ]'

        data_elements = re.split(split_regex, data)
        if node_type == 'Np':
            # Parsing Np entries
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
            # Parsing Ni entries
            if len(data_elements) != 12:
                continue
            for i in range(0, len(data_elements), 4):
                node_id = data_elements[i]
                phase = data_elements[i + 1]
                cpg_info1 = data_elements[i + 2]
                cpg_info2 = data_elements[i + 3]
                ni_data.append([timestamp, node_id, phase, cpg_info1, cpg_info2])

    return np_data, ni_data


parser = argparse.ArgumentParser(description='Plotting Neural Data')
parser.add_argument('--start',  type=int, action="store", dest='start', default=0, help='starting time desired for plotting')
parser.add_argument('--file_name', action="store", dest='file_name', default='neural_data.txt', help='file name to be processed for plotting')
args = parser.parse_args()
# Process the data with the updated function
with open(args.file_name, 'r') as file:
    data = file.readlines()
np_data, ni_data = process_data(data)

# print(np_data)
# print(ni_data)

module_np_time = []
module_np_pos = []
module_np_vel = []
module_np_load = []
module_np_contact = []
for data in np_data:
    if data[1] == MODULE:
        # print(data)
        module_np_time.append(data[0])
        module_np_pos.append(data[2])
        module_np_vel.append(data[3])
        module_np_load.append(data[4])
        module_np_contact.append(data[5])

module_np_time = np.array(module_np_time, dtype=float)
module_np_time = (module_np_time - module_np_time[0]) / 1E9

module_ni_time = []
module_ni_phase = []
module_ni_cpg_info1 = []
module_ni_cpg_info2 = []
for data in ni_data:
    if data[1] == MODULE:
        # print(data)
        module_ni_time.append(data[0])
        module_ni_phase.append(data[2])
        module_ni_cpg_info1.append(data[3])
        module_ni_cpg_info2.append(data[4])

module_ni_time = np.array(module_ni_time, dtype=float)
module_ni_time = (module_ni_time - module_ni_time[0]) / 1E9
idx_start = np.argwhere(module_ni_time > args.start)
# import ipdb;ipdb.set_trace()


plt.figure(figsize=(12, 30))
plt.subplot(4, 1, 1)
# plt.plot(module_ni_time[idx_start[0][0]:-1], np.array(module_ni_cpg_info1[idx_start[0][0]:-1], dtype=float), marker='o', linestyle='-', color='blue')
# plt.plot(module_ni_time[idx_start[0][0]:-1], np.array(module_ni_cpg_info2[idx_start[0][0]:-1], dtype=float), marker='o', linestyle='-', color='red')
plt.plot(module_ni_time[idx_start[0][0]:-1], np.array(module_ni_cpg_info1[idx_start[0][0]:-1], dtype=float),color="orange", alpha=1, linewidth=3)
plt.plot(module_ni_time[idx_start[0][0]:-1], np.array(module_ni_cpg_info2[idx_start[0][0]:-1], dtype=float), color="purple", alpha=15, linewidth=3)

plt.title('CPG vs. Timestamp for Module ' + MODULE)
plt.xlabel('Timestamp')
plt.ylabel('CPG')
plt.gca().set_facecolor((226 / 255, 253 / 255, 249 / 255)) 
# plt.grid(True)
# plt.legend(['CPG Info 1', 'CPG Info 2'])
# plt.legend(['CPG Retractor Activity', 'CPG Protractor Activity'])
# plt.savefig("neuron_graph/Module "+ MODULE + " CPG-Time.png")

# # plt.figure(figsize=(12, 6))
# plt.subplot(4, 1, 2)
# # plt.plot(module_np_time[idx_start[0][0]:-1], np.array(module_np_pos[idx_start[0][0]:-1], dtype=float), marker='o', linestyle='-')
# plt.plot(module_np_time[idx_start[0][0]:-1], np.array(module_np_pos[idx_start[0][0]:-1], dtype=float))
# plt.title('Position vs. Timestamp for Module ' + MODULE)
# plt.xlabel('Timestamp')
# plt.ylabel('Position')
# # plt.grid(True)
# # plt.savefig("neuron_graph/Module "+ MODULE + " Position-Time.png")

# plt.figure(figsize=(12, 6))
plt.subplot(4, 1, 3)
# plt.plot(module_np_time[idx_start[0][0]:-1], np.array(module_np_load[idx_start[0][0]:-1], dtype=float), marker='o', linestyle='-')
plt.plot(module_np_time[idx_start[0][0]:-1], np.array(module_np_load[idx_start[0][0]:-1], dtype=float))
plt.title('Load vs. Timestamp for Module ' + MODULE)
plt.xlabel('Timestamp')
plt.ylabel('Load')
# plt.grid(True)
# plt.savefig("neuron_graph/Module "+ MODULE + " Load-Time.png")


# plt.figure(figsize=(12, 6))
plt.subplot(4, 1, 4)
# plt.plot(module_ni_time[idx_start[0][0]:-1], np.array(module_ni_phase[idx_start[0][0]:-1], dtype=float), marker='o', linestyle='-')
plt.plot(module_ni_time[idx_start[0][0]:-1], np.array(module_ni_phase[idx_start[0][0]:-1], dtype=float))

plt.title('Phase vs. Timestamp for Module ' + MODULE)
plt.xlabel('Timestamp')
plt.ylabel('Phase')
# plt.grid(True)
# plt.savefig("neuron_graph/Module "+ MODULE + " Phase-Time.png")
plt.show()
# plt.savefig("Module "+ MODULE + " Data.png")
