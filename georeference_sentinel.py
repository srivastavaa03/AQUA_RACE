import xml.etree.ElementTree as ET
import glob
import numpy as np
import rasterio
from scipy.interpolate import RegularGridInterpolator
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio.crs import CRS


# =========================
# PATHS
# =========================

SAFE = r"D:\oilspill_project\data\S1A_test_extracted\S1A_IW_GRDH_1SDV_20200810T145024_20200810T145049_033846_03ECAE_2460_COG.SAFE"

VV = glob.glob(SAFE + r"\measurement\*-vv-*.tiff")[0]
ANNOTATION = glob.glob(SAFE + r"\annotation\*-vv-*.xml")[0]

OUTPUT = r"D:\oilspill_project\data\S1_georeferenced.tif"


# =========================
# TARGET AREA
# =========================

TARGET_LAT = 28.5875
TARGET_LON = 48.5678

# Approximate area around target
LAT_RADIUS = 0.10
LON_RADIUS = 0.10


# =========================
# READ GEOLOCATION GRID
# =========================

root = ET.parse(ANNOTATION).getroot()

points = root.findall(".//geolocationGridPoint")

lines = sorted(set(
    int(p.find("line").text)
    for p in points
))

pixels = sorted(set(
    int(p.find("pixel").text)
    for p in points
))

lat_grid = np.zeros((len(lines), len(pixels)))
lon_grid = np.zeros((len(lines), len(pixels)))

for p in points:

    line = int(p.find("line").text)
    pixel = int(p.find("pixel").text)

    i = lines.index(line)
    j = pixels.index(pixel)

    lat_grid[i, j] = float(p.find("latitude").text)
    lon_grid[i, j] = float(p.find("longitude").text)


print("Geolocation grid loaded")
print("Lines :", len(lines))
print("Pixels:", len(pixels))


# =========================
# INTERPOLATORS
# =========================

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


# =========================
# FIND TARGET PIXEL
# =========================

# Dense search around the image
search_lines = np.linspace(
    0,
    max(lines),
    1000
)

search_pixels = np.linspace(
    0,
    max(pixels),
    1500
)

L, P = np.meshgrid(
    search_lines,
    search_pixels,
    indexing="ij"
)

coords = np.column_stack([
    L.ravel(),
    P.ravel()
])

lat_values = lat_interp(coords)
lon_values = lon_interp(coords)

distance = (
    (lat_values - TARGET_LAT) ** 2 +
    (lon_values - TARGET_LON) ** 2
)

idx = np.nanargmin(distance)

target_line = L.ravel()[idx]
target_pixel = P.ravel()[idx]

target_lat = lat_values[idx]
target_lon = lon_values[idx]

print()
print("TARGET LOCATION")
print("--------------------------------")
print("Requested:")
print("Latitude :", TARGET_LAT)
print("Longitude:", TARGET_LON)

print()
print("SAR pixel:")
print("Line     :", target_line)
print("Pixel    :", target_pixel)

print()
print("Interpolated:")
print("Latitude :", target_lat)
print("Longitude:", target_lon)

print()
print("Coordinate error:")
print("Latitude :", abs(target_lat - TARGET_LAT))
print("Longitude:", abs(target_lon - TARGET_LON))


# =========================
# READ SAR IMAGE
# =========================

with rasterio.open(VV) as src:

    data = src.read(1)

    height = src.height
    width = src.width

print()
print("SAR image:")
print("Width :", width)
print("Height:", height)


# =========================
# EXTRACT LOCAL PATCH
# =========================

PATCH = 4096

row_center = int(round(target_line))
col_center = int(round(target_pixel))

row_start = max(
    0,
    row_center - PATCH // 2
)

row_end = min(
    height,
    row_center + PATCH // 2
)

col_start = max(
    0,
    col_center - PATCH // 2
)

col_end = min(
    width,
    col_center + PATCH // 2
)

patch = data[
    row_start:row_end,
    col_start:col_end
]

print()
print("Patch:")
print("Rows:", row_start, "-", row_end)
print("Cols:", col_start, "-", col_end)
print("Shape:", patch.shape)


# =========================
# FIND GEOLOCATION OF
# PATCH CORNERS
# =========================

corner_pixels = np.array([
    [row_start, col_start],
    [row_start, col_end - 1],
    [row_end - 1, col_start],
    [row_end - 1, col_end - 1]
])

corner_lat = lat_interp(corner_pixels)
corner_lon = lon_interp(corner_pixels)

print()
print("Patch corners:")
for i in range(4):
    print(
        i + 1,
        "lat=", corner_lat[i],
        "lon=", corner_lon[i]
    )


# =========================
# CREATE APPROXIMATE GEOREFERENCED TIFF
# =========================

south = float(np.min(corner_lat))
north = float(np.max(corner_lat))
west = float(np.min(corner_lon))
east = float(np.max(corner_lon))

transform = from_bounds(
    west,
    south,
    east,
    north,
    patch.shape[1],
    patch.shape[0]
)


# =========================
# SAVE
# =========================

with rasterio.open(
    OUTPUT,
    "w",
    driver="GTiff",
    height=patch.shape[0],
    width=patch.shape[1],
    count=1,
    dtype=patch.dtype,
    crs=CRS.from_epsg(4326),
    transform=transform,
    compress="deflate"
) as dst:

    dst.write(patch, 1)

print()
print("SUCCESS")
print("--------------------------------")
print("Saved:", OUTPUT)
print("Bounds:")
print("West :", west)
print("South:", south)
print("East :", east)
print("North:", north)