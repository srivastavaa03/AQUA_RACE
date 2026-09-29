import rasterio
import numpy as np

MASK = r"D:\oilspill_project\wakashio_oil_mask.tif"

with rasterio.open(MASK) as src:
    mask = src.read(1)
    transform = src.transform
    crs = src.crs

print("\n==============================")
print("WAKASHIO MASK ANALYSIS")
print("==============================")

print("Size:", mask.shape)
print("CRS:", crs)
print("Oil pixels:", int(mask.sum()))

# Find coordinates of all predicted oil pixels
rows, cols = np.where(mask > 0)

if len(rows) == 0:
    print("No oil detected.")
    exit()

# Overall bounding box
min_row = rows.min()
max_row = rows.max()
min_col = cols.min()
max_col = cols.max()

lon_min, lat_max = rasterio.transform.xy(
    transform, min_row, min_col, offset="ul"
)

lon_max, lat_min = rasterio.transform.xy(
    transform, max_row, max_col, offset="lr"
)

# Center of all predicted pixels
center_row = rows.mean()
center_col = cols.mean()

center_lon, center_lat = rasterio.transform.xy(
    transform, center_row, center_col
)

print("\nOVERALL DETECTION")
print("------------------------------")
print("Oil pixels:", len(rows))
print("Center latitude:", center_lat)
print("Center longitude:", center_lon)

print("\nBounding box")
print("Latitude:", lat_min, "to", lat_max)
print("Longitude:", lon_min, "to", lon_max)

print("\nPixel bounding box")
print("Rows:", min_row, "to", max_row)
print("Columns:", min_col, "to", max_col)

# Divide image into large blocks to see where predictions are concentrated
block_size = 1024

print("\nDETECTION DENSITY BY BLOCK")
print("------------------------------")

results = []

for r in range(0, mask.shape[0], block_size):
    for c in range(0, mask.shape[1], block_size):

        block = mask[
            r:min(r + block_size, mask.shape[0]),
            c:min(c + block_size, mask.shape[1])
        ]

        pixels = int(block.sum())

        if pixels > 100:
            lat1, lon1 = rasterio.transform.xy(
                transform, r, c, offset="ul"
            )

            results.append((pixels, lat1, lon1))

results.sort(reverse=True)

for i, (pixels, lat, lon) in enumerate(results[:20], 1):
    print(
        f"Block {i}: "
        f"{pixels} pixels | "
        f"Lat {lat:.5f} | Lon {lon:.5f}"
    )

print("\n==============================")
print("ANALYSIS COMPLETE")
print("==============================")