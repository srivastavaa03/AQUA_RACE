import os
import cv2
import numpy as np
import rasterio
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

VV_PATH = r"D:\oilspill_project\data\S1A_test_extracted\S1A_IW_GRDH_1SDV_20200810T145024_20200810T145049_033846_03ECAE_2460_COG.SAFE\measurement\s1a-iw-grd-vv-20200810t145024-20200810t145049-033846-03ecae-001-cog.tiff"

MASK_PATH = r"D:\oilspill_project\predictions\sentinel_real_mask.tif"

OUTPUT = r"D:\oilspill_project\predictions\candidate_spill_visual.png"


# Candidate SAR pixel
ROW = 12898
COL = 17640

# 2048 x 2048 area around candidate
SIZE = 2048

HALF = SIZE // 2

R1 = ROW - HALF
R2 = ROW + HALF

C1 = COL - HALF
C2 = COL + HALF


# ============================================================
# READ VV
# ============================================================

with rasterio.open(VV_PATH) as src:

    vv = src.read(
        1,
        window=((R1, R2), (C1, C2))
    ).astype(np.float32)


# ============================================================
# READ MASK
# ============================================================

with rasterio.open(MASK_PATH) as src:

    mask = src.read(
        1,
        window=((R1, R2), (C1, C2))
    )


# ============================================================
# NORMALIZE VV FOR DISPLAY
# ============================================================

low = np.percentile(vv, 2)
high = np.percentile(vv, 98)

vv_display = np.clip(
    (vv - low) / (high - low + 1e-8),
    0,
    1
)


# ============================================================
# CREATE RGB-LIKE IMAGE
# ============================================================

background = np.stack(
    [
        vv_display,
        vv_display,
        vv_display
    ],
    axis=2
)


# Highlight prediction in red

background[mask > 0, 0] = 1.0
background[mask > 0, 1] *= 0.25
background[mask > 0, 2] *= 0.25


# ============================================================
# SAVE
# ============================================================

plt.figure(
    figsize=(12, 12)
)

plt.imshow(background)

plt.title(
    "Sentinel-1 VV + U-Net Oil Spill Prediction"
)

plt.axis("off")

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# STATS
# ============================================================

oil_pixels = int((mask > 0).sum())

print("=" * 60)
print("CANDIDATE VISUALIZATION")
print("=" * 60)

print("Candidate row:", ROW)
print("Candidate col:", COL)

print("Patch:", SIZE, "x", SIZE)

print("Predicted oil pixels:", oil_pixels)

print(
    "Patch coverage:",
    f"{100 * oil_pixels / mask.size:.2f}%"
)

print("\nSaved:")
print(OUTPUT)

print("=" * 60)