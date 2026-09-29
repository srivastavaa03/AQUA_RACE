import json
import sys
import math
import pandas as pd


DISTANCE_LIMIT_KM = 25.0
TIME_LIMIT_HOURS = 6.0


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


def parse_time(value):
    if pd.isna(value):
        return None

    try:
        return pd.to_datetime(value, utc=True).to_pydatetime()
    except Exception:
        return None


def find_column(df, candidates):
    lookup = {c.lower(): c for c in df.columns}

    for name in candidates:
        if name.lower() in lookup:
            return lookup[name.lower()]

    return None


def load_origin_zone(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    trajectory = data.get("trajectory_points", [])

    if not trajectory:
        raise ValueError(
            "No trajectory_points found in origin zone file."
        )

    points = []

    for p in trajectory:

        if (
            p.get("latitude") is None
            or p.get("longitude") is None
            or p.get("time") is None
        ):
            continue

        points.append(
            {
                "latitude": float(p["latitude"]),
                "longitude": float(p["longitude"]),
                "time": parse_time(p["time"]),
                "hours_before_scene": p.get(
                    "hours_before_scene"
                ),
            }
        )

    return points


def main():

    if len(sys.argv) != 4:
        print(
            "Usage: python ais_correlator.py "
            "<AIS_CSV> <ORIGIN_ZONE_JSON> <OUTPUT_PREFIX>"
        )
        sys.exit(1)

    ais_path = sys.argv[1]
    origin_path = sys.argv[2]
    output_prefix = sys.argv[3]

    print("=" * 70)
    print("AIS VESSEL PRESENCE CORRELATION ENGINE")
    print("=" * 70)

    print()
    print("AIS file      :", ais_path)
    print("Origin zone   :", origin_path)
    print("Distance limit:", DISTANCE_LIMIT_KM, "km")
    print("Time limit    :", "+/-", TIME_LIMIT_HOURS, "hours")
    print()

    trajectory = load_origin_zone(origin_path)

    print("Trajectory points:", len(trajectory))

    df = pd.read_csv(ais_path)

    print("AIS rows loaded :", len(df))
    print("AIS columns     :", list(df.columns))
    print()

    lat_col = find_column(
        df,
        ["lat", "latitude"]
    )

    lon_col = find_column(
        df,
        ["lon", "longitude"]
    )

    time_col = find_column(
        df,
        [
            "entryTimestamp",
            "entry_time",
            "timestamp",
            "time",
            "date",
        ],
    )

    vessel_col = find_column(
        df,
        [
            "mmsi",
            "vessel_id",
            "vesselId",
            "imo",
        ],
    )

    if not lat_col or not lon_col or not time_col or not vessel_col:
        raise ValueError(
            "Could not detect required AIS columns."
        )

    print("Detected columns:")
    print("latitude    :", lat_col)
    print("longitude   :", lon_col)
    print("time        :", time_col)
    print("vessel      :", vessel_col)
    print()

    df["_lat"] = pd.to_numeric(
        df[lat_col],
        errors="coerce"
    )

    df["_lon"] = pd.to_numeric(
        df[lon_col],
        errors="coerce"
    )

    df["_time"] = df[time_col].apply(parse_time)

    df = df.dropna(
        subset=["_lat", "_lon", "_time"]
    )

    candidates = {}

    print(
        "Searching AIS vessel presence "
        "against hindcast trajectory..."
    )
    print()

    for _, row in df.iterrows():

        ais_lat = float(row["_lat"])
        ais_lon = float(row["_lon"])
        ais_time = row["_time"]

        vessel_id = str(row[vessel_col])

        best = None

        for point in trajectory:

            if point["time"] is None:
                continue

            distance = haversine_km(
                ais_lat,
                ais_lon,
                point["latitude"],
                point["longitude"],
            )

            time_difference = abs(
                (
                    ais_time
                    - point["time"]
                ).total_seconds()
            ) / 3600.0

            if (
                distance <= DISTANCE_LIMIT_KM
                and time_difference <= TIME_LIMIT_HOURS
            ):

                distance_score = max(
                    0.0,
                    100.0
                    * (
                        1.0
                        - distance
                        / DISTANCE_LIMIT_KM
                    ),
                )

                time_score = max(
                    0.0,
                    100.0
                    * (
                        1.0
                        - time_difference
                        / TIME_LIMIT_HOURS
                    ),
                )

                screening_score = (
                    0.70 * distance_score
                    + 0.30 * time_score
                )

                candidate = {
                    "vessel_id": vessel_id,
                    "ship_name": str(
                        row.get("shipName", "")
                    ),
                    "imo": str(
                        row.get("imo", "")
                    ),
                    "mmsi": str(
                        row.get("mmsi", "")
                    ),
                    "vessel_type": str(
                        row.get("vesselType", "")
                    ),
                    "geartype": str(
                        row.get("geartype", "")
                    ),
                    "flag": str(
                        row.get("flag", "")
                    ),

                    "gfw_latitude": ais_lat,
                    "gfw_longitude": ais_lon,
                    "gfw_date": str(
                        row.get("date", "")
                    ),
                    "gfw_entry_timestamp": str(
                        row.get(
                            "entryTimestamp",
                            ""
                        )
                    ),
                    "gfw_exit_timestamp": str(
                        row.get(
                            "exitTimestamp",
                            ""
                        )
                    ),
                    "gfw_presence_hours": float(
                        row.get("hours", 0)
                    ),

                    "distance_to_hindcast_km": round(
                        distance,
                        3
                    ),

                    "time_difference_hours": round(
                        time_difference,
                        2
                    ),

                    "screening_score": round(
                        screening_score,
                        1
                    ),

                    "hindcast_latitude": round(
                        point["latitude"],
                        6
                    ),

                    "hindcast_longitude": round(
                        point["longitude"],
                        6
                    ),

                    "hindcast_time": point[
                        "time"
                    ].isoformat(),

                    "hours_before_scene": point.get(
                        "hours_before_scene"
                    ),

                    "data_type":
                        "GFW vessel presence",

                    "interpretation":
                        "AIS-derived candidate for "
                        "further investigation. GFW "
                        "vessel presence is aggregated "
                        "data and does not provide an "
                        "individual vessel track or "
                        "establish causation.",
                }

                if (
                    best is None
                    or candidate[
                        "screening_score"
                    ]
                    > best[
                        "screening_score"
                    ]
                ):
                    best = candidate

        if best is not None:

            existing = candidates.get(
                vessel_id
            )

            if (
                existing is None
                or best[
                    "screening_score"
                ]
                > existing[
                    "screening_score"
                ]
            ):
                candidates[vessel_id] = best

    results = list(candidates.values())

    results.sort(
        key=lambda x: x["screening_score"],
        reverse=True,
    )

    print("=" * 70)
    print("AIS-DERIVED CANDIDATES")
    print("=" * 70)
    print()

    if not results:

        print("No AIS-derived candidates found.")

        output = {
            "status": "no_candidates",
            "candidate_count": 0,
            "data_type": "GFW vessel presence",
            "interpretation":
                "No GFW vessel-presence records "
                "satisfied the screening thresholds. "
                "This does not prove that no vessel "
                "was present.",
            "candidates": [],
        }

    else:

        for i, c in enumerate(results, 1):

            print(
                f"{i}. {c['ship_name']} "
                f"(MMSI {c['mmsi']})"
            )

            print(
                f"   IMO       : {c['imo']}"
            )

            print(
                f"   Type      : "
                f"{c['vessel_type']}"
            )

            print(
                f"   Flag      : "
                f"{c['flag']}"
            )

            print(
                f"   GFW cell  : "
                f"{c['gfw_latitude']:.6f}, "
                f"{c['gfw_longitude']:.6f}"
            )

            print(
                f"   Distance  : "
                f"{c['distance_to_hindcast_km']:.3f} km"
            )

            print(
                f"   Time diff : "
                f"{c['time_difference_hours']:.2f} h"
            )

            print(
                f"   Presence  : "
                f"{c['gfw_presence_hours']:.1f} h"
            )

            print(
                f"   Screening : "
                f"{c['screening_score']:.1f}"
            )

            print()

        output = {
            "status": "candidates_found",
            "candidate_count": len(results),
            "data_type": "GFW vessel presence",
            "interpretation":
                "These are AIS-derived vessel "
                "candidates for further investigation "
                "based on GFW vessel-presence records "
                "and proximity to the backward "
                "hindcast. GFW presence data does not "
                "provide individual vessel tracks and "
                "does not establish causation.",
            "candidates": results,
        }

    json_path = output_prefix + ".json"
    csv_path = output_prefix + ".csv"

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            indent=2
        )

    pd.DataFrame(results).to_csv(
        csv_path,
        index=False
    )

    print("=" * 70)
    print("Saved:", csv_path)
    print("Saved:", json_path)
    print("=" * 70)


if __name__ == "__main__":
    main()
