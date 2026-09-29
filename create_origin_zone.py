import sys
import json
import math
from pathlib import Path


def create_origin_zone(
    input_file,
    output_json,
    output_geojson,
    buffer_km=10.0,
):

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    track = data.get("backward_track", [])

    if not track:
        raise ValueError(
            "Backward hindcast track is empty."
        )

    lats = [
        p["latitude"]
        for p in track
    ]

    lons = [
        p["longitude"]
        for p in track
    ]

    mean_lat = sum(lats) / len(lats)

    lat_buffer = (
        buffer_km / 111.32
    )

    cos_lat = math.cos(
        math.radians(mean_lat)
    )

    if abs(cos_lat) < 1e-9:
        raise ValueError(
            "Longitude buffer cannot be calculated near the poles."
        )

    lon_buffer = (
        buffer_km
        / (111.32 * cos_lat)
    )

    origin = track[-1]

    origin_zone = {

        "type":
            "prototype_origin_zone",

        "method":
            "backward hindcast corridor",

        "buffer_km":
            buffer_km,

        "origin_endpoint": {

            "latitude":
                origin["latitude"],

            "longitude":
                origin["longitude"],

            "hours_before_scene":
                origin.get(
                    "hours_before_scene"
                ),

            "time":
                origin.get("time"),
        },

        "trajectory_bounds": {

            "north":
                max(lats),

            "south":
                min(lats),

            "east":
                max(lons),

            "west":
                min(lons),
        },

        "origin_search_box": {

            "north":
                origin["latitude"]
                + lat_buffer,

            "south":
                origin["latitude"]
                - lat_buffer,

            "east":
                origin["longitude"]
                + lon_buffer,

            "west":
                origin["longitude"]
                - lon_buffer,
        },

        "trajectory_points":
            track,

        "limitations": [

            "Origin is an estimated zone, not an exact source location.",

            "Origin accuracy depends on the quality and temporal coverage of ocean-current and wind data.",

            "The buffer is a prototype uncertainty assumption.",

            "Oil weathering, waves and Stokes drift are not modeled.",
        ],
    }

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    output_json_path = Path(
        output_json
    )

    output_json_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            origin_zone,
            f,
            indent=4
        )

    # ---------------------------------------------------------
    # GeoJSON
    # ---------------------------------------------------------

    coordinates = [
        [
            p["longitude"],
            p["latitude"]
        ]
        for p in track
    ]

    geojson = {

        "type":
            "FeatureCollection",

        "features": [

            {
                "type":
                    "Feature",

                "properties": {
                    "name":
                        "Oil-spill backward hindcast",

                    "buffer_km":
                        buffer_km,
                },

                "geometry": {

                    "type":
                        "LineString",

                    "coordinates":
                        coordinates,
                },
            },

            {
                "type":
                    "Feature",

                "properties": {
                    "name":
                        "Estimated origin endpoint",
                },

                "geometry": {

                    "type":
                        "Point",

                    "coordinates": [
                        origin["longitude"],
                        origin["latitude"],
                    ],
                },
            },
        ],
    }

    output_geojson_path = Path(
        output_geojson
    )

    output_geojson_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_geojson_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            geojson,
            f,
            indent=4
        )

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    print("=" * 70)
    print("ORIGIN ZONE CREATED")
    print("=" * 70)

    print()
    print("Backward-hindcast endpoint:")

    print(
        f"Latitude : "
        f"{origin['latitude']:.6f}"
    )

    print(
        f"Longitude: "
        f"{origin['longitude']:.6f}"
    )

    print(
        f"Time     : "
        f"{origin.get('time')}"
    )

    print()
    print(
        f"Uncertainty buffer: "
        f"{buffer_km:.1f} km"
    )

    print()
    print("Origin search box:")

    box = origin_zone[
        "origin_search_box"
    ]

    print(
        f"North : {box['north']:.6f}"
    )

    print(
        f"South : {box['south']:.6f}"
    )

    print(
        f"East  : {box['east']:.6f}"
    )

    print(
        f"West  : {box['west']:.6f}"
    )

    print()
    print(
        f"Saved: {output_json_path}"
    )

    print(
        f"Saved: {output_geojson_path}"
    )


def main():

    if len(sys.argv) not in (4, 5):

        print("Usage:")

        print(
            "python create_origin_zone.py "
            "<HINDCAST_JSON> "
            "<OUTPUT_JSON> "
            "<OUTPUT_GEOJSON> "
            "[BUFFER_KM]"
        )

        print()

        print("Example:")

        print(
            "python create_origin_zone.py "
            "hindcast.json "
            "origin_zone.json "
            "origin_corridor.geojson "
            "10"
        )

        sys.exit(1)

    input_file = sys.argv[1]
    output_json = sys.argv[2]
    output_geojson = sys.argv[3]

    buffer_km = (
        float(sys.argv[4])
        if len(sys.argv) == 5
        else 10.0
    )

    if buffer_km <= 0:
        raise ValueError(
            "Buffer must be greater than 0 km."
        )

    create_origin_zone(
        input_file,
        output_json,
        output_geojson,
        buffer_km,
    )


if __name__ == "__main__":
    main()
