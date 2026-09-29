import json
import os
import numpy as np
import rasterio
from scipy import ndimage


MASK_PATH = r"D:\oilspill_project\predictions\predicted_mask.tif"
OUTPUT_PATH = r"D:\oilspill_project\predictions\spill_characterization.json"


def pixel_area_km2(transform, latitude):
    """
    Approximate pixel area using geographic coordinates.
    """
    meters_per_degree_lat = 111320.0
    meters_per_degree_lon = (
        111320.0 * np.cos(np.radians(latitude))
    )

    pixel_width_m = abs(transform.a) * meters_per_degree_lon
    pixel_height_m = abs(transform.e) * meters_per_degree_lat

    return (pixel_width_m * pixel_height_m) / 1_000_000


def main():

    if not os.path.exists(MASK_PATH):
        print("ERROR: predicted_mask.tif not found")
        return

    with rasterio.open(MASK_PATH) as src:

        mask = src.read(1) > 0
        transform = src.transform
        crs = str(src.crs)

        height, width = mask.shape

    total_pixels = int(mask.sum())

    if total_pixels == 0:

        result = {
            "spill_detected": False,
            "total_area_km2": 0.0,
            "component_count": 0
        }

        with open(OUTPUT_PATH, "w") as f:
            json.dump(result, f, indent=4)

        print("No oil spill detected.")
        return

    # --------------------------------------------------
    # Connected components
    # --------------------------------------------------

    labeled, component_count = ndimage.label(mask)

    component_sizes = ndimage.sum(
        mask,
        labeled,
        range(1, component_count + 1)
    )

    component_sizes = np.asarray(component_sizes)

    largest_index = int(np.argmax(component_sizes)) + 1
    largest_pixels = int(component_sizes[largest_index - 1])

    # --------------------------------------------------
    # Centroid of detected pixels
    # --------------------------------------------------

    rows, cols = np.where(mask)

    xs, ys = rasterio.transform.xy(
        transform,
        rows,
        cols
    )

    longitude = float(np.mean(xs))
    latitude = float(np.mean(ys))

    # --------------------------------------------------
    # Area
    # --------------------------------------------------

    area_per_pixel = pixel_area_km2(
        transform,
        latitude
    )

    total_area_km2 = total_pixels * area_per_pixel
    largest_area_km2 = largest_pixels * area_per_pixel

    # --------------------------------------------------
    # Geographic bounds
    # --------------------------------------------------

    north = float(max(ys))
    south = float(min(ys))
    west = float(min(xs))
    east = float(max(xs))

    # --------------------------------------------------
    # Border contact
    # --------------------------------------------------

    border = np.zeros_like(mask)

    border[0, :] = True
    border[-1, :] = True
    border[:, 0] = True
    border[:, -1] = True

    border_pixels = int(np.sum(mask & border))

    border_percentage = (
        border_pixels / total_pixels * 100
    )

    # --------------------------------------------------
    # Largest component percentage
    # --------------------------------------------------

    largest_percentage = (
        largest_pixels / total_pixels * 100
    )

    # --------------------------------------------------
    # Component statistics
    # --------------------------------------------------

    components = []

    sorted_sizes = sorted(
        component_sizes,
        reverse=True
    )

    for i, size in enumerate(sorted_sizes[:10]):

        components.append({
            "rank": i + 1,
            "pixels": int(size),
            "area_km2": round(
                float(size * area_per_pixel),
                4
            )
        })

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    result = {

        "spill_detected": True,

        "crs": crs,

        "image_dimensions": {
            "width": width,
            "height": height
        },

        "total_oil_pixels": total_pixels,

        "total_area_km2": round(
            float(total_area_km2),
            4
        ),

        "largest_component": {

            "pixels": largest_pixels,

            "area_km2": round(
                float(largest_area_km2),
                4
            ),

            "percentage_of_spill": round(
                float(largest_percentage),
                2
            )
        },

        "component_count": int(
            component_count
        ),

        "top_components": components,

        "centroid": {

            "latitude": round(
                latitude,
                8
            ),

            "longitude": round(
                longitude,
                8
            )
        },

        "bounds": {

            "north": round(
                north,
                8
            ),

            "south": round(
                south,
                8
            ),

            "west": round(
                west,
                8
            ),

            "east": round(
                east,
                8
            )
        },

        "border_contact": {

            "pixels": border_pixels,

            "percentage": round(
                float(border_percentage),
                4
            )
        },

        "source_mask": MASK_PATH
    }

    with open(
        OUTPUT_PATH,
        "w"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )

    # --------------------------------------------------
    # Terminal summary
    # --------------------------------------------------

    print()
    print("=" * 55)
    print("       SPILL CHARACTERIZATION")
    print("=" * 55)

    print(
        f"Spill detected: YES"
    )

    print(
        f"Total area: {total_area_km2:.4f} km²"
    )

    print(
        f"Largest region: {largest_area_km2:.4f} km²"
    )

    print(
        f"Largest region: {largest_percentage:.2f}%"
    )

    print(
        f"Components: {component_count}"
    )

    print(
        f"Centroid: {latitude:.8f}, {longitude:.8f}"
    )

    print()
    print("Output:")
    print(OUTPUT_PATH)
    print("=" * 55)


if __name__ == "__main__":
    main()