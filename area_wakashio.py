import rasterio
import numpy as np
from pyproj import Geod

MASK = r"D:\oilspill_project\wakashio_oil_mask.tif"

with rasterio.open(MASK) as src:
    mask = src.read(1)
    transform = src.transform

geod = Geod(ellps="WGS84")

rows, cols = np.where(mask > 0)

pixel_area = 0.0

for r, c in zip(rows, cols):
    lon1, lat1 = rasterio.transform.xy(transform, r, c, offset="ul")
    lon2, lat2 = rasterio.transform.xy(transform, r, c, offset="lr")

    area, _ = geod.polygon_area_perimeter(
        [lon1, lon2, lon2, lon1],
        [lat1, lat1, lat2, lat2]
    )

    pixel_area += abs(area)

print("\n==============================")
print("WAKASHIO PREDICTED AREA")
print("==============================")

print("Oil pixels:", len(rows))
print("Area:", pixel_area, "m²")
print("Area:", pixel_area / 1_000_000, "km²")

print("==============================")