import re
import json
import os
from enum import Enum
import statistics
import sys


# Define global variables
left_overall = []
right_overall = []
left_sensor_intra_depth = []
right_sensor_intra_depth = []
left_sensor_inter_depth = []
right_sensor_inter_depth = []
left_intra_depth = []
right_intra_depth = []
left_inter_depth = []
right_inter_depth = []
left_time = []
left_intra = []
left_inter = []
left_dist = []
right_time = []
right_intra = []
right_inter = []
right_dist = []
left_sensors_old = []
right_sensors_old = []

left_barrier_state = []
right_barrier_state = []
left_barrier_time = []
right_barrier_time = []

closing_time = []

def extract_single(threshold_intra, threshold_inter, side="Left"):
    
    recalc = recalc_distance(threshold_intra, threshold_inter, side)
    
    if side == "Left":
        intra = left_intra
        inter = left_inter
        dist = left_dist
        sensors_old = left_sensors_old
        time = left_time
        barrier_state = left_barrier_state
        barrier_time = left_barrier_time
    elif side == "Right":
        intra = right_intra
        inter = right_inter
        dist = right_dist
        sensors_old = right_sensors_old
        time = right_time
        barrier_state = right_barrier_state
        barrier_time = right_barrier_time
    else:
        print("Enter Left, Right or Both!")
    
    with open("closing_time.json", 'r') as file:
        closing_algo = json.load(file)

    close_time_gate = closing_gate
    close_time_algo = closing_algo
    
    data = {
        "intra": intra,
        "inter": inter,
        "dist": dist,
        "recalc": recalc,
        "time": time,
        "sensors_old": sensors_old,
        "close_time_gate": close_time_gate,
        "close_time_algo": close_time_algo,
        "barrier_state": barrier_state,
        "barrier_time": barrier_time
    }
    
    with open("single_mes_" + "_" + side + ".json", 'w') as json_file:
        json.dump(data, json_file, indent=4)
 

# Used to recalculate all distances with new thresholds. 
# The array with the recalculated distances is returned.
def recalc_distance(threshold_intra, threshold_inter, side="Left"):
    indexes_intra = []
    indexes_inter = []
    score_intra = []
    score_inter = []
    dist_intra = []
    dist_inter = []
    
    if side == "Left":
        intra_depth = left_intra_depth
        inter_depth = left_inter_depth
        intra = left_intra
        inter = left_inter
    elif side == "Right":
        intra_depth = right_intra_depth
        inter_depth = right_inter_depth   
        intra = right_intra
        inter = right_inter
    else:
        print("Enter either Left or Right!")
        return 
    
    dist_intra = []
    dist_inter = []
    indexes_intra = []
    indexes_inter = []
    
    # Determine distance based on intra score
    for mes in intra_depth:
        index = 0
        max_score = 0
        counter = 0
        for point in mes:
            if point > max_score:
                max_score = point
                index = counter 
            counter += 1

        # Store max score and its location
        indexes_intra.append(index)
        score_intra.append(max_score)
    
    for ind in indexes_intra:
        dist_intra.append(100 + ind*10)

    
    # Determine distance based on inter score
    for mes in inter_depth:
        index = 0
        max_score = 0
        counter = 0
        for point in mes:
            if point > max_score:
                max_score = point
                index = counter 
            counter += 1

        # Store max score and its location
        indexes_inter.append(index)
        score_inter.append(max_score)
    
    for ind in indexes_inter:
        dist_inter.append(100 + ind*10)
    
    # determine overall distance
    distance = []

    for i in range(len(intra)):
        # check if both scores are above the threshold
        if intra[i] > threshold_intra and inter[i] > threshold_inter:
            # use intra when both scores are above the threshold, like in 
            # https://github.com/acconeer/acconeer-python-exploration/blob/602e796b1f58807f3dafa1ee4046e0caa2338ddc/src/acconeer/exptool/a121/algo/presence/_processors.py#L448
            distance.append(100 + indexes_intra[i]* 10)

        # Only intra score is above the threshold
        elif intra[i] > threshold_intra:
            distance.append(100 + indexes_intra[i]* 10)
        # Only inter score is above the threshold
        elif inter[i] > threshold_inter:
            distance.append(100 + indexes_inter[i]* 10)
        # No score is above the threshold
        else:
            distance.append(0)
                
    return distance


