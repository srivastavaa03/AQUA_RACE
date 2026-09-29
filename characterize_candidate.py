import os
import sys
import glob
import json
import numpy as np
import rasterio
import xml.etree.ElementTree as ET

from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import label


MIN_COMPONENT_PIXELS = 100


def characterize(mask_path, safe_dir, output_json):

    # ========================================================
    # READ FULL MASK
    # ========================================================

    with rasterio.open(mask_path) as src:

        mask = src.read(1)

    height, width = mask.shape

    print("Mask:")
    print("Height:", height)
    print("Width :", width)

    # ========================================================
    # CONNECTED COMPONENTS
    # ========================================================

    binary = mask > 0

    labels, count = label(binary)

    if count == 0:

        result = {
            "spill_detected": False,
            "candidate_count": 0,
            "message": "No detected candidate components."
        }

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
                indent=2
            )

        print("\nNo candidate detected.")

        return result

    sizes = np.bincount(
        labels.ravel()
    )

    # Ignore background
    sizes[0] = 0

    # ========================================================
    # FILTER SMALL COMPONENTS
    # ========================================================

    valid_components = np.where(
        sizes >= MIN_COMPONENT_PIXELS
    )[0]

    valid_components = valid_components[
        valid_components != 0
    ]

    if len(valid_components) == 0:

        result = {
            "spill_detected": False,
            "candidate_count": 0,
            "message": (
                "Detected pixels existed, "
                "but no component passed the "
                "minimum size threshold."
            )
        }

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
                indent=2
            )

        print(
            "\nNo meaningful candidate detected."
        )

        return result

    # Largest meaningful component
    component_id = valid_components[
        np.argmax(
            sizes[valid_components]
        )
    ]

    component_size = int(
        sizes[component_id]
    )

    component = (
        labels == component_id
    )

    rows, cols = np.where(
        component
    )

    print(
        "\nConnected components:",
        count
    )

    print(
        "Meaningful components:",
        len(valid_components)
    )

    print(
        "Largest component:",
        component_size,
        "pixels"
    )

    # ========================================================
    # COMPONENT BOUNDS IN IMAGE
    # ========================================================

    row_min = int(rows.min())
    row_max = int(rows.max())

    col_min = int(cols.min())
    col_max = int(cols.max())

    print(
        "Rows:",
        row_min,
        "-",
        row_max
    )

    print(
        "Cols:",
        col_min,
        "-",
        col_max
    )

    # ========================================================
    # SENTINEL GEOLOCATION GRID
    # ========================================================

    xml_files = glob.glob(
        os.path.join(
            safe_dir,
            "annotation",
            "*-vv-*.xml"
        )
    )

    if not xml_files:

        raise FileNotFoundError(
            "VV annotation XML not found"
        )

    xml_path = xml_files[0]

    root = ET.parse(
        xml_path
    ).getroot()

    points = root.findall(
        ".//geolocationGridPoint"
    )

    if not points:

        raise RuntimeError(
            "No geolocation grid points found"
        )

    lines = sorted(
        set(
            int(
                p.find("line").text
            )
            for p in points
        )
    )

    pixels_grid = sorted(
        set(
            int(
                p.find("pixel").text
            )
            for p in points
        )
    )

    lat_grid = np.zeros(
        (
            len(lines),
            len(pixels_grid)
        )
    )

    lon_grid = np.zeros_like(
        lat_grid
    )

    line_index = {
        value: i
        for i, value in enumerate(lines)
    }

    pixel_index = {
        value: i
        for i, value in enumerate(pixels_grid)
    }

    for p in points:

        line = int(
            p.find("line").text
        )

        pixel = int(
            p.find("pixel").text
        )

        lat = float(
            p.find("latitude").text
        )

        lon = float(
            p.find("longitude").text
        )

        i = line_index[line]
        j = pixel_index[pixel]

        lat_grid[i, j] = lat
        lon_grid[i, j] = lon

    # ========================================================
    # INTERPOLATORS
    # ========================================================

    lat_interp = RegularGridInterpolator(
        (lines, pixels_grid),
        lat_grid,
        bounds_error=False,
        fill_value=None
    )

    lon_interp = RegularGridInterpolator(
        (lines, pixels_grid),
        lon_grid,
        bounds_error=False,
        fill_value=None
    )

    # ========================================================
    # GEOLOCATE COMPONENT
    # ========================================================

    coords = np.column_stack(
        [
            rows,
            cols
        ]
    )

    lats = lat_interp(
        coords
    )

    lons = lon_interp(
        coords
    )

    # ========================================================
    # CENTROID
    # ========================================================

    centroid_lat = float(
        np.mean(lats)
    )

    centroid_lon = float(
        np.mean(lons)
    )

    north = float(
        np.max(lats)
    )

    south = float(
        np.min(lats)
    )

    east = float(
        np.max(lons)
    )

    west = float(
        np.min(lons)
    )

    # ========================================================
    # APPROXIMATE AREA
    #
    # Estimate using bounding geographic dimensions.
    # This is intentionally labelled approximate.
    # ========================================================

    mean_lat = np.mean(
        [
            north,
            south
        ]
    )

    lat_km = (
        abs(north - south)
        * 111.32
    )

    lon_km = (
        abs(east - west)
        * 111.32
        * np.cos(
            np.radians(mean_lat)
        )
    )

    bounding_box_area = (
        lat_km * lon_km
    )

    # Approximate occupied fraction
    bbox_pixels = (
        (row_max - row_min + 1)
        *
        (col_max - col_min + 1)
    )

    if bbox_pixels > 0:

        component_fraction = (
            component_size /
            bbox_pixels
        )

    else:

        component_fraction = 0

    estimated_area = (
        bounding_box_area
        *
        component_fraction
    )

    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "spill_detected": True,

        "source": (
            "AI candidate detected by "
            "U-Net on Sentinel-1 SAR"
        ),

        "candidate_count": len(
            valid_components
        ),

        "selected_component": {
            "component_id": int(
                component_id
            ),
            "pixels": component_size,
            "min_component_pixels":
                MIN_COMPONENT_PIXELS
        },

        "image_bounds": {
            "row_min": row_min,
            "row_max": row_max,
            "col_min": col_min,
            "col_max": col_max
        },

        "centroid": {
            "latitude": centroid_lat,
            "longitude": centroid_lon
        },

        "bounds": {
            "north": north,
            "south": south,
            "east": east,
            "west": west
        },

        "estimated_area_km2":
            float(estimated_area),

        "bounding_box_area_km2":
            float(bounding_box_area),

        "notes": [
            "This is an AI candidate/suspected slick.",
            "Detection is not independently confirmed as oil.",
            "Area is approximate because Sentinel-1 "
            "geolocation and pixel spacing are not perfectly uniform."
        ]
    }

    # ========================================================
    # SAVE JSON
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
            indent=2
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("CANDIDATE CHARACTERIZATION COMPLETE")
    print("=" * 60)

    print(
        "Candidate pixels:",
        component_size
    )

    print(
        "Centroid:",
        f"{centroid_lat:.6f}, "
        f"{centroid_lon:.6f}"
    )

    print(
        "Estimated area:",
        f"{estimated_area:.3f} km²"
    )

    print(
        "Bounds:"
    )

    print(
        f"  North: {north:.6f}"
    )

    print(
        f"  South: {south:.6f}"
    )

    print(
        f"  East : {east:.6f}"
    )

    print(
        f"  West : {west:.6f}"
    )

    print()
    print("Saved:")
    print(output_json)

    print("=" * 60)

    return result


def main():

    if len(sys.argv) != 4:

        print(
            "Usage:"
        )

        print(
            "python characterize_candidate.py "
            "<MASK_PATH> <SAFE_DIR> <OUTPUT_JSON>"
        )

        sys.exit(1)

    mask_path = sys.argv[1]
    safe_dir = sys.argv[2]
    output_json = sys.argv[3]

    if not os.path.isfile(mask_path):

        raise FileNotFoundError(
            f"Mask not found: {mask_path}"
        )

    if not os.path.isdir(safe_dir):

        raise FileNotFoundError(
            f"SAFE directory not found: {safe_dir}"
        )

    characterize(
        mask_path,
        safe_dir,
        output_json
    )


if __name__ == "__main__":
    main()
