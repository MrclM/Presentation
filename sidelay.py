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

with open('interpolated_data.json') as f:
    sensor_data_old = json.load(f)

# Extract data
sensor_df_left = pd.DataFrame({
    'intra': sensor_data_left["intra"],
    'inter': sensor_data_left["inter"],
    'time': sensor_data_left["time"],
    'recalc': sensor_data_left["recalc"],
    'dist': sensor_data_left["dist"],
    'presence_control': sensor_data_old["presence_control_left"],
    'closing': sensor_data_old["closing_left"]
})

sensor_df_right = pd.DataFrame({
    'intra': sensor_data_right["intra"],
    'inter': sensor_data_right["inter"],
    'time': sensor_data_right["time"],
    'recalc': sensor_data_right["recalc"],
    'dist': sensor_data_right["dist"],
    'presence_control': sensor_data_old["presence_control_right"],
    'closing': sensor_data_old["closing_right"]
})

# Get the maximum recorded time
max_time = max(sensor_df_left['time'].max(), sensor_df_right['time'].max())

# Define the offset (in seconds) to sync the video with sensor data
offset = 0.6  # Adjust this value based on your specific offset

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps
video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calculate the frame number to stop at
max_frame_number = int((max_time + offset) * fps)

# Set the new dimensions for the output video (16:9 aspect ratio)
output_height = video_height
output_width = int(output_height * 16 / 9)

# Create a VideoWriter object to save the output video
output_path = 'overlay.avi'  # Change this to your desired output file
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Using XVID codec for AVI files
out = cv2.VideoWriter(output_path, fourcc, fps, (output_width, output_height))

# Create subplots for the sensor data
plt.ion()
fig, axs = plt.subplots(3, 1, figsize=(6, 12))

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
    
    # Intra Score
    axs[0].plot(data_left['time'], data_left['intra'], label='Left')
    axs[0].plot(data_right['time'], data_right['intra'], label='Right')
    axs[0].set_xlim(0, max_time)
    axs[0].set_ylim(0, max(sensor_df_left['intra'].max(), sensor_df_right['intra'].max()))
    axs[0].set_title('Intra Score')
    axs[0].legend(loc='upper right')

    # Inter Score
    axes3 = axs[1].twinx()
    axs[1].yaxis.label.set_color('C0')
    axs[1].tick_params(axis='y', labelcolor='C0')  # Set the color of the right y-axis labels
    axes3.tick_params(axis='y', labelcolor='C1')  # Set the color of the right y-axis labels
    axs[1].plot(data_left['time'], data_left['inter'], label='Left')
    axes3.plot(data_right['time'], data_right['inter'], label='Right', color='C1')
    axs[1].set_xlim(0, max_time)
    axs[1].set_ylim(0, sensor_df_left['inter'].max())
    axes3.set_ylim(0, sensor_df_right['inter'].max())
    # Combine legend handles and labels from both axes
    handles, labels = axs[1].get_legend_handles_labels()
    handles2, labels2 = axes3.get_legend_handles_labels()
    handles += handles2
    labels += labels2
    axs[1].set_title('Inter Score')  
    # Create a single legend
    axs[1].legend(handles, labels, loc='upper right')

    # Distance
    axs[2].plot(data_left['time'], data_left['recalc'], label='Left')
    axs[2].plot(data_right['time'], data_right['recalc'], label='Right')
    axs[2].set_xlim(0, max_time)
    axs[2].set_ylim(0, max(sensor_df_left['recalc'].max(), sensor_df_right['recalc'].max()))
    axs[2].set_xlabel('Time [s]')
    axs[2].legend(loc='upper right')
    axs[2].set_title('Distance [mm]')

    fig.tight_layout()
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

    # Create a white background
    white_bg = np.ones((video_height, output_width - video_width, 3), dtype=np.uint8) * 255

    # Resize plot image to fit the additional width
    plot_img_resized = cv2.resize(plot_img, (output_width - video_width, video_height))

    # Combine the video frame and the white background
    combined_frame = np.hstack((frame, white_bg))

    # Overlay the plot on the combined frame
    combined_frame[:, video_width:] = plot_img_resized

    # Write the frame to the output video
    out.write(combined_frame)

    frame_number += 1

# Release everything
cap.release()
out.release()
plt.ioff()
plt.close(fig)
