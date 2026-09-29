import json
import math
from pathlib import Path

import numpy as np
import xarray as xr


BASE_DIR = Path(r"D:\oilspill_project")
PRED_DIR = BASE_DIR / "predictions"


SPILL_FILE = PRED_DIR / "spill_characterization_real.json"
META_FILE = PRED_DIR / "sentinel_metadata_real.json"
CURRENT_FILE = PRED_DIR / "environmental" / "ocean_currents_20200810.nc"
OUTPUT_FILE = PRED_DIR / "drift_result.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_nearest_current(ds, latitude, longitude, date):
    """
    Get Copernicus uo/vo at the nearest grid point and requested date.
    """

    # Select the requested day
    current_day = ds.sel(
        time=np.datetime64(date),
        latitude=latitude,
        longitude=longitude,
        method="nearest",
    )

    # Remove depth dimension if present
    uo = current_day["uo"].squeeze().item()
    vo = current_day["vo"].squeeze().item()

    if not np.isfinite(uo) or not np.isfinite(vo):
        raise ValueError(
            f"Invalid ocean current at {latitude}, {longitude}: "
            f"uo={uo}, vo={vo}"
        )

    actual_lat = float(current_day.latitude.values)
    actual_lon = float(current_day.longitude.values)
    actual_time = str(current_day.time.values)

    return float(uo), float(vo), actual_lat, actual_lon, actual_time


def current_speed_direction(uo, vo):
    """
    uo = eastward velocity
    vo = northward velocity

    Direction is degrees clockwise from north.
    """
    speed = math.sqrt(uo ** 2 + vo ** 2)

    direction = math.degrees(math.atan2(uo, vo))
    if direction < 0:
        direction += 360

    return speed, direction


def move_point(lat, lon, speed_mps, direction_deg, hours):
    """
    Move a point using a simple constant-current drift model.
    Positive hours = forward.
    Negative hours = backward.
    """

    distance_m = speed_mps * hours * 3600

    direction_rad = math.radians(direction_deg)

    north_m = distance_m * math.cos(direction_rad)
    east_m = distance_m * math.sin(direction_rad)

    new_lat = lat + north_m / 111320.0

    meters_per_degree_lon = 111320.0 * math.cos(math.radians(lat))

    if abs(meters_per_degree_lon) < 1e-9:
        new_lon = lon
    else:
        new_lon = lon + east_m / meters_per_degree_lon

    return new_lat, new_lon


def build_track(
    start_lat,
    start_lon,
    speed,
    direction,
    start_hours,
    end_hours,
    step_hours,
):
    track = []

    hour = start_hours

    while hour <= end_hours:
        lat, lon = move_point(
            start_lat,
            start_lon,
            speed,
            direction,
            hour,
        )

        track.append(
            {
                "hours_from_scene": hour,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
            }
        )

        hour += step_hours

    return track


def main():

    print("=" * 60)
    print("OIL-SPILL DRIFT MODEL - REAL COPERNICUS CURRENTS")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load spill information
    # ---------------------------------------------------------

    spill = load_json(SPILL_FILE)
    metadata = load_json(META_FILE)

    centroid = spill.get("centroid", {})

    spill_lat = centroid.get("latitude")
    spill_lon = centroid.get("longitude")

    if spill_lat is None or spill_lon is None:
        raise ValueError("Spill centroid not found.")

    acquisition_time = metadata["acquisition_start"]
    acquisition_date = acquisition_time[:10]

    print(f"Spill location : {spill_lat:.6f}, {spill_lon:.6f}")
    print(f"Scene time     : {acquisition_time}")
    print(f"Current file   : {CURRENT_FILE}")

    # ---------------------------------------------------------
    # Load Copernicus data
    # ---------------------------------------------------------

    if not CURRENT_FILE.exists():
        raise FileNotFoundError(
            f"Copernicus current file not found:\n{CURRENT_FILE}"
        )

    ds = xr.open_dataset(CURRENT_FILE)

    print("\nCopernicus dataset loaded.")
    print(f"Dimensions     : {dict(ds.sizes)}")

    # ---------------------------------------------------------
    # Extract nearest real current
    # ---------------------------------------------------------

    uo, vo, actual_lat, actual_lon, actual_time = get_nearest_current(
        ds,
        spill_lat,
        spill_lon,
        acquisition_date,
    )

    speed, direction = current_speed_direction(uo, vo)

    print("\nREAL OCEAN CURRENT")
    print(f"Nearest latitude  : {actual_lat:.6f}")
    print(f"Nearest longitude : {actual_lon:.6f}")
    print(f"Current date      : {actual_time}")
    print(f"uo (eastward)     : {uo:.6f} m/s")
    print(f"vo (northward)    : {vo:.6f} m/s")
    print(f"Speed             : {speed:.6f} m/s")
    print(f"Direction         : {direction:.2f}°")

    # ---------------------------------------------------------
    # Build drift tracks
    # ---------------------------------------------------------

    backward_track = build_track(
        spill_lat,
        spill_lon,
        speed,
        direction,
        -96,
        0,
        6,
    )

    forward_track = build_track(
        spill_lat,
        spill_lon,
        speed,
        direction,
        0,
        24,
        6,
    )

    # ---------------------------------------------------------
    # Save result
    # ---------------------------------------------------------

    result = {
        "model_type": "constant-current drift using Copernicus historical ocean current",
        "demo_environmental_values": False,
        "source": {
            "dataset": "cmems_mod_glo_phy_my_0.083deg_P1D-m_202311",
            "file": str(CURRENT_FILE),
            "acquisition_time": acquisition_time,
            "current_date_used": acquisition_date,
        },
        "spill_location": {
            "latitude": spill_lat,
            "longitude": spill_lon,
        },
        "current": {
            "nearest_latitude": actual_lat,
            "nearest_longitude": actual_lon,
            "uo_eastward_mps": uo,
            "vo_northward_mps": vo,
            "speed_mps": speed,
            "direction_degrees": direction,
        },
        "backward_hours": 96,
        "forward_hours": 24,
        "backward_track": backward_track,
        "forward_track": forward_track,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print("\nRESULT")
    print(f"Backward track : {len(backward_track)} points")
    print(f"Forward track  : {len(forward_track)} points")
    print(f"\nSaved: {OUTPUT_FILE}")

    ds.close()


if __name__ == "__main__":
    main()