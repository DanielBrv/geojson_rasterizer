import json
import math

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
        # bug where distance is 0 or negative
        box, points = bounding_box(coordinates, 25)
        feature_points = []
        for point in points:
            curr = {
                "type": "Point",
                "coordinates": point
            }
            feature_points.append(curr)
        output([coordinates], feature_points)
    elif polygon_type == "MultiPolygon":
        

        bbox = []
        points = []
        for polygon in coordinates:
            polygon, = polygon
            box, point = bounding_box(polygon, 5)
            bbox.append(box)
            points += point
        feature_points = []
        for point in points:
            curr = {
                "type": "Point",
                "coordinates": point
            }
            feature_points.append(curr)

        output(bbox, feature_points)

    else:
        return
    return

# creates polygon representing the bounding box of given geojson
def bounding_box(polygon, distance_km):
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

    bounding_box = [
            [left, top],
            [right, top],
            [right, bottom],
            [left, bottom],
            [left, top]
        ]
    # constructing grid of points points distance_km appart
    points = generate_grid([[left, bottom],[right, top]], distance_km)

    # Removing points outside of polygon
    points = filter_points(polygon, points)

    return bounding_box, points
    


# writes bounding box and points to a file for debug
def output(bounding_box, points):
    sjson_output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Bounding Box Grid"
            },
            "geometry": {
                "type": "GeometryCollection",
                "geometries": points + [{
                        "type": "Polygon",
                        "coordinates": [bounding_box]
                    }]
            }
            }
        ]
    }
    json_output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Bounding Box Grid"
            },
            "geometry": {
                "type": "GeometryCollection",
                "geometries": points + [{
                        "type": "MultiPolygon",
                        "coordinates": [bounding_box]
                    }]
            }
            }
        ]
    }

    try:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=4)
        print(f"Successfully wrote JSON to output.json")
    except OSError as e:
        print(f"File error: {e}")
    except TypeError:
        print("Error: Data provided is not JSON serializable.")


# Uses ray casting to test if some point is inside the polygon
# Counts how many times a ray passes through the polygons edges.
#
# The given point's latitude will be used as the ray. All edges of the polygon
# west of the given point are ignored

# If a ray passes through an even number of edges, it is assumed 
# the point is out side of the polygon and returns False. 
# Otherwise it is assumed the point is inside the polygon and func returns True 
def point_in_polygon(point, polygon):
    lon, lat = point
    inside = False

    n = len(polygon)

    for i in range(n):
        lon1, lat1 = polygon[i]
        lon2, lat2 = polygon[(i + 1) % n]

        # Check if the ray crosses the edge vertically
        if ((lat1 > lat) != (lat2 > lat)):
            # Compute intersection longitude
            intersect_lon = lon1 + (lat - lat1) * (lon2 - lon1) / (lat2 - lat1)

            if lon < intersect_lon:
                inside = not inside

    return inside

# removes points located outside of the original polygon
# Returns list of original polygons
def filter_points(polygon, points):
    filtered = []
    for point in points:
        if point_in_polygon(point, polygon):
            filtered.append(point)
    return filtered


def normalize_lon(lon):
    # Wrap longitude to [-180, 180]
    return ((lon + 180) % 360) - 180


def clamp_lat(lat):
    # Clamp latitude to [-90, 90]
    return max(-90, min(90, lat))


def move_point(lat, lon, distance_km, bearing_deg):
    R = 6371.0  # Earth radius in km
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    theta = math.radians(bearing_deg)
    d_div_r = distance_km / R

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d_div_r) +
        math.cos(lat1) * math.sin(d_div_r) * math.cos(theta)
    )

    lon2 = lon1 + math.atan2(
        math.sin(theta) * math.sin(d_div_r) * math.cos(lat1),
        math.cos(d_div_r) - math.sin(lat1) * math.sin(lat2)
    )

    return clamp_lat(math.degrees(lat2)), normalize_lon(math.degrees(lon2))



# Generates grid of points inside of bounding box
# starts at the most western longitude, creating line of points 
# -along current latitude d_km km away.
# 
# Once the points fall off the right side of the bounding box,
# line restarts on left side of bounding box d_km km south from previous latitude
def generate_grid(bbox, d_km):
    
    # bbox: [[min_lon, min_lat], [max_lon, max_lat]]
    

    min_lon, min_lat = bbox[0]
    max_lon, max_lat = bbox[1]

    points = []

    current_lat = max_lat

    while current_lat >= min_lat:

        current_lon = min_lon

        while True:
            
            #point = {
            #    "type": "Point",
            #    "coordinates": [current_lon, current_lat]
            #}
            #points.append(point)
            points.append([current_lon, current_lat])

            # move east
            next_lat, next_lon = move_point(current_lat, current_lon, d_km, 90)

            # stop if we passed right boundary
            if (min_lon <= max_lon and next_lon > max_lon) or \
               (min_lon > max_lon and next_lon < min_lon):  # dateline case
                break

            current_lon = next_lon

        # move south from westmost longitude
        next_lat, _ = move_point(current_lat, min_lon, d_km, 180)

        if next_lat < min_lat:
            break

        current_lat = next_lat

    return points

    
  