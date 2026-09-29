import os
import numpy as np
import torch
import rasterio
import cv2
import segmentation_models_pytorch as smp

from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm


# =========================
# PATHS
# =========================

TRAIN_IMAGES = r"D:\oilspill_dataset\train\images"
TRAIN_MASKS = r"D:\oilspill_dataset\train\masks"

VAL_IMAGES = r"D:\oilspill_dataset\val\images"
VAL_MASKS = r"D:\oilspill_dataset\val\masks"


# =========================
# SETTINGS
# =========================

IMAGE_SIZE = 512
BATCH_SIZE = 4
EPOCHS = 30
LEARNING_RATE = 1e-4

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", DEVICE)

if DEVICE == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))


# =========================
# DATASET
# =========================

class OilSpillDataset(Dataset):

    def __init__(self, image_dir, mask_dir):

        self.image_dir = image_dir
        self.mask_dir = mask_dir

        self.files = sorted([
            f for f in os.listdir(image_dir)
            if f.lower().endswith(".tif")
        ])

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):

        filename = self.files[idx]

        image_path = os.path.join(
            self.image_dir,
            filename
        )

        mask_path = os.path.join(
            self.mask_dir,
            filename
        )

        # =========================
        # READ SATELLITE IMAGE
        # =========================

        with rasterio.open(image_path) as src:
            image = src.read()

        # Convert CHW -> HWC

        image = np.transpose(
            image,
            (1, 2, 0)
        )

        # =========================
        # HANDLE CHANNELS
        # =========================

        if image.shape[2] == 1:

            image = np.repeat(
                image,
                3,
                axis=2
            )

        elif image.shape[2] == 2:

            third_channel = np.mean(
                image,
                axis=2,
                keepdims=True
            )

            image = np.concatenate(
                [image, third_channel],
                axis=2
            )

        elif image.shape[2] >= 3:

            image = image[:, :, :3]


        # =========================
        # NORMALIZE
        # =========================

        image = image.astype(
            np.float32
        )

        for c in range(3):

            channel = image[:, :, c]

            low = np.percentile(
                channel,
                1
            )

            high = np.percentile(
                channel,
                99
            )

            image[:, :, c] = np.clip(
                (channel - low) /
                (high - low + 1e-8),
                0,
                1
            )


        # =========================
        # READ MASK
        # =========================

        with rasterio.open(mask_path) as src:
            mask = src.read(1)

        # 0 = background
        # 1 = oil

        mask = (
            mask > 0
        ).astype(np.float32)


        # =========================
        # RESIZE
        # =========================

        image = cv2.resize(
            image,
            (IMAGE_SIZE, IMAGE_SIZE),
            interpolation=cv2.INTER_AREA
        )

        mask = cv2.resize(
            mask,
            (IMAGE_SIZE, IMAGE_SIZE),
            interpolation=cv2.INTER_NEAREST
        )


        # =========================
        # HWC -> CHW
        # =========================

        image = np.transpose(
            image,
            (2, 0, 1)
        )


        # =========================
        # NUMPY -> TORCH
        # =========================

        image = torch.tensor(
            image,
            dtype=torch.float32
        )

        mask = torch.tensor(
            mask,
            dtype=torch.float32
        )

        mask = mask.unsqueeze(0)

        return image, mask


# =========================
# DATA
# =========================

train_dataset = OilSpillDataset(
    TRAIN_IMAGES,
    TRAIN_MASKS
)

val_dataset = OilSpillDataset(
    VAL_IMAGES,
    VAL_MASKS
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

print(
    "Training images:",
    len(train_dataset)
)

print(
    "Validation images:",
    len(val_dataset)
)


# =========================
# MODEL
# =========================

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=1
)

model = model.to(DEVICE)


# =========================
# LOSS
# =========================

dice_loss = smp.losses.DiceLoss(
    mode="binary"
)

bce_loss = smp.losses.SoftBCEWithLogitsLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# =========================
# TRAINING
# =========================

best_val_loss = float("inf")

for epoch in range(EPOCHS):

    model.train()

    train_loss = 0.0

    progress = tqdm(
        train_loader,
        desc=f"Epoch {epoch + 1}/{EPOCHS}"
    )

    for images, masks in progress:

        images = images.to(DEVICE)
        masks = masks.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = (
            dice_loss(outputs, masks)
            + bce_loss(outputs, masks)
        )

        loss.backward()

        optimizer.step()

        train_loss += loss.item()

        progress.set_postfix(
            loss=f"{loss.item():.4f}"
        )


    train_loss /= len(train_loader)


    # =========================
    # VALIDATION
    # =========================

    model.eval()

    val_loss = 0.0

    with torch.no_grad():

        for images, masks in val_loader:

            images = images.to(DEVICE)
            masks = masks.to(DEVICE)

            outputs = model(images)

            loss = (
                dice_loss(outputs, masks)
                + bce_loss(outputs, masks)
            )

            val_loss += loss.item()


    val_loss /= len(val_loader)


    print(
        f"\nEpoch {epoch + 1}: "
        f"Train Loss = {train_loss:.4f} "
        f"Val Loss = {val_loss:.4f}"
    )


    # =========================
    # SAVE BEST MODEL
    # =========================

    if val_loss < best_val_loss:

        best_val_loss = val_loss

        torch.save(
            model.state_dict(),
            r"D:\oilspill_project\best_oilspill_unet.pth"
        )

        print(
            "🔥 Best model saved!"
        )


print()
print("=========================")
print("TRAINING COMPLETE!")
print("=========================")

print(
    "Model saved at:",
    r"D:\oilspill_project\best_oilspill_unet.pth"
)