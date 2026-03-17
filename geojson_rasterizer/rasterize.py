import json
def load_geojson(geojson):
    if geojson.get("type") != "GeometryCollection":
        return
    geometries = geojson.get("geometries")[0]
    if not geometries:
        return
    polygon_type = geometries.get("type")
    coordinates = geometries.get("coordinates")
    if polygon_type == "Polygon":
        coordinates, = coordinates
        bounding_box(coordinates, 0)
    elif polygon_type == "MultiPolygon":
        pass
    else:
        return
    return

# creates polygon representing the bounding box of given geojson
def bounding_box(polygon, distance):
    # finding bounds 
    top = float("-inf")
    bottom = float("inf")
    left = float("inf")
    right = float("-inf")
    for longitude, latitude in polygon:
        left = min(left, longitude)
        right = max(right, longitude)
        top = max(top, latitude)
        bottom = min(bottom, latitude)

    bounds = [
            [left, top],
            [right, top],
            [right, bottom],
            [left, bottom],
            [left, top]
        ]
    
    points = []
    

    return 

# writes bounding box to a file for debug
def output(bounds):
    bound_box = {"type":"GeometryCollection",
        "geometries": [
            {
                "type":"Polygon",
                "coordinates":[
                    bounds
                ]
            }

    ]}

    try:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(bound_box, f, indent=4)
        print(f"Successfully wrote JSON to output.json")
    except OSError as e:
        print(f"File error: {e}")
    except TypeError:
        print("Error: Data provided is not JSON serializable.")

    
  