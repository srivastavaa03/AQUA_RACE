import argparse
import json
import subprocess
import sys
import zipfile
import os
from pathlib import Path
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv


BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
PRED = BASE / "predictions"
ENV = PRED / "environmental"

load_dotenv(BASE / ".env")

def run_command(command, step_name):
    print()
    print("=" * 70)
    print(step_name)
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=str(BASE),
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{step_name} failed with exit code {result.returncode}"
        )

    return result


def find_safe(download_path):
    download_path = Path(download_path)

    if download_path.is_dir() and download_path.name.endswith(".SAFE"):
        return download_path

    if download_path.is_file():
        extract_dir = download_path.with_name(
            download_path.stem + "_extracted"
        )

        if not extract_dir.exists():
            print("Extracting Sentinel-1 SAFE archive...")

            with zipfile.ZipFile(download_path, "r") as z:
                z.extractall(extract_dir)

        safes = list(extract_dir.rglob("*.SAFE"))

        if safes:
            return safes[0]

    if download_path.exists():
        safes = list(download_path.rglob("*.SAFE"))

        if safes:
            return safes[0]

    raise RuntimeError(
        "Could not locate Sentinel-1 SAFE directory."
    )


def create_origin_polygon(origin_data):
    """
    Convert the origin search box from origin_zone.json
    into a GeoJSON Polygon for GFW.
    """

    box = origin_data.get("origin_search_box")

    if not box:
        raise RuntimeError(
            "origin_zone.json does not contain origin_search_box."
        )

    north = float(box["north"])
    south = float(box["south"])
    east = float(box["east"])
    west = float(box["west"])

    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [west, south],
                [east, south],
                [east, north],
                [west, north],
                [west, south]
            ]
        ]
    }

    return polygon


def run_gfw_ais(origin_json, date, output_json, output_csv):
    """
    Query Global Fishing Watch AIS Vessel Presence
    for the estimated origin zone.

    This is vessel-presence screening, NOT exact vessel tracking
    and NOT proof of causation.
    """

    token = os.environ.get("GFW_API_TOKEN")

    if not token:
        print()
        print("GFW AIS: token unavailable; attribution skipped.")

        status = {
            "status": "data_unavailable",
            "message": (
                "GFW_API_TOKEN was not available in the environment. "
                "No AIS vessel attribution was performed."
            )
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)

        return False

    with open(origin_json, "r", encoding="utf-8") as f:
        origin_data = json.load(f)

    polygon = create_origin_polygon(origin_data)

    # Use the 96-hour hindcast period.
    scene_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = (scene_date - timedelta(days=4)).strftime("%Y-%m-%d")
    end_date = date

    print()
    print("=" * 70)
    print("GLOBAL FISHING WATCH AIS CORRELATION")
    print("=" * 70)
    print()
    print(f"AIS date range : {start_date} to {end_date}")
    print("AIS source     : GFW Vessel Presence")
    print("Spatial area   : Estimated origin zone")

    url = (
        "https://gateway.api.globalfishingwatch.org/v3/4wings/report"
        "?spatial-resolution=LOW"
        "&temporal-resolution=DAILY"
        "&group-by=VESSEL_ID"
        "&datasets[0]=public-global-presence%3Alatest"
        f"&date-range={start_date}%2C{end_date}"
        "&format=JSON"
        "&spatial-aggregation=false"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "geojson": polygon
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=120
        )
    except requests.RequestException as e:

        status = {
            "status": "request_failed",
            "message": str(e)
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)

        print()
        print("GFW AIS request failed.")
        print(str(e))

        return False

    print()
    print(f"GFW HTTP status: {response.status_code}")

    if response.status_code != 200:

        status = {
            "status": "request_failed",
            "http_status": response.status_code,
            "message": response.text[:1000]
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)

        print("GFW AIS request was not successful.")
        print(response.text[:500])

        return False

    try:
        gfw_data = response.json()
    except ValueError:

        status = {
            "status": "invalid_response",
            "message": "GFW returned a non-JSON response."
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)

        return False

    # Save raw GFW response.
    raw_path = PRED / (
        f"gfw_ais_{start_date.replace('-', '')}_"
        f"{end_date.replace('-', '')}.json"
    )

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(gfw_data, f, indent=4)

    # ------------------------------------------------------------
    # Extract vessel records
    # ------------------------------------------------------------

    records = []

    if isinstance(gfw_data, dict):

        entries = gfw_data.get("entries", [])

        for entry in entries:

            if not isinstance(entry, dict):
                continue

            # GFW Vessel Presence response format:
            # entries
            #   -> public-global-presence:v4.0
            #       -> list of vessel records

            for dataset_key, dataset_records in entry.items():

                if not isinstance(dataset_records, list):
                    continue

                for vessel in dataset_records:

                    if not isinstance(vessel, dict):
                        continue

                    if "vesselId" in vessel or "mmsi" in vessel:
                        records.append(vessel)

    print()
    print(f"GFW vessel-presence records: {len(records)}")

    # ------------------------------------------------------------
    # Convert GFW JSON to AIS CSV
    # ------------------------------------------------------------

    import csv

    fieldnames = [
        "shipName",
        "imo",
        "mmsi",
        "vesselType",
        "geartype",
        "flag",
        "lat",
        "lon",
        "date",
        "entryTimestamp",
        "exitTimestamp",
        "hours",
        "callsign",
        "vesselId"
    ]

    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for record in records:

            row = {}

            for field in fieldnames:
                row[field] = record.get(field, "")

            writer.writerow(row)

    print(f"GFW AIS CSV: {output_csv}")

    # ------------------------------------------------------------
    # Run existing AIS correlation engine
    # ------------------------------------------------------------

    if records:

        prefix = PRED / "ais_ranked_candidates"

        run_command(
            [
                sys.executable,
                str(BASE / "ais_correlator.py"),
                str(output_csv),
                str(origin_json),
                str(prefix)
            ],
            "AIS VESSEL PRESENCE CORRELATION"
        )

        # Add source metadata to the final JSON.
        if output_json.exists():

            try:

                with open(output_json, "r", encoding="utf-8") as f:
                    result = json.load(f)

            except Exception:

                result = {}

            result["ais_source"] = {
                "provider": "Global Fishing Watch",
                "dataset": "public-global-presence:latest",
                "data_type": "AIS vessel presence",
                "date_range": [
                    start_date,
                    end_date
                ]
            }

            result["interpretation"] = (
                "AIS vessel presence identifies vessels observed "
                "within the estimated origin zone or nearby "
                "screening area. It does not provide an exact "
                "individual vessel track and does not establish "
                "that a vessel caused the spill."
            )

            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4)

    else:

        status = {
            "status": "no_vessel_presence_records",
            "ais_source": {
                "provider": "Global Fishing Watch",
                "dataset": "public-global-presence:latest",
                "data_type": "AIS vessel presence",
                "date_range": [
                    start_date,
                    end_date
                ]
            },
            "message": (
                "No GFW vessel-presence records were returned "
                "for the estimated origin zone and hindcast period."
            )
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)

    return True


