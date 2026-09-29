import rasterio
import numpy as np
from scipy.ndimage import label

MASK = r"D:\oilspill_project\predictions\sentinel_real_mask.tif"

ROW = 12898
COL = 17640
SIZE = 2048

half = SIZE // 2

with rasterio.open(MASK) as src:
    mask = src.read(
        1,
        window=(
            (ROW - half, ROW + half),
            (COL - half, COL + half)
        )
    )

labels, count = label(mask)

sizes = np.bincount(labels.ravel())

components = []

for component_id in range(1, count + 1):

    pixels = sizes[component_id]

    if pixels == 0:
        continue

    ys, xs = np.where(labels == component_id)

    y_min = int(ys.min())
    y_max = int(ys.max())
    x_min = int(xs.min())
    x_max = int(xs.max())

    touches_border = (
        y_min == 0 or
        x_min == 0 or
        y_max == mask.shape[0] - 1 or
        x_max == mask.shape[1] - 1
    )

    components.append(
        (
            pixels,
            y_min,
            y_max,
            x_min,
            x_max,
            touches_border
        )
    )

components.sort(reverse=True)

print("=" * 60)
print("TOP DETECTION COMPONENTS")
print("=" * 60)

for i, c in enumerate(components[:10], 1):

    pixels, y1, y2, x1, x2, border = c

    print(
        f"Component {i}: "
        f"pixels={pixels}, "
        f"bbox=rows {y1}-{y2}, "
        f"cols {x1}-{x2}, "
        f"border={border}"
    )