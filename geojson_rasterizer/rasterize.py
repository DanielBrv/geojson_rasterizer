def load_geojson(geojson):
    if geojson.get("type") != "GeometryCollection":
        return
    geometries = geojson.get("geometries")[0]
    if not geometries:
        return
    polygon_type = geometries.get("type")
    coordinates = geometries.get("coordinates")
    if polygon_type == "Polygon":
        print(coordinates)
    elif polygon_type == "MultiPolygon":
        pass
    else:
        return
    return

  