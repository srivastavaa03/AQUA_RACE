import pandas as pd
import numpy as np

INPUT = r"D:\oilspill_project\predictions\sentinel_detection_points.csv"
OUTPUT = r"D:\oilspill_project\predictions\sentinel_detection_clusters.csv"

df = pd.read_csv(INPUT)

lat = df["latitude"].to_numpy()
lon = df["longitude"].to_numpy()

# Approximately 2 km grid cells
# This is only for finding broad detection regions.
LAT_CELL = 0.02
LON_CELL = 0.02

df["lat_cell"] = np.floor(lat / LAT_CELL).astype(int)
df["lon_cell"] = np.floor(lon / LON_CELL).astype(int)

groups = (
    df.groupby(["lat_cell", "lon_cell"])
    .agg(
        points=("latitude", "size"),
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean")
    )
    .reset_index()
)

groups = groups.sort_values(
    "points",
    ascending=False
)

groups.to_csv(
    OUTPUT,
    index=False
)

print("=" * 60)
print("DETECTION REGIONS")
print("=" * 60)

print("Total sampled detections:", len(df))
print("Grid regions:", len(groups))

print("\nLargest detection regions:")
print(
    groups.head(20).to_string(index=False)
)

print("\nSaved:")
print(OUTPUT)