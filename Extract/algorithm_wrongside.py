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

closing_time = []



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


def algo_statemachine(intra_th, inter_th):
    global left_time 
    global left_intra
    global left_inter
    global left_dist
    global right_time
    global right_intra
    global right_inter
    global right_dist
    
    # Minimum required distance on both sensor to close the barriers at a straight distance
    STRAIGHT_EXIT_DISTANCE = 350
    # Minimum required close distance for sideway passage 
    SIDEWAY_EXIT_DISTANCE_CLOSE = 250
    # Minimum required far distance for sideway passage 
    SIDEWAY_EXIT_DISTANCE_FAR = 480
    # Distance to check for wrong side passages
    WRONG_SIDE_DISTANCE = 390
    
    left_dist_recalc = recalc_distance(intra_th, inter_th, "Left")
    right_dist_recalc = recalc_distance(intra_th, inter_th, "Right")
    
    class State(Enum):
        WAIT_FOR_PRESENCE, PRESENCE, PASSAGE = range(3)
    
    # Determine number of samples. Choose the lower number of both sides if they do not have the same length
    # to prevent a segfault.
    measurement_samples = len(left_intra) if len(left_intra) < len(right_intra) else len(right_intra)
    
    cur_state = State.WAIT_FOR_PRESENCE
    next_state = State.WAIT_FOR_PRESENCE
    
    INTRA_THRESH_ADD = 1500
    REQ_CONS_PRESENCES = 10
    REQ_INTRA_EXCEEDED = 3
    
    # Counts how many times the additional intra threshold is exceeded.
    # The additional threshold is necessary to verify an actual person made the passage.
    # The normal intra threshold is set relatively low to be sure the distance is tracked long enough.
    intra_exceeded = 0
    # Make sure an certain amount of consecutive presents is detected to be sure that no false detection
    # triggers a passage.
    cons_presences = 0
    
    # If algorithm don't recognize a passage, a very high value is assigend as closing time
    closing_t = 9999
    
    # Is set true if an passage from the exit side is detected
    wrong_way_passage = False
    
    # Varible that tells us if initial distance already has been checked
    initial_distance_checked = False
    
    for j in range(measurement_samples):
        intra_l_cur = left_intra[j]
        inter_l_cur = left_inter[j]
        intra_r_cur = right_intra[j]
        inter_r_cur = right_inter[j]
        dist_l_cur = left_dist_recalc[j]
        dist_r_cur = right_dist_recalc[j]
        
        # Set stated which was determined
        cur_state = next_state
        
        # Python does not require a break after every case. 
        # Using a break exits the loop completely, so continue is used if an early exit from a case is necessary
        match cur_state:
            
            case State.WAIT_FOR_PRESENCE:
                # Reset presence related counters when (re-)enter the state
                intra_exceeded = 0
                cons_presences = 0
                
                initial_distance_checked = False
                
                # Check if presence is detected at both sensors
                if (intra_l_cur > intra_th or inter_l_cur > inter_th) and (intra_r_cur > intra_th or inter_r_cur > inter_th):
                    # Stay in wait for presence until person which entered from wrong side leaves the detection area gain
                    if wrong_way_passage is True:
                        next_state = State.WAIT_FOR_PRESENCE
                    else:
                        next_state = State.PRESENCE
                else:
                    # No person in the detection zone, set wrong_way_passage to false
                    wrong_way_passage = False
                    next_state = State.WAIT_FOR_PRESENCE
            
            case State.PRESENCE:
                # Check if presence is detected at both sensors
                if (intra_l_cur > intra_th or inter_l_cur > inter_th) and (intra_r_cur > intra_th or inter_r_cur > inter_th):
                    next_state = State.PRESENCE
                else:
                    next_state = State.WAIT_FOR_PRESENCE
                    continue
                
                # Increment number of consecutive presences
                cons_presences += 1 
                
                # Determine if initial distance is above the threshold. Check that the intra score is exceeded to make sure
                # we don't use the distance of the moving flap pedals.
                if intra_l_cur > 1200 and intra_r_cur > 1200 and initial_distance_checked is False:
                    # Check for wrong side passage
                    if (dist_l_cur >= WRONG_SIDE_DISTANCE and dist_r_cur >= WRONG_SIDE_DISTANCE):# or ((dist_l_cur + dist_r_cur) >= 950):
                        # Wrong side distance detected
                        wrong_way_passage = True
                        next_state = State.WAIT_FOR_PRESENCE
                        continue
                    else:
                        initial_distance_checked = True
                    
                
                # Check if the additional threshold was exceeded
                if intra_l_cur > INTRA_THRESH_ADD or intra_r_cur > INTRA_THRESH_ADD:
                    intra_exceeded += 1
                
                # Can't go into next passage state if one of the requirements is not fullfiled  
                if cons_presences < REQ_CONS_PRESENCES or intra_exceeded < REQ_INTRA_EXCEEDED:
                    next_state = State.PRESENCE
                    continue
                
                # Go in next state if person has reached the required distance to the sensor
                if ((dist_l_cur >= STRAIGHT_EXIT_DISTANCE and dist_r_cur >= STRAIGHT_EXIT_DISTANCE) or \
                (dist_l_cur >= SIDEWAY_EXIT_DISTANCE_FAR and dist_r_cur >= SIDEWAY_EXIT_DISTANCE_CLOSE) or \
                (dist_l_cur >= SIDEWAY_EXIT_DISTANCE_CLOSE and dist_r_cur >= SIDEWAY_EXIT_DISTANCE_FAR)) and (intra_l_cur > intra_th and intra_r_cur > intra_th):
                    next_state = State.PASSAGE
                else:
                    next_state = State.PRESENCE
                
            case State.PASSAGE:
                # Append timestamp of previous measurement where passage was detected
                closing_t = (right_time[j - 1])
                break
            
            case _:
                print("Undefined State!")
                break
            
    if closing_t == 9999:
        print("No passage detected!")
        
    with open("closing_time.json", 'w') as file:
        json.dump(closing_t, file)

def main():
    
    directory = "measurement_18/"
    os.chdir(directory)
    
    extract_overall()

    algo_statemachine(1200, 2000)
    

# The following block ensures that the main function is called only when the script is run, not when it's imported as a module
if __name__ == "__main__":
    main()