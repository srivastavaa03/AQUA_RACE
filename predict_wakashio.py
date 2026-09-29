import os
import glob
import numpy as np
import torch
import segmentation_models_pytorch as smp
from tqdm import tqdm

# =========================
# PATHS
# =========================

MODEL_PATH = r"D:\oilspill_project\best_oilspill_unet.pth"
TILES_DIR = r"D:\oilspill_project\wakashio_tiles"
OUTPUT_DIR = r"D:\oilspill_project\wakashio_predictions"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# DEVICE
# =========================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", DEVICE)

# =========================
# LOAD MODEL
# =========================

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights=None,
    in_channels=3,
    classes=1
)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )
)

model = model.to(DEVICE)
model.eval()

print("Model loaded successfully.")

# =========================
# GET TILES
# =========================

files = sorted(
    glob.glob(
        os.path.join(
            TILES_DIR,
            "*.npz"
        )
    )
)

print("Tiles found:", len(files))

# =========================
# PREDICTION
# =========================

threshold = 0.5
total_oil_pixels = 0

for file in tqdm(files, desc="Predicting"):

    data = np.load(file)

    image = data["image"]

    # HWC -> CHW
    image = np.transpose(
        image,
        (2, 0, 1)
    )

    image = torch.from_numpy(
        image
    ).float().unsqueeze(0).to(DEVICE)

    # =========================
    # MODEL
    # =========================

    with torch.no_grad():

        output = model(image)

        probability = torch.sigmoid(
            output
        )

    mask = (
        probability[0, 0].cpu().numpy()
        >= threshold
    ).astype(np.uint8)

    oil_pixels = int(mask.sum())

    total_oil_pixels += oil_pixels

    # =========================
    # SAVE MASK
    # =========================

    tile_name = os.path.basename(file)

    output_name = tile_name.replace(
        ".npz",
        "_mask.npy"
    )

    np.save(
        os.path.join(
            OUTPUT_DIR,
            output_name
        ),
        mask
    )

print()
print("==============================")
print("WAKASHIO PREDICTION COMPLETE")
print("==============================")
print("Tiles processed:", len(files))
print("Total predicted oil pixels:", total_oil_pixels)
print("Output:", OUTPUT_DIR)