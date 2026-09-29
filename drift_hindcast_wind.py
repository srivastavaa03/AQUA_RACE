import sys
import json
import math
from pathlib import Path
from datetime import datetime, timedelta, timezone

import numpy as np
import xarray as xr


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def move_point(lat, lon, north_m, east_m):

    new_lat = lat + north_m / 111320.0

    meters_per_degree_lon = (
        111320.0 * math.cos(math.radians(lat))
    )

    if abs(meters_per_degree_lon) > 1e-9:
        new_lon = lon + east_m / meters_per_degree_lon
    else:
        new_lon = lon

    return new_lat, new_lon


def scalar_from_dataarray(da):
    """
    Reduce any remaining non-spatial dimensions such as depth
    and return one scalar value.
    """
    while da.ndim > 0:
        dim = da.dims[0]
        da = da.isel({dim: 0})

    return float(da.values)


def get_current(current_ds, lat, lon, timestamp):
    """
    Sample the nearest Copernicus ocean-current grid cell
    at the requested location and time.
    """

    current = current_ds.sel(
        time=np.datetime64(timestamp),
        latitude=lat,
        longitude=lon,
        method="nearest",
    )

    uo = scalar_from_dataarray(current["uo"])
    vo = scalar_from_dataarray(current["vo"])

    current_lat = float(
        current["latitude"].values
    )

    current_lon = float(
        current["longitude"].values
    )

    return (
        uo,
        vo,
        current_lat,
        current_lon
    )


def get_wind(wind_ds, lat, lon, timestamp):
    """
    Sample the nearest ERA5 wind grid cell.
    """

    wind = wind_ds.sel(
        valid_time=np.datetime64(timestamp),
        latitude=lat,
        longitude=lon,
        method="nearest",
    )

    u10 = scalar_from_dataarray(wind["u10"])
    v10 = scalar_from_dataarray(wind["v10"])

    return u10, v10


