import json
import numpy as np
import rasterio
from rasterio.features import shapes

mask_path = "wakashio_oil_mask.tif"

with rasterio.open(mask_path) as src:
    mask = src.read(1)
    transform = src.transform

    results = [
        {"type": "Feature", "geometry": s, "properties": {"val": int(v)}}
        for s, v in shapes(mask, mask=(mask > 0), transform=transform)
    ]

    # Calculate weighted centroid across all positive spill pixels
    rows, cols = np.where(mask > 0)

    if len(rows) > 0:
        # Convert pixel coordinates to geographic Lat/Lon
        lons, lats = rasterio.transform.xy(transform, rows, cols)
        centroid_lat = float(np.mean(lats))
        centroid_lon = float(np.mean(lons))

        spill_geojson = {
            "type": "FeatureCollection",
            "features": results
        }

        with open("spill_polygon.geojson", "w") as f:
            json.dump(spill_geojson, f, indent=4)

        print(f"\nSpill Centroid Lat: {centroid_lat:.5f}°S, Lon: {centroid_lon:.5f}°E")
        print(f"Total Oil Pixel Count: {len(rows)}")
        print("Exported spill_polygon.geojson successfully.")
    else:
        print("No spill pixels found in raster mask.")
