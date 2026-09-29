import csv
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(r"D:\oilspill_project")
PRED_DIR = BASE_DIR / "predictions"

SPILL_FILE = PRED_DIR / "spill_characterization.json"
META_FILE = PRED_DIR / "sentinel_metadata.json"
DRIFT_FILE = PRED_DIR / "drift_result.json"

DEFAULT_AIS_FILE = BASE_DIR / "Aquatrace-ai" / "data" / "ais_demo.csv"

OUTPUT_CSV = PRED_DIR / "ais_candidate_vessels.csv"
OUTPUT_JSON = PRED_DIR / "ais_candidate_vessels.json"

# AIS must be close to the modeled drift trajectory
MAX_TRACK_DISTANCE_KM = 50.0

# AIS timestamp tolerance around each 6-hour drift point
TIME_TOLERANCE_HOURS = 6.0


def parse_time(value):
    if not value:
        return None

    value = str(value).strip()

    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)

        return dt
    except Exception:
        return None


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def normalize_row(row):
    """
    Normalize common AIS column names.
    """

    normalized = {}

    for key, value in row.items():
        if key is None:
            continue

        k = key.strip().lower()

        if k in ["mmsi", "mmsi_number"]:
            normalized["mmsi"] = value

        elif k in ["timestamp", "time", "datetime", "date_time"]:
            normalized["timestamp"] = value

        elif k in ["latitude", "lat"]:
            normalized["latitude"] = value

        elif k in ["longitude", "lon", "lng"]:
            normalized["longitude"] = value

        elif k in ["speed", "sog"]:
            normalized["speed"] = value

        elif k in ["heading", "cog"]:
            normalized["heading"] = value

        elif k in ["vessel_name", "ship_name", "name"]:
            normalized["vessel_name"] = value

        elif k in ["vessel_type", "ship_type", "type"]:
            normalized["vessel_type"] = value

    return normalized


def load_ais(path):
    records = []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row = normalize_row(row)

            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
            except Exception:
                continue

            timestamp = parse_time(row.get("timestamp"))

            if timestamp is None:
                continue

            row["latitude"] = lat
            row["longitude"] = lon
            row["_time"] = timestamp

            records.append(row)

    return records


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def track_points_with_time(drift, acquisition_time):
    """
    Convert drift model hours into real timestamps.
    """

    scene_time = parse_time(acquisition_time)

    points = []

    for track_name in ["backward_track", "forward_track"]:

        for point in drift.get(track_name, []):

            hours = float(point["hours_from_scene"])

            point_time = scene_time + timedelta(hours=hours)

            points.append(
                {
                    "track": track_name,
                    "hours_from_scene": hours,
                    "timestamp": point_time,
                    "latitude": float(point["latitude"]),
                    "longitude": float(point["longitude"]),
                }
            )

    return points


def find_best_track_match(ais_record, track_points):
    """
    Find the drift-track point that is both:
      - temporally close
      - spatially close
    """

    best = None

    ais_time = ais_record["_time"]

    for point in track_points:

        time_diff_hours = abs(
            (ais_time - point["timestamp"]).total_seconds()
        ) / 3600.0

        if time_diff_hours > TIME_TOLERANCE_HOURS:
            continue

        distance = haversine_km(
            ais_record["latitude"],
            ais_record["longitude"],
            point["latitude"],
            point["longitude"],
        )

        if distance > MAX_TRACK_DISTANCE_KM:
            continue

        # Smaller distance + smaller time difference = better match
        score = (
            max(0.0, 1.0 - distance / MAX_TRACK_DISTANCE_KM) * 0.7
            + max(0.0, 1.0 - time_diff_hours / TIME_TOLERANCE_HOURS)
            * 0.3
        )

        candidate = {
            "distance_km": distance,
            "time_difference_hours": time_diff_hours,
            "score": score,
            "track": point["track"],
            "track_hours_from_scene": point["hours_from_scene"],
            "track_timestamp": point["timestamp"],
            "track_latitude": point["latitude"],
            "track_longitude": point["longitude"],
        }

        if best is None or score > best["score"]:
            best = candidate

    return best


