import re
import json
import os
import sys

# Stores all the overall scores of the left and right sensor into a json file. 
# If remove_timeout is set to True, measurements where a timeout occurs are not included in the data set.
# Script has to be executed in the locate where the measurement folders reside
def extract_overall_scores():
    
    # Define a regular expression pattern to match the measurement lines
    pattern = r'(\d+\.\d+): Sample: (\d+), Intra presence score: (\d+), Inter presence score: (\d+), Distance \(mm\): (\d+)'

    # List to store the extracted data
    measurements_left = []
    measurements_right = []

    # Open and read the left sensor file
    with open("sensor_left.txt", 'r') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                # Extract values from the matched line
                timestamp, sample, intra_score, inter_score, distance = match.groups()
                
                # Convert the values to appropriate data types if needed
                timestamp = float(timestamp)
                intra_score = int(intra_score)
                inter_score = int(inter_score)
                distance = int(distance)
                
                # Create a dictionary to store the data
                measurement_data = {
                    'timestamp': timestamp,
                    'intra_score': intra_score,
                    'inter_score': inter_score,
                    'distance': distance
                }
                
                # Append the data to the measurements list
                measurements_left.append(measurement_data)
    
    # Open and read the right sensor file
    with open("sensor_right.txt", 'r') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                # Extract values from the matched line
                timestamp, sample, intra_score, inter_score, distance = match.groups()
                
                # Convert the values to appropriate data types if needed
                timestamp = float(timestamp)
                intra_score = int(intra_score)
                inter_score = int(inter_score)
                distance = int(distance)
                
                # Create a dictionary to store the data
                measurement_data = {
                    'timestamp': timestamp,
                    'intra_score': intra_score,
                    'inter_score': inter_score,
                    'distance': distance
                }
                
                # Append the data to the measurements list
                measurements_right.append(measurement_data)

    # Serialize and save the variable to a JSON file
    with open('left_sensor_passages_overall.json', 'w') as file:
        json.dump(measurements_left, file)
    with open('right_sensor_passages_overall.json', 'w') as file:
        json.dump(measurements_right, file)


# Stores all the depth scores of the left and right sensor into a json file. 
# If remove_timeout is set to True, measurements where a timeout occurs are not included in the data set.
# Script has to be executed in the locate where the measurement folders reside
def extract_depth_scores():
    
    # Define a regular expression pattern to match the measurement lines
    pattern_intra = r'(\d+\.\d+): Intra values of sample \d+: (.+)'
    pattern_inter = r'(\d+\.\d+): Inter values of sample \d+: (.+)'
       
    # List to store the extracted data
    measurements_left_intra = []
    measurements_left_inter = []
    measurements_right_intra = []
    measurements_right_inter = []

    # Open and read the left sensor file
    with open("sensor_left.txt", 'r') as file:
        for line in file:
            match_intra = re.match(pattern_intra, line)
            match_inter = re.match(pattern_inter, line)
            if match_intra:
                # Extract values from the matched line
                timestamp, scores_str = match_intra.groups()
                # Convert string to list with numbers
                scores = [int(match.group()) for match in re.finditer(r'\d+', scores_str)]
                
                
                # Convert the values to appropriate data types if needed
                timestamp = float(timestamp)
                intra_scores = [int(score) for score in scores]
                
                # Create a dictionary to store the data
                measurement_data = {
                    'timestamp': timestamp,
                    'intra_scores': intra_scores,
                }
                
                # Append the data to the measurements list
                measurements_left_intra.append(measurement_data)
                
            elif match_inter:
                # Extract values from the matched line
                timestamp, scores_str = match_inter.groups()
                # Convert string to list with numbers
                scores = [int(match.group()) for match in re.finditer(r'\d+', scores_str)]
                
                # Convert the values to appropriate data types if needed
                timestamp = float(timestamp)
                inter_scores = [int(score) for score in scores]
                
                # Create a dictionary to store the data
                measurement_data = {
                    'timestamp': timestamp,
                    'inter_scores': inter_scores,
                }
                
                # Append the data to the measurements list
                measurements_left_inter.append(measurement_data)
        
        
    # Open and read the right sensor file
    with open("sensor_right.txt", 'r') as file:
        for line in file:
            match_intra = re.match(pattern_intra, line)
            match_inter = re.match(pattern_inter, line)
            if match_intra:
                # Extract values from the matched line
                timestamp, scores_str = match_intra.groups()
                # Convert string to list with numbers
                scores = [int(match.group()) for match in re.finditer(r'\d+', scores_str)]
                
                # Convert the values to appropriate data types if needed
                timestamp = float(timestamp)
                intra_scores = [int(score) for score in scores]
                
                # Create a dictionary to store the data
                measurement_data = {
                    'timestamp': timestamp,
                    'intra_scores': intra_scores,
                }
                
                # Append the data to the measurements list
                measurements_right_intra.append(measurement_data)
                
            if match_inter:
                # Extract values from the matched line
                timestamp, scores_str = match_inter.groups()
                # Convert string to list with numbers
                scores = [int(match.group()) for match in re.finditer(r'\d+', scores_str)]
                
                # Convert the values to appropriate data types if needed
                timestamp = float(timestamp)
                inter_scores = [int(score) for score in scores]
                
                # Create a dictionary to store the data
                measurement_data = {
                    'timestamp': timestamp,
                    'inter_scores': inter_scores,
                }
                
                # Append the data to the measurements list
                measurements_right_inter.append(measurement_data)

    # Serialize and save the variable to a JSON file
    with open('left_sensor_passages_intra_depth.json', 'w') as file:
        json.dump(measurements_left_intra, file)
    with open('right_sensor_passages_intra_depth.json', 'w') as file:
        json.dump(measurements_right_intra, file)
    with open('left_sensor_passages_inter_depth.json', 'w') as file:
        json.dump(measurements_left_inter, file)
    with open('right_sensor_passages_inter_depth.json', 'w') as file:
        json.dump(measurements_right_inter, file)


def main():
    directory = "measurement_18/"
    os.chdir(directory)
    extract_overall_scores()
    extract_depth_scores()

# The following block ensures that the main function is called only when the script is run, not when it's imported as a module
if __name__ == "__main__":
    main()