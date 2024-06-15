import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os

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

# Gate sensors (assuming you have 'opening_sensor', 'presence_control_sensor', 'closing_sensor', and 'timestamp' in your JSON data)
# For simplicity, the original JSON data structure used in your example is maintained
# However, the loop for extracting sensor data was incorrect
# So we can create the arrays without unnecessary loops

# Gate sensors left (assuming all sensors and timestamps are present in the JSON data)
opening_left = sensor_data_left.get('opening_sensor', [])
presence_control_left = sensor_data_left.get('presence_control_sensor', [])
closing_left = sensor_data_left.get('closing_sensor', [])
time_pillar_left = sensor_data_left.get('timestamp', [])

# Gate sensors right (assuming all sensors and timestamps are present in the JSON data)
opening_right = sensor_data_right.get('opening_sensor', [])
presence_control_right = sensor_data_right.get('presence_control_sensor', [])
closing_right = sensor_data_right.get('closing_sensor', [])
time_pillar_right = sensor_data_right.get('timestamp', [])

# Get the maximum recorded time
max_time = max(sensor_df_left['time'].max(), sensor_df_right['time'].max())

# Define the offset (in seconds) to sync the video with sensor data
offset = 0.6  # Adjust this value based on your specific offset

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

# Calculate the frame number to stop at
max_frame_number = int((max_time + offset) * fps)

# Create a VideoWriter object to save the output video
output_path = 'overlay.avi'  # Change this to your desired output file
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Using XVID codec for AVI files
out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

# Create subplots for the sensor data
plt.ion()
fig = plt.figure(figsize=(10, 8))
gs = fig.add_gridspec(3, 2)

# Create axes
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[0, 1])
ax4 = fig.add_subplot(gs[1, 1])
ax5 = fig.add_subplot(gs[2, 1])

axs = [ax1, ax2, ax3, ax4, ax5]

# Function to update the subplots
def update_plots(frame_time):
    # Clear all axes
    for ax in axs:
        ax.clear()

    # Adjust frame time by subtracting the offset
    adjusted_time = frame_time - offset

    # Plot for left sensor data
    data_left = sensor_df_left[sensor_df_left['time'] <= adjusted_time]
    data_right = sensor_df_right[sensor_df_right['time'] <= adjusted_time]
    
    axs[0].plot(data_left['time'], data_left['intra'], 'r-')
    axs[0].set_xlim(0, max_time)
    axs[0].set_ylim(0, sensor_df_left['intra'].max())
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('Left Intra')

    axs[1].plot(data_left['time'], data_left['inter'], 'g-')
    axs[1].set_xlim(0, max_time)
    axs[1].set_ylim(0, sensor_df_left['inter'].max())
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Left Inter')

    # Intra Score
    axs[2].plot(data_left['time'], data_left['intra'], label='Left')
    axs[2].plot(data_right['time'], data_right['intra'], label='Right')
    axs[2].set_xlim(0, max_time)
    axs[2].set_ylim(0, max(sensor_df_left['intra'].max(), sensor_df_right['intra'].max()))
    axs[2].set_title('Intra Score')

    axes3 = axs[3].twinx()
    axs[3].yaxis.label.set_color('C0')
    axs[3].tick_params(axis='y', labelcolor='C0')  # Set the color of the right y-axis labels
    axes3.tick_params(axis='y', labelcolor='C1')  # Set the color of the right y-axis labels
    axs[3].plot(data_left['time'], data_left['inter'], label='Left')
    axes3.plot(data_right['time'], data_right['inter'], label='Right', color='C1')
    axs[3].set_xlim(0, max_time)
    axs[3].set_ylim(0, sensor_df_left['inter'].max())
    axes3.set_ylim(0, sensor_df_right['inter'].max())
    # Combine legend handles and labels from both axes
    handles, labels = axs[3].get_legend_handles_labels()
    handles2, labels2 = axes3.get_legend_handles_labels()
    handles += handles2
    labels += labels2
    axs[3].set_title('Inter Score')  
    # Create a single legend
    axs[3].legend(handles, labels, loc='upper left')

    axs[4].plot(data_left['time'], data_left['recalc'], label='Left')
    axs[4].plot(data_right['time'], data_right['recalc'], label='Right')
    axs[4].set_xlim(0, max_time)
    axs[4].set_ylim(0, max(sensor_df_left['recalc'].max(), sensor_df_right['recalc'].max()))
    axs[4].set_xlabel('Time (s)')
    axs[4].legend()

    fig.canvas.draw()
    # Convert plot to image
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return img

# Create directory to save images
output_dir = 'frames'
os.makedirs(output_dir, exist_ok=True)

frame_number = 0
while cap.isOpened() and frame_number <= max_frame_number:
    ret, frame = cap.read()
    if not ret:
        break

    frame_time = frame_number / fps

    # Update plot
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