def run_hindcast(
    spill_file,
    metadata_file,
    current_file,
    wind_file,
    output_file,
    backward_hours=96,
    windage=0.03,
):

    spill = load_json(spill_file)
    metadata = load_json(metadata_file)

    start_lat = float(
        spill["centroid"]["latitude"]
    )

    start_lon = float(
        spill["centroid"]["longitude"]
    )

    acquisition = metadata["acquisition_start"]

    # Convert Sentinel timestamp to Python UTC datetime.
    scene_time = datetime.fromisoformat(
        acquisition.replace("Z", "+00:00")
    )

    print("=" * 70)
    print("OIL-SPILL HINDCAST")
    print("COPERNICUS HYDRODYNAMIC CURRENT + ERA5 WIND")
    print("=" * 70)

    print()
    print(f"Spill location : {start_lat:.6f}, {start_lon:.6f}")
    print(f"Scene time     : {acquisition}")
    print(f"Current file   : {current_file}")
    print(f"Wind file      : {wind_file}")
    print(f"Backward time  : {backward_hours} hours")
    print(f"Windage        : {windage * 100:.1f}%")

    if not Path(current_file).exists():
        raise FileNotFoundError(
            f"Ocean current file not found:\n{current_file}"
        )

    if not Path(wind_file).exists():
        raise FileNotFoundError(
            f"ERA5 wind file not found:\n{wind_file}"
        )

    current_ds = xr.open_dataset(current_file)
    wind_ds = xr.open_dataset(wind_file)

    # ---------------------------------------------------------
    # Inspect current dataset
    # ---------------------------------------------------------

    print()
    print("HYDRODYNAMIC CURRENT DATASET")

    print(
        f"Current dimensions: "
        f"{dict(current_ds.sizes)}"
    )

    # ---------------------------------------------------------
    # Initial current
    # ---------------------------------------------------------

    (
        initial_uo,
        initial_vo,
        initial_current_lat,
        initial_current_lon
    ) = get_current(
        current_ds,
        start_lat,
        start_lon,
        scene_time
    )

    print()
    print("INITIAL OCEAN CURRENT")
    print(
        f"Grid location : "
        f"{initial_current_lat:.6f}, "
        f"{initial_current_lon:.6f}"
    )

    print(
        f"uo            : "
        f"{initial_uo:.6f} m/s"
    )

    print(
        f"vo            : "
        f"{initial_vo:.6f} m/s"
    )

    # ---------------------------------------------------------
    # Wind information
    # ---------------------------------------------------------

    print()
    print("ERA5 WIND")

    print(
        f"Wind grid     : "
        f"{wind_ds.sizes.get('latitude', '?')} x "
        f"{wind_ds.sizes.get('longitude', '?')}"
    )

    # ---------------------------------------------------------
    # Lagrangian backward hindcast
    # ---------------------------------------------------------

    lat = start_lat
    lon = start_lon

    track = []

    for hour_back in range(
        0,
        backward_hours + 1
    ):

        timestamp = (
            scene_time
            - timedelta(hours=hour_back)
        )

        # Sample ocean current at the particle's
        # CURRENT position.
        (
            uo,
            vo,
            current_lat,
            current_lon
        ) = get_current(
            current_ds,
            lat,
            lon,
            timestamp
        )

        # Sample wind at the particle's current position.
        u10, v10 = get_wind(
            wind_ds,
            lat,
            lon,
            timestamp
        )

        # Wind contribution.
        wind_east = u10 * windage
        wind_north = v10 * windage

        # Combined surface transport velocity.
        total_east = uo + wind_east
        total_north = vo + wind_north

        speed = math.sqrt(
            total_east ** 2 +
            total_north ** 2
        )

        direction = math.degrees(
            math.atan2(
                total_east,
                total_north
            )
        )

        if direction < 0:
            direction += 360

        # Store current position.
        track.append(
            {
                "hours_before_scene": hour_back,
                "time": timestamp.isoformat(),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "current_grid_latitude": round(
                    current_lat,
                    6
                ),
                "current_grid_longitude": round(
                    current_lon,
                    6
                ),
                "u10_mps": round(u10, 4),
                "v10_mps": round(v10, 4),
                "current_uo_mps": round(uo, 4),
                "current_vo_mps": round(vo, 4),
                "windage_factor": windage,
                "combined_speed_mps": round(
                    speed,
                    4
                ),
                "combined_direction_deg": round(
                    direction,
                    2
                ),
            }
        )

        # Move one hour backward.
        if hour_back < backward_hours:

            north_m = -total_north * 3600
            east_m = -total_east * 3600

            lat, lon = move_point(
                lat,
                lon,
                north_m,
                east_m,
            )

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    result = {

        "model":
            "Lagrangian backward drift using "
            "Copernicus hydrodynamic currents + ERA5 wind",

        "model_type":
            "hydrodynamic-current-driven surface transport "
            "with windage",

        "windage_factor":
            windage,

        "backward_hours":
            backward_hours,

        "spill_location": {
            "latitude": start_lat,
            "longitude": start_lon,
        },

        "scene_time":
            acquisition,

        "ocean_current": {
            "source":
                "Copernicus Marine",

            "variables": [
                "uo",
                "vo"
            ],

            "time_behavior":
                "sampled at each hindcast timestep",

            "spatial_behavior":
                "nearest current grid cell sampled at particle position",

            "initial_grid": {
                "latitude":
                    initial_current_lat,

                "longitude":
                    initial_current_lon,

                "uo_mps":
                    initial_uo,

                "vo_mps":
                    initial_vo,
            },

            "file":
                str(
                    Path(current_file).resolve()
                ),
        },

        "wind": {
            "source":
                "ERA5",

            "variables": [
                "u10",
                "v10"
            ],

            "time_behavior":
                "hourly",

            "spatial_behavior":
                "nearest wind grid cell sampled at particle position",

            "file":
                str(
                    Path(wind_file).resolve()
                ),
        },

        "backward_track":
            track,

        "limitations": [
            "Oil weathering, spreading, evaporation and emulsification are not modeled.",
            "Vertical transport is not modeled.",
            "The current dataset is relatively coarse and may not resolve small-scale coastal circulation.",
            "Windage is represented by a configurable surface-wind fraction.",
            "Trajectory represents a possible source pathway rather than an exact source location.",
        ],
    }

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )

    current_ds.close()
    wind_ds.close()

    print()
    print("=" * 70)
    print("HINDCAST COMPLETE")
    print("=" * 70)

    print(
        f"Track points: {len(track)}"
    )

    print()
    print(
        f"{backward_hours} HOURS BACK:"
    )

    print(
        f"Latitude : "
        f"{track[-1]['latitude']:.6f}"
    )

    print(
        f"Longitude: "
        f"{track[-1]['longitude']:.6f}"
    )

    print()
    print(
        f"Saved: {output_path}"
    )


def main():

    if len(sys.argv) != 6:

        print("Usage:")

        print(
            "python drift_hindcast_wind.py "
            "<SPILL_JSON> "
            "<METADATA_JSON> "
            "<CURRENT_NC> "
            "<WIND_NC> "
            "<OUTPUT_JSON>"
        )

        print()

        print("Example:")

        print(
            "python drift_hindcast_wind.py "
            "spill.json "
            "metadata.json "
            "currents.nc "
            "wind.nc "
            "hindcast.json"
        )

        sys.exit(1)

    run_hindcast(
        spill_file=sys.argv[1],
        metadata_file=sys.argv[2],
        current_file=sys.argv[3],
        wind_file=sys.argv[4],
        output_file=sys.argv[5],
    )


if __name__ == "__main__":
    main()
