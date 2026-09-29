import os
import numpy as np
import rasterio
from rasterio.windows import Window
from tqdm import tqdm

# =========================
# PATHS
# =========================

VV_PATH = r"D:\oilspill_project\wakashio_processed.data\Sigma0_VV_dB.img"
VH_PATH = r"D:\oilspill_project\wakashio_processed.data\Sigma0_VH_dB.img"

OUTPUT_DIR = r"D:\oilspill_project\wakashio_tiles"

TILE_SIZE = 512
STRIDE = 512

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# OPEN SAR DATA
# =========================

vv = rasterio.open(VV_PATH)
vh = rasterio.open(VH_PATH)

print("Scene size:", vv.width, "x", vv.height)
print("CRS:", vv.crs)

# =========================
# TILE PROCESSING
# =========================

tile_id = 0
saved = 0

rows = range(0, vv.height - TILE_SIZE + 1, STRIDE)
cols = range(0, vv.width - TILE_SIZE + 1, STRIDE)

total = len(rows) * len(cols)

print("Total possible tiles:", total)

for row in tqdm(rows, desc="Creating tiles"):

    for col in cols:

        window = Window(
            col,
            row,
            TILE_SIZE,
            TILE_SIZE
        )

        vv_data = vv.read(1, window=window).astype(np.float32)
        vh_data = vh.read(1, window=window).astype(np.float32)

        # =========================
        # VALID PIXELS
        # =========================

        valid = (vv_data > 0) & (vh_data > 0)

        # Skip tiles containing almost no valid SAR data
        valid_ratio = np.mean(valid)

        if valid_ratio < 0.50:
            continue

        # =========================
        # LINEAR -> dB
        # =========================

        vv_db = np.full_like(vv_data, -60.0)
        vh_db = np.full_like(vh_data, -60.0)

        vv_db[valid] = 10.0 * np.log10(
            np.maximum(vv_data[valid], 1e-10)
        )

        vh_db[valid] = 10.0 * np.log10(
            np.maximum(vh_data[valid], 1e-10)
        )

        # =========================
        # 3 CHANNELS
        # Same as train.py
        # =========================

        third_channel = (vv_db + vh_db) / 2.0

        image = np.stack(
            [vv_db, vh_db, third_channel],
            axis=2
        ).astype(np.float32)

        # =========================
        # NORMALIZATION
        # Same as train.py
        # =========================

        for c in range(3):

            channel = image[:, :, c]

            low = np.percentile(channel, 1)
            high = np.percentile(channel, 99)

            image[:, :, c] = np.clip(
                (channel - low) /
                (high - low + 1e-8),
                0,
                1
            )

        # =========================
        # SAVE
        # =========================

        output_path = os.path.join(
            OUTPUT_DIR,
            f"tile_{tile_id:05d}.npz"
        )

        transform = rasterio.windows.transform(
            window,
            vv.transform
        )

        np.savez_compressed(
            output_path,
            image=image,
            transform=np.array(transform),
            crs=str(vv.crs),
            row=row,
            col=col
        )

        saved += 1
        tile_id += 1

print()
print("================================")
print("WAKASHIO PREPARATION COMPLETE")
print("================================")
print("Tiles saved:", saved)
print("Output:", OUTPUT_DIR)

vv.close()
vh.close()