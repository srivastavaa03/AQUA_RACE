import os
import glob
import numpy as np
import rasterio
from rasterio.transform import from_origin

# =========================
# PATHS
# =========================

TILES_DIR = r"D:\oilspill_project\wakashio_tiles"
PRED_DIR = r"D:\oilspill_project\wakashio_predictions"

OUTPUT_MASK = r"D:\oilspill_project\wakashio_oil_mask_corrected.tif"

# =========================
# READ TILE INFORMATION
# =========================

tile_files = sorted(
    glob.glob(os.path.join(TILES_DIR, "tile_*.npz"))
)

if not tile_files:
    raise RuntimeError("No tiles found.")

# =========================
# GET TILE INFORMATION
# =========================

first = np.load(tile_files[0], allow_pickle=True)

tile_size = first["image"].shape[0]

base_transform = rasterio.Affine(
    *first["transform"][:6]
)

crs = str(first["crs"])

# =========================
# FIND TILE EXTENT
# =========================

rows = []
cols = []

for file in tile_files:
    data = np.load(file, allow_pickle=True)

    rows.append(int(data["row"]))
    cols.append(int(data["col"]))

min_row = min(rows)
max_row = max(rows)

min_col = min(cols)
max_col = max(cols)

print("MIN ROW:", min_row)
print("MAX ROW:", max_row)
print("MIN COL:", min_col)
print("MAX COL:", max_col)

# =========================
# OUTPUT SIZE
# =========================

height = max_row - min_row + tile_size
width = max_col - min_col + tile_size

print("OUTPUT SIZE:", width, "x", height)

# =========================
# CORRECT GEOGRAPHIC ORIGIN
# =========================

pixel_width = base_transform.a
pixel_height = base_transform.e

base_lon = base_transform.c
base_lat = base_transform.f

# Shift geographic origin from the first tile's
# original-scene coordinates to MIN ROW / MIN COL.

new_lon = base_lon + (min_col - int(first["col"])) * pixel_width
new_lat = base_lat + (min_row - int(first["row"])) * pixel_height

transform = from_origin(
    new_lon,
    new_lat,
    pixel_width,
    abs(pixel_height)
)

print("NEW ORIGIN:")
print("Longitude:", new_lon)
print("Latitude :", new_lat)

# =========================
# CREATE EMPTY MASK
# =========================

combined = np.zeros(
    (height, width),
    dtype=np.uint8
)

# =========================
# PLACE PREDICTIONS
# =========================

count = 0

for file in tile_files:

    data = np.load(file, allow_pickle=True)

    row = int(data["row"])
    col = int(data["col"])

    tile_name = os.path.basename(file)

    mask_name = tile_name.replace(
        ".npz",
        "_mask.npy"
    )

    mask_path = os.path.join(
        PRED_DIR,
        mask_name
    )

    if not os.path.exists(mask_path):
        continue

    mask = np.load(mask_path)

    # Convert original-scene coordinates
    # to coordinates inside the cropped output.

    out_row = row - min_row
    out_col = col - min_col

    combined[
        out_row:out_row + tile_size,
        out_col:out_col + tile_size
    ] = mask

    count += 1

# =========================
# WRITE GEOTIFF
# =========================

with rasterio.open(
    OUTPUT_MASK,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype="uint8",
    crs=crs,
    transform=transform,
    compress="lzw"
) as dst:

    dst.write(combined, 1)

# =========================
# RESULTS
# =========================

oil_pixels = int(combined.sum())

print()
print("==============================")
print("CORRECTED WAKASHIO MASK")
print("==============================")
print("Tiles placed:", count)
print("Mask size:", width, "x", height)
print("Oil pixels:", oil_pixels)
print("CRS:", crs)
print("Origin:", new_lon, new_lat)
print("Output:", OUTPUT_MASK)