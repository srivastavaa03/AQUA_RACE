import os
import sys
import glob
import numpy as np
import rasterio
import xml.etree.ElementTree as ET
from scipy.interpolate import RegularGridInterpolator


def geolocate_mask(mask_path, safe_dir, output_csv):

    # ========================================================
    # FIND VV ANNOTATION XML
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

    print("Annotation:")
    print(xml_path)

    # ========================================================
    # READ GEOLOCATION GRID
    # ========================================================

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
            int(p.find("line").text)
            for p in points
        )
    )

    pixels = sorted(
        set(
            int(p.find("pixel").text)
            for p in points
        )
    )

    lat_grid = np.zeros(
        (len(lines), len(pixels))
    )

    lon_grid = np.zeros(
        (len(lines), len(pixels))
    )

    line_index = {
        value: index
        for index, value in enumerate(lines)
    }

    pixel_index = {
        value: index
        for index, value in enumerate(pixels)
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

    print("\nGeolocation grid:")
    print("Lines :", len(lines))
    print("Pixels:", len(pixels))

    # ========================================================
    # INTERPOLATORS
    # ========================================================

    lat_interp = RegularGridInterpolator(
        (lines, pixels),
        lat_grid,
        bounds_error=False,
        fill_value=None
    )

    lon_interp = RegularGridInterpolator(
        (lines, pixels),
        lon_grid,
        bounds_error=False,
        fill_value=None
    )

    # ========================================================
    # READ MASK
    # ========================================================

    with rasterio.open(mask_path) as src:

        mask = src.read(1)

    height, width = mask.shape

    rows, cols = np.where(
        mask > 0
    )

    print("\nMask:")
    print("Height:", height)
    print("Width :", width)
    print(
        "Detected pixels:",
        len(rows)
    )

    if len(rows) == 0:

        print(
            "\nNo detected pixels. "
            "Nothing to geolocate."
        )

        os.makedirs(
            os.path.dirname(output_csv),
            exist_ok=True
        )

        with open(
            output_csv,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "row,col,latitude,longitude\n"
            )

        return {
            "detected_pixels": 0,
            "output_csv": output_csv
        }

    # ========================================================
    # GEOLocate
    # ========================================================

    print(
        "\nGeolocating",
        len(rows),
        "detected pixels..."
    )

    coordinates = np.column_stack(
        [rows, cols]
    )

    lats = lat_interp(
        coordinates
    )

    lons = lon_interp(
        coordinates
    )

    # ========================================================
    # SAVE CSV
    # ========================================================

    os.makedirs(
        os.path.dirname(output_csv),
        exist_ok=True
    )

    data = np.column_stack(
        [
            rows,
            cols,
            lats,
            lons
        ]
    )

    np.savetxt(
        output_csv,
        data,
        delimiter=",",
        header="row,col,latitude,longitude",
        comments="",
        fmt=[
            "%d",
            "%d",
            "%.8f",
            "%.8f"
        ]
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "GEOLOCATION COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        "Latitude range :",
        f"{lats.min():.6f}",
        "to",
        f"{lats.max():.6f}"
    )

    print(
        "Longitude range:",
        f"{lons.min():.6f}",
        "to",
        f"{lons.max():.6f}"
    )

    print(
        "\nSaved:"
    )

    print(output_csv)

    print(
        "=" * 60
    )

    return {
        "detected_pixels": len(rows),
        "latitude_min": float(lats.min()),
        "latitude_max": float(lats.max()),
        "longitude_min": float(lons.min()),
        "longitude_max": float(lons.max()),
        "output_csv": output_csv
    }


def main():

    if len(sys.argv) != 4:

        print(
            "Usage:"
        )

        print(
            "python geolocate_mask.py "
            "<MASK_PATH> <SAFE_DIR> <OUTPUT_CSV>"
        )

        sys.exit(1)

    mask_path = sys.argv[1]
    safe_dir = sys.argv[2]
    output_csv = sys.argv[3]

    if not os.path.isfile(mask_path):

        raise FileNotFoundError(
            f"Mask not found: {mask_path}"
        )

    if not os.path.isdir(safe_dir):

        raise FileNotFoundError(
            f"SAFE directory not found: {safe_dir}"
        )

    geolocate_mask(
        mask_path,
        safe_dir,
        output_csv
    )


if __name__ == "__main__":
    main()
