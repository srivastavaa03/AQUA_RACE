import os
import cv2
import numpy as np
import rasterio
import torch
import segmentation_models_pytorch as smp

# =========================
# PATHS
# =========================
IMAGE_DIR = r"D:\oilspill_dataset\val\images"
MASK_DIR = r"D:\oilspill_dataset\val\masks"
MODEL_PATH = r"D:\oilspill_project\best_oilspill_unet.pth"

# =========================
# SETTINGS
# =========================
IMG_SIZE = 512
THRESHOLD = 0.5

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Device:", device)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

# =========================
# MODEL
# =========================
model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights=None,
    in_channels=3,
    classes=1
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=True
)

model.load_state_dict(checkpoint)
model.to(device)
model.eval()

print("Model loaded successfully!")

# =========================
# IMAGE PREPROCESSING
# SAME AS TRAINING
# =========================
def load_image(path):

    with rasterio.open(path) as src:
        image = src.read()

    image = np.transpose(image, (1, 2, 0))

    # Handle channels
    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)

    elif image.shape[2] == 2:
        third = np.mean(image, axis=2, keepdims=True)
        image = np.concatenate([image, third], axis=2)

    else:
        image = image[:, :, :3]

    image = image.astype(np.float32)

    # Percentile normalization
    for c in range(3):
        low = np.percentile(image[:, :, c], 1)
        high = np.percentile(image[:, :, c], 99)

        image[:, :, c] = np.clip(
            (image[:, :, c] - low) / (high - low + 1e-8),
            0,
            1
        )

    image = cv2.resize(
        image,
        (IMG_SIZE, IMG_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    image = np.transpose(image, (2, 0, 1))

    return torch.tensor(image, dtype=torch.float32)


# =========================
# METRICS
# =========================
total_intersection = 0
total_union = 0
total_pred = 0
total_true = 0

dice_scores = []
precision_scores = []
recall_scores = []

image_files = sorted([
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith(".tif")
])

print("Validation images:", len(image_files))

# =========================
# EVALUATION
# =========================
with torch.no_grad():

    for i, filename in enumerate(image_files):

        image_path = os.path.join(IMAGE_DIR, filename)
        mask_path = os.path.join(MASK_DIR, filename)

        image = load_image(image_path)

        with rasterio.open(mask_path) as src:
            mask = src.read(1)

        mask = (mask > 0).astype(np.uint8)

        mask = cv2.resize(
            mask,
            (IMG_SIZE, IMG_SIZE),
            interpolation=cv2.INTER_NEAREST
        )

        image = image.unsqueeze(0).to(device)

        output = model(image)

        probability = torch.sigmoid(output)[0, 0].cpu().numpy()

        prediction = (probability >= THRESHOLD).astype(np.uint8)

        true_mask = mask

        # Pixels
        intersection = np.logical_and(
            prediction == 1,
            true_mask == 1
        ).sum()

        union = np.logical_or(
            prediction == 1,
            true_mask == 1
        ).sum()

        pred_pixels = (prediction == 1).sum()
        true_pixels = (true_mask == 1).sum()

        # Dice
        dice = (
            2 * intersection /
            (pred_pixels + true_pixels + 1e-8)
        )

        # Precision
        precision = (
            intersection /
            (pred_pixels + 1e-8)
        )

        # Recall
        recall = (
            intersection /
            (true_pixels + 1e-8)
        )

        total_intersection += intersection
        total_union += union
        total_pred += pred_pixels
        total_true += true_pixels

        dice_scores.append(dice)
        precision_scores.append(precision)
        recall_scores.append(recall)

        if (i + 1) % 20 == 0:
            print(f"Processed {i + 1}/{len(image_files)}")


# =========================
# FINAL RESULTS
# =========================
IoU = total_intersection / (total_union + 1e-8)

Dice = np.mean(dice_scores)
Precision = np.mean(precision_scores)
Recall = np.mean(recall_scores)

print("\n==============================")
print("MODEL EVALUATION COMPLETE")
print("==============================")

print(f"IoU       : {IoU:.4f}")
print(f"Dice      : {Dice:.4f}")
print(f"Precision : {Precision:.4f}")
print(f"Recall    : {Recall:.4f}")

print("==============================")