import json
import math
from pathlib import Path

BASE = Path(r"D:\oilspill_project")
PRED = BASE / "predictions"

INPUT = PRED / "drift_hindcast_wind.json"
OUTPUT = PRED / "origin_corridor.geojson"

BUFFER_KM = 10.0


def offset_point(lat, lon, north_km, east_km):
    new_lat = lat + north_km / 111.32

    meters_per_degree_lon = (
        111.32 * math.cos(math.radians(lat))
    )

    new_lon = lon + east_km / meters_per_degree_lon

    return new_lat, new_lon


with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

track = data["backward_track"]

left_side = []
right_side = []

for p in track:

    lat = p["latitude"]
    lon = p["longitude"]

    # Estimate local direction using neighbouring points
    idx = track.index(p)

    if idx == 0:
        p2 = track[1]
    else:
        p2 = track[idx - 1]

    dlat = lat - p2["latitude"]
    dlon = lon - p2["longitude"]

    # Convert direction to approximate metres
    north = dlat * 111.32
    east = dlon * 111.32 * math.cos(math.radians(lat))

    length = math.sqrt(north ** 2 + east ** 2)

    if length == 0:
        north = 1
        east = 0
        length = 1

    # Perpendicular vector
    perp_north = -east / length
    perp_east = north / length

    left_lat, left_lon = offset_point(
        lat,
        lon,
        perp_north * BUFFER_KM,
        perp_east * BUFFER_KM
    )

    right_lat, right_lon = offset_point(
        lat,
        lon,
        -perp_north * BUFFER_KM,
        -perp_east * BUFFER_KM
    )

    left_side.append([left_lon, left_lat])
    right_side.append([right_lon, right_lat])


# Close polygon
polygon = left_side + right_side[::-1] + [left_side[0]]

geojson = {
    "type": "FeatureCollection",

    "features": [
        {
            "type": "Feature",

            "properties": {
                "name": "96-hour oil-spill origin corridor",
                "buffer_km": BUFFER_KM,
                "hours": 96
            },

            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            }
        },

        {
            "type": "Feature",

            "properties": {
                "name": "Backward hindcast trajectory"
            },

            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [p["longitude"], p["latitude"]]
                    for p in track
                ]
            }
        }
    ]
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=4)

print("=" * 70)
print("ORIGIN CORRIDOR CREATED")
print("=" * 70)

print(f"Trajectory points : {len(track)}")
print(f"Buffer            : {BUFFER_KM} km")

print()
print("96h endpoint:")
print(
    f"{track[-1]['latitude']:.6f}, "
    f"{track[-1]['longitude']:.6f}"
)

print()
print(f"Saved: {OUTPUT}")