# A slight variation of the already implemented algorithm used for tests with a single person
def extract_overall():
    global left_overall
    global right_overall
    global left_sensor_intra_depth
    global right_sensor_intra_depth
    global left_sensor_inter_depth
    global right_sensor_inter_depth
    global left_intra_depth
    global right_intra_depth
    global left_inter_depth
    global right_inter_depth
    global left_time 
    global left_intra
    global left_inter
    global left_dist
    global right_time
    global right_intra
    global right_inter
    global right_dist
    global closing_gate
    global left_sensors_old
    global right_sensors_old
    global closing_time
    global left_barrier_state
    global right_barrier_state
    global left_barrier_time
    global right_barrier_time

    # Load data from json files
    with open('left_sensor_passages_overall.json', 'r') as file:
        left_overall = json.load(file)
    with open('right_sensor_passages_overall.json', 'r') as file:
        right_overall = json.load(file)

    with open('left_sensor_passages_intra_depth.json', 'r') as file:
        left_sensor_intra_depth = json.load(file)
    with open('right_sensor_passages_intra_depth.json', 'r') as file:
        right_sensor_intra_depth = json.load(file)
    with open('left_sensor_passages_inter_depth.json', 'r') as file:
        left_sensor_inter_depth = json.load(file)
    with open('right_sensor_passages_inter_depth.json', 'r') as file:
        right_sensor_inter_depth = json.load(file)
    with open('closing_timestamp.json', 'r') as file:
        closing_gate = json.load(file)
    with open('left_sensors_old.json', 'r') as file:
        left_sensors_old = json.load(file)
    with open('right_sensors_old.json', 'r') as file:
        right_sensors_old = json.load(file)
    with open('closing_time.json', 'r') as file:
        closing_time = json.load(file)
    with open('left_barrier.json', 'r') as file:
        left_barrier = json.load(file)
    with open('right_barrier.json', 'r') as file:
        right_barrier = json.load(file)
    
    # Extract all data of left sensor
    for measurement in left_overall:
        left_time.append(measurement['timestamp'])
        left_intra.append(measurement['intra_score'])
        left_inter.append(measurement['inter_score'])
        left_dist.append(measurement['distance'])

    # Extract all data of right sensor
    for measurement in right_overall:
        right_time.append(measurement['timestamp'])
        right_intra.append(measurement['intra_score'])
        right_inter.append(measurement['inter_score'])
        right_dist.append(measurement['distance'])

    # Extract data from depth measurements, do not extract timestamps as they are useless because the data is printed after the actual measurement
    for measurement in left_sensor_intra_depth:
        left_intra_depth.append(measurement['intra_scores'])  

    for measurement in left_sensor_inter_depth:
        left_inter_depth.append(measurement['inter_scores'])  

    for measurement in right_sensor_intra_depth:
        right_intra_depth.append(measurement['intra_scores'])  

    for measurement in right_sensor_inter_depth:
        right_inter_depth.append(measurement['inter_scores'])  
        
    for measurement in left_barrier:
        left_barrier_state.append(measurement['barrier_state'])
        left_barrier_time.append(measurement['timestamp'])
        
    for measurement in right_barrier:
        right_barrier_state.append(measurement['barrier_state'])
        right_barrier_time.append(measurement['timestamp'])


def main():
    
    directory = "measurement_18/"
    os.chdir(directory)
    
    extract_overall()
    extract_single(1200, 2000, 'Left')
    extract_single(1200, 2000, 'Right')

    
# The following block ensures that the main function is called only when the script is run, not when it's imported as a module
if __name__ == "__main__":
    main()