def main():

    parser = argparse.ArgumentParser(
        description="SIH26143 SAR Oil-Spill Detection Pipeline"
    )

    parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="Target latitude"
    )

    parser.add_argument(
        "--lon",
        type=float,
        required=True,
        help="Target longitude"
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Target date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "--ais",
        default=None,
        help="Optional real AIS CSV file. Overrides automatic GFW AIS."
    )

    args = parser.parse_args()

    lat = args.lat
    lon = args.lon
    date = args.date

    DATA.mkdir(parents=True, exist_ok=True)
    PRED.mkdir(parents=True, exist_ok=True)
    ENV.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 70)
    print("SIH26143 SAR OIL-SPILL INVESTIGATION PIPELINE")
    print("=" * 70)
    print()
    print(f"Location : {lat}, {lon}")
    print(f"Date     : {date}")

    # ------------------------------------------------------------
    # 1. SEARCH SENTINEL-1
    # ------------------------------------------------------------

    search_cmd = [
        sys.executable,
        str(BASE / "sentinel_search.py"),
        str(lat),
        str(lon),
        date,
        date,
        "--json"
    ]

    search_result = subprocess.run(
        search_cmd,
        cwd=str(BASE),
        capture_output=True,
        text=True
    )

    if search_result.returncode != 0:

        print(search_result.stdout)
        print(search_result.stderr)

        try:
            error_data = json.loads(search_result.stdout)
        except json.JSONDecodeError:
            error_data = {}

        if isinstance(error_data, dict) and error_data.get("error"):
            raise RuntimeError(error_data["error"])

        error_message = (
            search_result.stdout.strip()
            or search_result.stderr.strip()
            or "Sentinel-1 search failed."
        )

        raise RuntimeError(error_message)

    try:

        search_data = json.loads(
            search_result.stdout
        )

    except json.JSONDecodeError as e:

        print(search_result.stdout)

        raise RuntimeError(
            "Could not parse Sentinel-1 search response."
        ) from e

    if "error" in search_data:
        raise RuntimeError(
            search_data["error"]
        )

    product_id = search_data.get("id")
    product_name = search_data.get("name")

    if not product_id or not product_name:

        raise RuntimeError(
            "Sentinel search did not return a valid product."
        )

    print()
    print("Sentinel-1 product found:")
    print(product_name)

    # ------------------------------------------------------------
    # 2. DOWNLOAD SENTINEL-1
    # ------------------------------------------------------------

    download_path = DATA / product_name

    if download_path.exists():

        print()
        print("Sentinel-1 product already exists.")
        print(download_path)

    else:

        run_command(
            [
                sys.executable,
                str(BASE / "sentinel_download.py"),
                product_id,
                str(download_path)
            ],
            "DOWNLOADING SENTINEL-1"
        )

    # ------------------------------------------------------------
    # 3. LOCATE SAFE
    # ------------------------------------------------------------

    safe_path = find_safe(download_path)

    print()
    print("SAFE:")
    print(safe_path)

    # ------------------------------------------------------------
    # 4. AI OIL-SPILL DETECTION
    # ------------------------------------------------------------

    mask_path = PRED / "sentinel_mask.tif"

    run_command(
        [
            sys.executable,
            str(BASE / "predict_sentinel.py"),
            str(safe_path),
            str(mask_path)
        ],
        "AI OIL-SPILL DETECTION"
    )

    # ------------------------------------------------------------
    # 5. SENTINEL METADATA
    # ------------------------------------------------------------

    metadata_path = PRED / "sentinel_metadata.json"

    run_command(
        [
            sys.executable,
            str(BASE / "extract_sentinel_metadata.py"),
            str(safe_path),
            str(metadata_path)
        ],
        "EXTRACTING SENTINEL METADATA"
    )

    # ------------------------------------------------------------
    # 6. SPILL CHARACTERIZATION
    # ------------------------------------------------------------

    spill_path = PRED / "spill_characterization.json"

    run_command(
        [
            sys.executable,
            str(BASE / "characterize_candidate.py"),
            str(mask_path),
            str(safe_path),
            str(spill_path)
        ],
        "SPILL CHARACTERIZATION"
    )

    with open(
        spill_path,
        "r",
        encoding="utf-8"
    ) as f:

        spill_data = json.load(f)

    spill_detected = bool(
        spill_data.get(
            "spill_detected",
            False
        )
    )

    # ------------------------------------------------------------
    # STOP IF NO CANDIDATE
    # ------------------------------------------------------------

    if not spill_detected:

        summary = {
            "status": "completed",
            "spill_detected": False,
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "date": date,
            "sentinel_product": product_name,
            "message": (
                "No oil-spill candidate detected "
                "by the AI model."
            )
        }

        summary_path = PRED / "pipeline_summary.json"

        with open(
            summary_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                summary,
                f,
                indent=4
            )

        print()
        print("=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)
        print()
        print("No oil-spill candidate detected.")
        print(f"Summary: {summary_path}")

        return

    # ------------------------------------------------------------
    # 7. GEOLOCATION
    # ------------------------------------------------------------

    geolocation_path = (
        PRED / "spill_pixels_geolocation.csv"
    )

    run_command(
        [
            sys.executable,
            str(BASE / "geolocate_mask.py"),
            str(mask_path),
            str(safe_path),
            str(geolocation_path)
        ],
        "SPILL GEOLOCATION"
    )

    # ------------------------------------------------------------
    # GET DETECTED CENTROID
    # ------------------------------------------------------------

    spill_lat = spill_data["centroid"]["latitude"]
    spill_lon = spill_data["centroid"]["longitude"]

    print()
    print(
        f"Detected spill centroid: "
        f"{spill_lat}, {spill_lon}"
    )

    # ------------------------------------------------------------
    # 8. OCEAN CURRENTS
    # ------------------------------------------------------------

    currents_path = (
        ENV / f"ocean_currents_{date}.nc"
    )

    run_command(
        [
            sys.executable,
            str(BASE / "download_currents.py"),
            str(spill_lat),
            str(spill_lon),
            date,
            date,
            str(currents_path)
        ],
        "DOWNLOADING OCEAN CURRENTS"
    )

    # ------------------------------------------------------------
    # 9. WIND
    # ------------------------------------------------------------

    scene_date = datetime.strptime(
        date,
        "%Y-%m-%d"
    )

    wind_start = (
        scene_date - timedelta(days=4)
    ).strftime("%Y-%m-%d")

    wind_path = ENV / (
        f"era5_wind_{wind_start}_{date}.nc"
    )

    run_command(
        [
            sys.executable,
            str(BASE / "download_wind.py"),
            str(spill_lat),
            str(spill_lon),
            wind_start,
            date,
            str(wind_path)
        ],
        "DOWNLOADING ERA5 WIND"
    )

    # ------------------------------------------------------------
    # 10. DRIFT / HINDCAST
    # ------------------------------------------------------------

    hindcast_path = (
        PRED / "drift_hindcast.json"
    )

    run_command(
        [
            sys.executable,
            str(BASE / "drift_hindcast_wind.py"),
            str(spill_path),
            str(metadata_path),
            str(currents_path),
            str(wind_path),
            str(hindcast_path)
        ],
        "96-HOUR BACKWARD DRIFT HINDCAST"
    )

    # ------------------------------------------------------------
    # 11. ORIGIN ZONE
    # ------------------------------------------------------------

    origin_json = (
        PRED / "origin_zone.json"
    )

    origin_geojson = (
        PRED / "origin_corridor.geojson"
    )

    run_command(
        [
            sys.executable,
            str(BASE / "create_origin_zone.py"),
            str(hindcast_path),
            str(origin_json),
            str(origin_geojson),
            "10"
        ],
        "ESTIMATED ORIGIN ZONE"
    )

    # ------------------------------------------------------------
    # 12. AIS CORRELATION
    # ------------------------------------------------------------

    ais_json = (
        PRED / "ais_ranked_candidates.json"
    )

    ais_csv = (
        PRED / "ais_gfw.csv"
    )

    if args.ais:

        print()
        print("Using manually supplied AIS CSV.")

        ais_prefix = (
            PRED / "ais_ranked_candidates"
        )

        run_command(
            [
                sys.executable,
                str(BASE / "ais_correlator.py"),
                str(Path(args.ais)),
                str(origin_json),
                str(ais_prefix)
            ],
            "AIS VESSEL CORRELATION"
        )

        ais_csv = Path(args.ais)

    else:

        run_gfw_ais(
            origin_json,
            date,
            ais_json,
            ais_csv
        )

    # ------------------------------------------------------------
    # 13. FINAL PIPELINE SUMMARY
    # ------------------------------------------------------------

    summary = {
        "status": "completed",
        "spill_detected": True,

        "input": {
            "latitude": lat,
            "longitude": lon,
            "date": date
        },

        "sentinel": {
            "product": product_name,
            "safe_path": str(safe_path)
        },

        "ai_detection": {
            "model": "U-Net ResNet34",
            "mask": str(mask_path),
            "spill_characterization": str(spill_path)
        },

        "spill": {
            "centroid": spill_data.get(
                "centroid"
            ),
            "estimated_area_km2": spill_data.get(
                "estimated_area_km2"
            ),
            "bounds": spill_data.get(
                "bounds"
            )
        },

        "environment": {
            "ocean_currents": str(
                currents_path
            ),
            "wind": str(
                wind_path
            )
        },

        "drift": {
            "method": (
                "Lagrangian backward drift "
                "using Copernicus hydrodynamic "
                "currents and ERA5 wind"
            ),
            "hindcast": str(
                hindcast_path
            )
        },

        "origin": {
            "json": str(
                origin_json
            ),
            "geojson": str(
                origin_geojson
            )
        },

        "ais": {
            "json": str(
                ais_json
            ),
            "csv": str(
                ais_csv
            ),
            "interpretation": (
                "AIS vessel presence is used "
                "for screening candidates for "
                "further investigation. It is "
                "not evidence of causation."
            )
        }
    }

    summary_path = (
        PRED / "pipeline_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=4
        )

    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print()
    print("AI candidate       : YES")
    print(
        f"Spill centroid     : "
        f"{spill_lat}, {spill_lon}"
    )
    print(
        f"Estimated area     : "
        f"{spill_data.get('estimated_area_km2')} km "
    )
    print(
        f"Origin zone        : "
        f"{origin_json}"
    )
    print(
        f"AIS results        : "
        f"{ais_json}"
    )
    print(
        f"Final summary      : "
        f"{summary_path}"
    )
    print()


if __name__ == "__main__":
    main()
