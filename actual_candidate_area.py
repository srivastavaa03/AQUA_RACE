import numpy as np
import rasterio
import xml.etree.ElementTree as ET
from scipy.interpolate import RegularGridInterpolator

MASK = r"D:\oilspill_project\predictions\sentinel_real_mask.tif"

XML = r"D:\oilspill_project\data\S1A_test_extracted\S1A_IW_GRDH_1SDV_20200810T145024_20200810T145049_033846_03ECAE_2460_COG.SAFE\annotation\s1a-iw-grd-vv-20200810t145024-20200810t145049-033846-03ecae-001-cog.xml"

ROW_MIN = 12607
ROW_MAX = 13059
COL_MIN = 17590
COL_MAX = 17777

# Load mask
with rasterio.open(MASK) as src:
    mask = src.read(1)

patch = mask[
    ROW_MIN:ROW_MAX + 1,
    COL_MIN:COL_MAX + 1
]

rows, cols = np.where(patch == 1)

rows = rows + ROW_MIN
cols = cols + COL_MIN

print("Positive pixels in candidate box:", len(rows))

# Read geolocation grid
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

coords = np.column_stack((rows, cols))

lat = lat_interp(coords)
lon = lon_interp(coords)

valid = np.isfinite(lat) & np.isfinite(lon)

lat = lat[valid]
lon = lon[valid]

print("Geolocated pixels:", len(lat))

# Estimate local pixel dimensions
# Use neighboring geolocation-grid points around the candidate.

center_row = np.mean(rows)
center_col = np.mean(cols)

# Small offsets in SAR pixel coordinates
dr = 10
dc = 10

p0 = np.array([[center_row, center_col]])

p_row = np.array([[center_row + dr, center_col]])
p_col = np.array([[center_row, center_col + dc]])

lat0 = lat_interp(p0)[0]
lon0 = lon_interp(p0)[0]

lat_r = lat_interp(p_row)[0]
lon_r = lon_interp(p_row)[0]

lat_c = lat_interp(p_col)[0]
lon_c = lon_interp(p_col)[0]

# Earth radius approximation
R = 6371.0

def distance_km(lat1, lon1, lat2, lon2):

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)
    dlat = lat2 - lat1

    dlon = np.radians(lon2 - lon1)

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 2 * R * np.arcsin(np.sqrt(a))

row_distance = distance_km(
    lat0, lon0,
    lat_r, lon_r
)

col_distance = distance_km(
    lat0, lon0,
    lat_c, lon_c
)

# Convert 10-pixel distance to 1-pixel distance
pixel_height_km = row_distance / dr
pixel_width_km = col_distance / dc

pixel_area_km2 = (
    pixel_height_km *
    pixel_width_km
)

detected_area_km2 = (
    len(lat) *
    pixel_area_km2
)

print()
print("=" * 60)
print("ACTUAL DETECTED AREA ESTIMATE")
print("=" * 60)

print(f"Pixel height : {pixel_height_km * 1000:.2f} m")
print(f"Pixel width  : {pixel_width_km * 1000:.2f} m")
print(f"Pixel area   : {pixel_area_km2:.8f} km²")

print()
print(f"Detected pixels: {len(lat)}")
print(f"Estimated detected area: {detected_area_km2:.3f} km²")

print()
print("NOTE:")
print("This is an approximate area because GRD pixel spacing")
print("and geolocation are not perfectly uniform.")