def main():

    print("=" * 65)
    print("GENERIC AIS + SAR + DRIFT CORRELATION")
    print("=" * 65)

    # ---------------------------------------------------------
    # AIS file
    # ---------------------------------------------------------

    if len(sys.argv) > 1:
        ais_file = Path(sys.argv[1])
    else:
        ais_file = DEFAULT_AIS_FILE

    if not ais_file.exists():
        raise FileNotFoundError(
            f"AIS file not found:\n{ais_file}"
        )

    # ---------------------------------------------------------
    # Load project outputs
    # ---------------------------------------------------------

    spill = load_json(SPILL_FILE)
    metadata = load_json(META_FILE)
    drift = load_json(DRIFT_FILE)

    centroid = spill.get("centroid", {})

    spill_lat = float(centroid["latitude"])
    spill_lon = float(centroid["longitude"])

    acquisition_time = metadata["acquisition_start"]

    scene_time = parse_time(acquisition_time)

    # ---------------------------------------------------------
    # Build timestamped drift trajectory
    # ---------------------------------------------------------

    track_points = track_points_with_time(
        drift,
        acquisition_time,
    )

    print(f"SAR acquisition : {acquisition_time}")
    print(
        f"Spill centroid  : "
        f"{spill_lat:.6f}, {spill_lon:.6f}"
    )

    print(f"Drift points    : {len(track_points)}")

    print(
        f"Spatial limit   : "
        f"{MAX_TRACK_DISTANCE_KM} km from drift track"
    )

    print(
        f"Time tolerance  : "
        f"±{TIME_TOLERANCE_HOURS} hours"
    )

    # ---------------------------------------------------------
    # Load AIS
    # ---------------------------------------------------------

    ais_records = load_ais(ais_file)

    print(f"AIS records     : {len(ais_records)}")
    print()

    # ---------------------------------------------------------
    # Match AIS against drift trajectory
    # ---------------------------------------------------------

    candidates = []

    for record in ais_records:

        match = find_best_track_match(
            record,
            track_points,
        )

        if match is None:
            continue

        output = {
            "mmsi": record.get("mmsi"),
            "vessel_name": record.get("vessel_name"),
            "vessel_type": record.get("vessel_type"),
            "ais_timestamp": record["_time"].isoformat(),
            "ais_latitude": record["latitude"],
            "ais_longitude": record["longitude"],
            "speed": record.get("speed"),
            "heading": record.get("heading"),

            "distance_to_drift_km": round(
                match["distance_km"], 3
            ),

            "time_difference_hours": round(
                match["time_difference_hours"], 3
            ),

            "correlation_score": round(
                match["score"],
                4,
            ),

            "matched_track": match["track"],

            "track_hours_from_sar": match[
                "track_hours_from_scene"
            ],

            "track_timestamp": match[
                "track_timestamp"
            ].isoformat(),

            "track_latitude": match[
                "track_latitude"
            ],

            "track_longitude": match[
                "track_longitude"
            ],
        }

        candidates.append(output)

    # ---------------------------------------------------------
    # Sort by correlation score
    # ---------------------------------------------------------

    candidates.sort(
        key=lambda x: x["correlation_score"],
        reverse=True,
    )

    # ---------------------------------------------------------
    # Save CSV
    # ---------------------------------------------------------

    if candidates:

        fieldnames = list(candidates[0].keys())

        with open(
            OUTPUT_CSV,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
            )

            writer.writeheader()
            writer.writerows(candidates)

    else:

        with open(
            OUTPUT_CSV,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            writer = csv.writer(f)

            writer.writerow(
                [
                    "mmsi",
                    "vessel_name",
                    "distance_to_drift_km",
                    "time_difference_hours",
                    "correlation_score",
                ]
            )

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    result = {
        "method": "SAR acquisition time + spill location + drift trajectory",
        "sar_acquisition_time": acquisition_time,
        "spill_location": {
            "latitude": spill_lat,
            "longitude": spill_lon,
        },
        "search_parameters": {
            "max_distance_to_drift_km": MAX_TRACK_DISTANCE_KM,
            "time_tolerance_hours": TIME_TOLERANCE_HOURS,
            "backward_drift_hours": 96,
            "forward_drift_hours": 24,
        },
        "ais_file": str(ais_file),
        "ais_records_loaded": len(ais_records),
        "candidate_vessels": len(candidates),
        "candidates": candidates,
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=4,
        )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print("=" * 65)
    print("RESULT")
    print("=" * 65)

    print(
        f"Candidate vessels: {len(candidates)}"
    )

    if candidates:

        print("\nTop candidates:")

        for i, candidate in enumerate(
            candidates[:10],
            start=1,
        ):

            print(
                f"{i}. "
                f"{candidate.get('vessel_name') or 'Unknown'} "
                f"({candidate.get('mmsi')})"
            )

            print(
                f"   Distance to drift: "
                f"{candidate['distance_to_drift_km']} km"
            )

            print(
                f"   Time difference: "
                f"{candidate['time_difference_hours']} h"
            )

            print(
                f"   Track: "
                f"{candidate['matched_track']}"
            )

            print(
                f"   Score: "
                f"{candidate['correlation_score']}"
            )

    else:

        print(
            "\nNo AIS vessels matched the "
            "SAR + drift criteria."
        )

    print(f"\nSaved: {OUTPUT_CSV}")
    print(f"Saved: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()