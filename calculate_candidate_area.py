import numpy as np
import rasterio
import xml.etree.ElementTree as ET
from scipy.interpolate import RegularGridInterpolator

MASK = r"D:\oilspill_project\predictions\sentinel_real_mask.tif"

XML = r"D:\oilspill_project\data\S1A_test_extracted\S1A_IW_GRDH_1SDV_20200810T145024_20200810T145049_033846_03ECAE_2460_COG.SAFE\annotation\s1a-iw-grd-vv-20200810t145024-20200810t145049-033846-03ecae-001-cog.xml"

# Largest component bounds from previous step
ROW_MIN = 12607
ROW_MAX = 13059
COL_MIN = 17590
COL_MAX = 17777

# --------------------------------------------------
# Load mask
# --------------------------------------------------

with rasterio.open(MASK) as src:
    mask = src.read(1)

window = mask[
    ROW_MIN:ROW_MAX + 1,
    COL_MIN:COL_MAX + 1
]

rows, cols = np.where(window == 1)

rows = rows + ROW_MIN
cols = cols + COL_MIN

print("Detected pixels:", len(rows))

# --------------------------------------------------
# Read Sentinel geolocation grid
# --------------------------------------------------

root = ET.parse(XML).getroot()

points = []

for elem in root.iter():
    if elem.tag.endswith("geolocationGridPoint"):
        values = {}

        for child in elem.iter():
            name = child.tag.split("}")[-1]

            if name in ["line", "pixel", "latitude", "longitude"]:
                values[name] = float(child.text)

        if len(values) == 4:
            points.append(values)

print("Geolocation points:", len(points))

if not points:
    raise RuntimeError("No geolocation points found.")

lines = sorted(set(p["line"] for p in points))
pixels = sorted(set(p["pixel"] for p in points))

lat_grid = np.zeros((len(lines), len(pixels)))
lon_grid = np.zeros((len(lines), len(pixels)))

line_index = {v: i for i, v in enumerate(lines)}
pixel_index = {v: i for i, v in enumerate(pixels)}

for p in points:
    i = line_index[p["line"]]
    j = pixel_index[p["pixel"]]

    lat_grid[i, j] = p["latitude"]
    lon_grid[i, j] = p["longitude"]

# --------------------------------------------------
# Interpolate coordinates
# --------------------------------------------------

lat_interp = RegularGridInterpolator(
    (lines, pixels),
    lat_grid,
    bounds_error=False
)

lon_interp = RegularGridInterpolator(
    (lines, pixels),
    lon_grid,
    bounds_error=False
)

sample = np.column_stack((rows, cols))

latitudes = lat_interp(sample)
longitudes = lon_interp(sample)

valid = (
    np.isfinite(latitudes)
    & np.isfinite(longitudes)
)

latitudes = latitudes[valid]
longitudes = longitudes[valid]

print("Valid geolocated pixels:", len(latitudes))

# --------------------------------------------------
# Results
# --------------------------------------------------

print()
print("=" * 60)
print("ACTUAL CANDIDATE GEOLOCATION")
print("=" * 60)

print(f"Latitude range : {latitudes.min():.6f} - {latitudes.max():.6f}")
print(f"Longitude range: {longitudes.min():.6f} - {longitudes.max():.6f}")

print()
print(f"Centroid latitude : {latitudes.mean():.6f}")
print(f"Centroid longitude: {longitudes.mean():.6f}")

print()
print("Bounding box:")
print(f"North: {latitudes.max():.6f}")
print(f"South: {latitudes.min():.6f}")
print(f"East : {longitudes.max():.6f}")
print(f"West : {longitudes.min():.6f}")

# --------------------------------------------------
# Approximate bounding-box dimensions
# --------------------------------------------------

lat_km = (
    latitudes.max() - latitudes.min()
) * 111.32

lon_km = (
    longitudes.max() - longitudes.min()
) * 111.32 * np.cos(
    np.radians(latitudes.mean())
)

print()
print(f"Bounding-box N-S : {lat_km:.2f} km")
print(f"Bounding-box E-W : {lon_km:.2f} km")
print(f"Bounding-box area: {lat_km * lon_km:.2f} km²")

print()
print("IMPORTANT:")
print("This is the bounding-box area, NOT the actual oil area.")
print("Next step: calculate geodesic area of the detected pixels.")