import os
import sys
import json
import re


def extract_metadata(safe_path, output_json):

    product_name = os.path.basename(
        os.path.normpath(safe_path)
    )

    # ========================================================
    # SENTINEL-1 PRODUCT NAME
    # ========================================================

    match = re.match(
        r"(S1[AB])_"
        r"([A-Z]+)_"
        r"([A-Z0-9]+)_"
        r"([A-Z0-9]+)_"
        r"(\d{8}T\d{6})_"
        r"(\d{8}T\d{6})_"
        r"(\d+)_"
        r"([A-Z0-9]+)_"
        r"([A-Z0-9]+)",
        product_name
    )

    if match:

        satellite = match.group(1)
        mode = match.group(2)
        product_type = match.group(3)
        polarization = match.group(4)

        start_time = match.group(5)
        end_time = match.group(6)

        orbit = match.group(7)
        mission_data_take = match.group(8)
        product_unique_id = match.group(9)

        # Convert:
        # 20200810T145024
        # →
        # 2020-08-10T14:50:24Z

        start_time = (
            start_time[:4]
            + "-"
            + start_time[4:6]
            + "-"
            + start_time[6:8]
            + "T"
            + start_time[9:11]
            + ":"
            + start_time[11:13]
            + ":"
            + start_time[13:15]
            + "Z"
        )

        end_time = (
            end_time[:4]
            + "-"
            + end_time[4:6]
            + "-"
            + end_time[6:8]
            + "T"
            + end_time[9:11]
            + ":"
            + end_time[11:13]
            + ":"
            + end_time[13:15]
            + "Z"
        )

    else:

        satellite = None
        mode = None
        product_type = None
        polarization = None
        start_time = None
        end_time = None
        orbit = None
        mission_data_take = None
        product_unique_id = None

    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "product_name": product_name,

        "satellite": satellite,

        "sensor": "Sentinel-1",

        "mode": mode,

        "product_type": product_type,

        "polarization": polarization,

        "acquisition_start": start_time,

        "acquisition_end": end_time,

        "orbit": orbit,

        "mission_data_take": mission_data_take,

        "product_unique_id": product_unique_id,

        "safe_path": os.path.abspath(
            safe_path
        )
    }

    # ========================================================
    # SAVE
    # ========================================================

    os.makedirs(
        os.path.dirname(output_json),
        exist_ok=True
    )

    with open(
        output_json,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 60)
    print("       SENTINEL-1 METADATA")
    print("=" * 60)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print("=" * 60)

    print()
    print("Saved:")
    print(output_json)

    return result


def main():

    if len(sys.argv) != 3:

        print(
            "Usage:"
        )

        print(
            "python extract_sentinel_metadata.py "
            "<SAFE_PATH> <OUTPUT_JSON>"
        )

        sys.exit(1)

    safe_path = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.isdir(safe_path):

        raise FileNotFoundError(
            f"SAFE directory not found: {safe_path}"
        )

    extract_metadata(
        safe_path,
        output_json
    )


if __name__ == "__main__":
    main()
