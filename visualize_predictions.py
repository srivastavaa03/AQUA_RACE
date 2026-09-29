import os
import cv2
import numpy as np
import rasterio
import torch
import segmentation_models_pytorch as smp

IMAGE_DIR = r"D:\oilspill_dataset\val\images"
MASK_DIR = r"D:\oilspill_dataset\val\masks"
MODEL_PATH = r"D:\oilspill_project\best_oilspill_unet.pth"
OUTPUT_DIR = r"D:\oilspill_project\prediction_examples"

IMG_SIZE = 512
THRESHOLD = 0.5

os.makedirs(OUTPUT_DIR, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Device:", device)

# Load model
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

print("Model loaded!")

def load_image(path):

    with rasterio.open(path) as src:
        image = src.read()

    image = np.transpose(image, (1, 2, 0))

    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)

    elif image.shape[2] == 2:
        third = np.mean(image, axis=2, keepdims=True)
        image = np.concatenate([image, third], axis=2)

    else:
        image = image[:, :, :3]

    image = image.astype(np.float32)

    for c in range(3):
        low = np.percentile(image[:, :, c], 1)
        high = np.percentile(image[:, :, c], 99)

        image[:, :, c] = np.clip(
            (image[:, :, c] - low) /
            (high - low + 1e-8),
            0,
            1
        )

    original_visual = image[:, :, 0].copy()

    image = cv2.resize(
        image,
        (IMG_SIZE, IMG_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    image = np.transpose(image, (2, 0, 1))

    tensor = torch.tensor(
        image,
        dtype=torch.float32
    )

    return tensor, original_visual


files = sorted([
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith(".tif")
])

saved = 0

with torch.no_grad():

    for filename in files:

        image_path = os.path.join(IMAGE_DIR, filename)
        mask_path = os.path.join(MASK_DIR, filename)

        image, original_visual = load_image(image_path)

        with rasterio.open(mask_path) as src:
            true_mask = src.read(1)

        true_mask = (true_mask > 0).astype(np.uint8)

        image_input = image.unsqueeze(0).to(device)

        output = model(image_input)

        probability = torch.sigmoid(output)[0, 0].cpu().numpy()

        prediction = (
            probability >= THRESHOLD
        ).astype(np.uint8)

        # Convert original SAR image to 512x512
        sar = cv2.resize(
            original_visual,
            (IMG_SIZE, IMG_SIZE),
            interpolation=cv2.INTER_AREA
        )

        sar = (sar * 255).astype(np.uint8)

        # Ground truth
        gt = cv2.resize(
            true_mask,
            (IMG_SIZE, IMG_SIZE),
            interpolation=cv2.INTER_NEAREST
        )

        gt = gt * 255

        pred = prediction * 255

        # Create overlays
        gt_overlay = cv2.cvtColor(
            sar,
            cv2.COLOR_GRAY2BGR
        )

        pred_overlay = cv2.cvtColor(
            sar,
            cv2.COLOR_GRAY2BGR
        )

        # Ground truth = green
        gt_overlay[gt > 0] = (0, 255, 0)

        # Prediction = red
        pred_overlay[pred > 0] = (0, 0, 255)

        # Save files
        base = os.path.splitext(filename)[0]

        cv2.imwrite(
            os.path.join(
                OUTPUT_DIR,
                f"{base}_sar.png"
            ),
            sar
        )

        cv2.imwrite(
            os.path.join(
                OUTPUT_DIR,
                f"{base}_ground_truth.png"
            ),
            gt
        )

        cv2.imwrite(
            os.path.join(
                OUTPUT_DIR,
                f"{base}_prediction.png"
            ),
            pred
        )

        cv2.imwrite(
            os.path.join(
                OUTPUT_DIR,
                f"{base}_ground_truth_overlay.png"
            ),
            gt_overlay
        )

        cv2.imwrite(
            os.path.join(
                OUTPUT_DIR,
                f"{base}_prediction_overlay.png"
            ),
            pred_overlay
        )

        saved += 1

        print(f"Saved example {saved}: {filename}")

        if saved >= 5:
            break

print("\n==============================")
print("VISUALIZATION COMPLETE")
print("==============================")
print("Saved in:")
print(OUTPUT_DIR)