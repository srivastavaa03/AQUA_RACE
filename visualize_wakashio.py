import rasterio
import numpy as np
import matplotlib.pyplot as plt

VV = r"D:\oilspill_project\wakashio_processed.data\Sigma0_VV_dB.img"
MASK = r"D:\oilspill_project\wakashio_oil_mask.tif"
OUT = r"D:\oilspill_project\wakashio_overlay.png"

with rasterio.open(VV) as src:
    vv = src.read(1)
    transform = src.transform

with rasterio.open(MASK) as src:
    mask = src.read(1)

print("VV shape:", vv.shape)
print("Mask shape:", mask.shape)

# Convert VV to display dB
valid = vv > 0
vv_db = np.full(vv.shape, -40.0, dtype=np.float32)
vv_db[valid] = 10 * np.log10(np.maximum(vv[valid], 1e-10))

# Display only area containing predictions
rows, cols = np.where(mask > 0)

if len(rows) == 0:
    print("No predicted oil found.")
    exit()

r1 = max(0, rows.min() - 512)
r2 = min(mask.shape[0], rows.max() + 512)
c1 = max(0, cols.min() - 512)
c2 = min(mask.shape[1], cols.max() + 512)

image = vv_db[r1:r2, c1:c2]
prediction = mask[r1:r2, c1:c2]

# Improve contrast
vmin = np.percentile(image[image > -40], 2)
vmax = np.percentile(image[image > -40], 98)

plt.figure(figsize=(12, 10))

plt.imshow(
    image,
    cmap="gray",
    vmin=vmin,
    vmax=vmax
)

# Prediction overlay
overlay = np.ma.masked_where(prediction == 0, prediction)

plt.imshow(
    overlay,
    cmap="autumn",
    alpha=0.55
)

plt.title("Wakashio Sentinel-1 VV + AI Oil-Spill Prediction")
plt.axis("off")

plt.savefig(
    OUT,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print("\n==============================")
print("VISUALIZATION COMPLETE")
print("==============================")
print("Output:", OUT)
print("Predicted pixels:", int(mask.sum()))
print("Displayed area:", image.shape)
