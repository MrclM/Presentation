import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json

# Load the video
video_path = 'output.avi'  # Change this to your AVI video file
cap = cv2.VideoCapture(video_path)

# Load the sensor data from JSON files
with open('single_mes__Left.json') as f:
    sensor_data_left = json.load(f)

with open('single_mes__Right.json') as f:
    sensor_data_right = json.load(f)

# Extract data
sensor_df_left = pd.DataFrame({
    'intra': sensor_data_left["intra"],
    'inter': sensor_data_left["inter"],
    'time': sensor_data_left["time"],
    'recalc': sensor_data_left["recalc"],
    'dist': sensor_data_left["dist"]
})

sensor_df_right = pd.DataFrame({
    'intra': sensor_data_right["intra"],
    'inter': sensor_data_right["inter"],
    'time': sensor_data_right["time"],
    'recalc': sensor_data_right["recalc"],
    'dist': sensor_data_right["dist"]
})

# Gate sensors for left
opening_left = [m['opening_sensor'] for m in sensor_data_left["sensors_old"]]
presence_control_left = [m['presence_control_sensor'] for m in sensor_data_left["sensors_old"]]
closing_left = [m['closing_sensor'] for m in sensor_data_left["sensors_old"]]
time_pillar_left = [m['timestamp'] for m in sensor_data_left["sensors_old"]]

# Gate sensors for right
opening_right = [m['opening_sensor'] for m in sensor_data_right["sensors_old"]]
presence_control_right = [m['presence_control_sensor'] for m in sensor_data_right["sensors_old"]]
closing_right = [m['closing_sensor'] for m in sensor_data_right["sensors_old"]]
time_pillar_right = [m['timestamp'] for m in sensor_data_right["sensors_old"]]

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

# Create a VideoWriter object to save the output video
output_path = 'overlay.avi'  # Change this to your desired output file
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Using XVID codec for AVI files
out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

# Create subplots for the sensor data
plt.ion()
fig, axs = plt.subplots(2, 1, figsize=(6, 6))

# Function to update the subplots
def update_plots(frame_time):
    for ax in axs:
        ax.clear()

    # Plot for left sensor data
    data_left = sensor_df_left[sensor_df_left['time'] <= frame_time]
    axs[0].plot(data_left['time'], data_left['intra'], 'r-')
    axs[0].set_xlim(0, duration)
    axs[0].set_ylim(sensor_df_left['inter'].min(), sensor_df_left['intra'].max())
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('Left Sensor Value')

    # Plot for right sensor data
    data_right = sensor_df_right[sensor_df_right['time'] <= frame_time]
    axs[1].plot(data_right['time'], data_right['inter'], 'b-')
    axs[1].set_xlim(0, duration)
    axs[1].set_ylim(sensor_df_right['inter'].min(), sensor_df_right['inter'].max())
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Right Sensor Value')

    fig.canvas.draw()
    # Convert plot to image
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return img

frame_number = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_time = frame_number / fps

    # Update plots
    plot_img = update_plots(frame_time)

    # Resize plot image to match the video frame size
    plot_img = cv2.resize(plot_img, (frame.shape[1], frame.shape[0]))

    # Overlay the plot on the video frame
    overlay_frame = cv2.addWeighted(frame, 0.7, plot_img, 0.3, 0)

    # Write the frame to the output video
    out.write(overlay_frame)

    frame_number += 1

# Release everything
cap.release()
out.release()
plt.ioff()
plt.close(fig)
