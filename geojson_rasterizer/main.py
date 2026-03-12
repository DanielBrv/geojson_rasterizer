import json
import os.path
import directory_dict
# save states as serparate geojson files

# select states
# Reads in json containing list of states that have been selected by user
def select_states() -> list:
    print("reading states from selected_states.json")
    states = []
    try:
        # opening json containing states that will be processed
        with open('../geojson/selected_states.json') as file:
            states = json.load(file)
    except FileNotFoundError:
        print("Error: The file 'selected_states.json' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
    # list of states from  json
    return states       

def open_geojson(states: list):
    for state in states:
        if state not in directory_dict.us_states_path:
            print(f'Error: {state} is not a valid state')
            continue

        file_path = directory_dict.us_states_path[state]
        if os.path.exists("../geojson/united_states/" + file_path):

            print(f'{state} geojson file found')
        else:
            print(f'Error: {state} geojson file not found')

open_geojson(select_states())
# parse polygons

# calc bounding box

# ray casting

# result