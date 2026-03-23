import json
import os.path
import directory_dict
import rasterize
# save states as serparate geojson files

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


# Reads in json file located at path and returns 
def open_geojson(path:str) -> json:
    geojson = {}
    try:
        # opening json located at path
        with open(path) as file:
            geojson = json.load(file)
    except FileNotFoundError:
        print("Error: The file was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
    # geojson from file located at path
    return geojson

# spacing between points in kilometers
distance_km = 4
states = select_states()
for state in states:
    if state not in directory_dict.us_states_path:
        print(f'Error: {state} is not a valid state')
        continue

    file_path = "../geojson/united_states/" + directory_dict.us_states_path[state]
    if not os.path.exists(file_path):
        print(f'Error: {state} geojson file not found')
        continue
    geojson = open_geojson(file_path)
    rasterize.load_geojson(geojson, distance_km)
    #print(json.dumps(geojson))

# parse polygons

# calc bounding box

# ray casting

# result