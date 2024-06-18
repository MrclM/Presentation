import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    
def convert_bool_to_int(bool_array):
    """
    Convert an array of boolean values to integers (False -> 0, True -> 1).
    
    Parameters:
    - bool_array (list or numpy.ndarray): Array of boolean values
    
    Returns:
    - numpy.ndarray: Array of integers (0 for False, 1 for True)
    """
    # Convert the boolean array to integers using list comprehension
    int_array = [1 if x else 0 for x in bool_array]
    
    return int_array

def interpolate(values, timestamps, new_timestamps):
    # Convert lists to numpy arrays for easier handling
    timestamps = np.array(timestamps)
    values = np.array(values)
    new_timestamps = np.array(new_timestamps)
    
    interpolated_values = []
    
    # Iterate through each new timestamp
    for new_ts in new_timestamps:
        # Find indices of timestamps before and after new_ts
        idx = np.searchsorted(timestamps, new_ts)
        
        # Edge cases: new_ts is outside the range of timestamps
        if idx >= len(timestamps):
            interpolated_values.append(values[-1])  # Use the last value
        elif idx == 0:
            interpolated_values.append(values[0])   # Use the first value
        else:
            # Step interpolation: value remains constant until the next timestamp
            interpolated_values.append(values[idx - 1])
    
    return interpolated_values


# Load the sensor data from JSON files
with open('single_mes__Left.json') as f:
    sensor_data_left = json.load(f)

with open('single_mes__Right.json') as f:
    sensor_data_right = json.load(f)

sensors_old_left = sensor_data_left["sensors_old"]
sensors_old_right = sensor_data_right["sensors_old"]

radar_time_left = sensor_data_left["time"]
radar_time_right = sensor_data_right["time"]


# Gate sensors
opening_left = []
presence_control_left = []
closing_left = []
time_pillar_left = []
    
    
for measurement in sensors_old_left:
    opening_left.append(measurement['opening_sensor'])
    presence_control_left.append(measurement['presence_control_sensor'])
    closing_left.append(measurement['closing_sensor'])
    time_pillar_left.append(measurement['timestamp'])

# Gate sensors
print(time_pillar_left)
opening_right = []
presence_control_right = []
closing_right = []
time_pillar_right = []


for measurement in sensors_old_right:
    opening_right.append(measurement['opening_sensor'])
    presence_control_right.append(measurement['presence_control_sensor'])
    closing_right.append(measurement['closing_sensor'])
    time_pillar_right.append(measurement['timestamp'])

presence_control_left = convert_bool_to_int(presence_control_left)
closing_left = convert_bool_to_int(closing_left)
presence_control_right = convert_bool_to_int(presence_control_right)
closing_right = convert_bool_to_int(closing_right)

# Print or use the new interpolated values
presence_control_left_i = interpolate(presence_control_left, time_pillar_left, radar_time_left)
presence_control_right_i = interpolate(presence_control_right, time_pillar_right, radar_time_right)
closing_left_i = interpolate(closing_left, time_pillar_left, radar_time_left)
closing_right_i = interpolate(closing_right, time_pillar_right, radar_time_right)

print(type(presence_control_left_i))
# Combine into a dictionary for JSON storage
data = {
    "presence_control_left": presence_control_left_i,
    "presence_control_right": presence_control_right_i,
    "closing_left": closing_left_i,
    "closing_right": closing_right_i
}

# Write to JSON file
with open('interpolated_data.json', 'w') as json_file:
    json.dump(data, json_file, cls=NpEncoder, indent=4)