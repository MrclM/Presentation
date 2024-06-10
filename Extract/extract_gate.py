import re
import json
import os
import sys

# Regular expression pattern to match the desired pattern
pattern_sensor_left = r'(\d+\.\d+): SRC: 0x53, DST: 0x0, MESS: PDI (\w+)'
pattern_barrier_left = r'^(\d+\.\d+): SRC: 0x53, DST: 0x1, MESS: R00 (\d+) 0'
pattern_sensor_right = r'(\d+\.\d+): SRC: 0x52, DST: 0x0, MESS: PDI (\w+)'
pattern_barrier_right = r'^(\d+\.\d+): SRC: 0x52, DST: 0x1, MESS: R00 (\d+) 0'
pattern_closing_time = r'^(\d+\.\d+): SRC: 0x52, DST: 0x53, MESS: GSO 3'


def set_levels(pdi_value):
     # Presence and control sensor are in software treated as the same signal
    if(pdi_value == "2A2C2E"):
        opening = False
        presence_control = False
        closing = False
    elif(pdi_value == "2A2D2E"):
        opening = True
        presence_control = False
        closing = False
    elif(pdi_value == "2A2C2F"):
        opening = False
        presence_control = True
        closing = False
    elif(pdi_value == "2B2C2E"):
        opening = False
        presence_control = False
        closing = True
    elif(pdi_value == "2B2C2F"):
        opening = False
        presence_control = True
        closing = True
    elif(pdi_value == "2A2D2F"):
        opening = True
        presence_control = True
        closing = False
    elif(pdi_value == "2B2D2F"):
        opening = True
        presence_control = True
        closing = True
    #TODO: Confirm this is correct, as it only has been added as it was missing without any checking
    elif(pdi_value == "2B2D2E"):
        opening = True
        presence_control = False
        closing = True
    
    return opening, presence_control, closing

# Stores the sensor and barrier levels of all passages in files.
# remove_timeout is set to True by default, this way measurements where a timeout 
# occurs are skipped
def extract_sensor_levels():
    
    sensors_left = []
    sensors_right = []

    
    file_path = os.path.join(os.getcwd(), 'old_system.txt')

    with open(file_path, 'r') as file:   
        for line in file:
            match_sensors_left = re.search(pattern_sensor_left, line)
            match_sensors_right = re.search(pattern_sensor_right, line)

            if match_sensors_left:
                timestamp, pdi_value = match_sensors_left.groups()
                timestamp = float(timestamp)  # Convert timestamp to float
                
                opening, presence_control, closing = set_levels(pdi_value)
                
                sensor_data = {
                    'timestamp' : timestamp,
                    'opening_sensor' : opening,
                    'presence_control_sensor' : presence_control,
                    'closing_sensor' : closing
                }
                
                sensors_left.append(sensor_data)
                #Match already found, skip search for barrier pattern
                continue

        
            elif match_sensors_right:
                timestamp, pdi_value = match_sensors_right.groups()
                timestamp = float(timestamp)  # Convert timestamp to float
                
                opening, presence_control, closing = set_levels(pdi_value)
                
                sensor_data = {
                    'timestamp' : timestamp,
                    'opening_sensor' : opening,
                    'presence_control_sensor' : presence_control,
                    'closing_sensor' : closing
                }
                
                sensors_right.append(sensor_data)
                #Match already found, skip search for barrier pattern
                continue

    # Serialize and save the variable to a JSON file
    with open('left_sensors_old.json', 'w') as file:
        json.dump(sensors_left, file)
    with open('right_sensors_old.json', 'w') as file:
        json.dump(sensors_right, file)


# Stores the sensor and barrier levels of all passages in files.
# remove_timeout is set to True by default, this way measurements where a timeout 
# occurs are skipped
def extract_barrier_levels():
  
    barriers_left = []
    barriers_right = []

    file_path = os.path.join(os.getcwd(), 'old_system.txt')

    with open(file_path, 'r') as file:   
        for line in file:
            match_barriers_left = re.search(pattern_barrier_left, line)
            match_barriers_right = re.search(pattern_barrier_right, line)

            if match_barriers_left:
                timestamp, barrier_state = match_barriers_left.groups()
                timestamp = float(timestamp)  # Convert timestamp to float
                
                #opening, presence_control, closing = set_levels(pdi_value)
                
                barrier_data = {
                    'timestamp' : timestamp,
                    'barrier_state' : barrier_state
                }
                    
                barriers_left.append(barrier_data)
                #Match already found, skip search for barrier pattern
                continue

            if match_barriers_right:
                timestamp, barrier_state = match_barriers_right.groups()
                timestamp = float(timestamp)  # Convert timestamp to float
                
                #opening, presence_control, closing = set_levels(pdi_value)
                
                barrier_data = {
                    'timestamp' : timestamp,
                    'barrier_state' : barrier_state
                }
                    
                barriers_right.append(barrier_data)
                #Match already found, skip search for barrier pattern
                continue

    # Serialize and save the variable to a JSON file
    with open('left_barrier.json', 'w') as file:
        json.dump(barriers_left, file)
    with open('right_barrier.json', 'w') as file:
        json.dump(barriers_right, file)


# Extracts the closing time. All timeout measurements are ignored.
def extract_closing_time():
       
    file_path = os.path.join(os.getcwd(), 'old_system.txt')

    with open(file_path, 'r') as file:
        found = False   
        for line in file:
            match = re.search(pattern_closing_time, line)
            if match:
                timestamp, = match.groups()
                timestamp = float(timestamp)
                found = True
                break
            
        if found is False:
            print("No closing timestamp of the old system found!")
            timestamp = 0
        
    with open('closing_timestamp.json', 'w') as file:
        json.dump(timestamp, file)
    
    
def main():
    # Navigate to measurement directory
    
    directory = "measurement_18/"
    os.chdir(directory)
    extract_sensor_levels()
    extract_barrier_levels()
    extract_closing_time()


# The following block ensures that the main function is called only when the script is run, not when it's imported as a module
if __name__ == "__main__":
    main()