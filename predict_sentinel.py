import os
import sys
import glob
import numpy as np
import rasterio
import torch
import segmentation_models_pytorch as smp


from pathlib import Path
MODEL_PATH = str(Path(__file__).resolve().parent / "best_oilspill_unet.pth")

TILE_SIZE = 512
OVERLAP = 64
THRESHOLD = 0.5


def predict(safe_dir, output_mask):

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 60)
    print("       SENTINEL-1 OIL SPILL DETECTION")
    print("=" * 60)
    print("Device:", device)

    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    # ========================================================
    # FIND VV / VH
    # ========================================================

    vv_files = glob.glob(
        os.path.join(
            safe_dir,
            "measurement",
            "*-vv-*.tiff"
        )
    )

    vh_files = glob.glob(
        os.path.join(
            safe_dir,
            "measurement",
            "*-vh-*.tiff"
        )
    )

    if not vv_files:
        raise FileNotFoundError(
            "VV TIFF not found in SAFE product"
        )

    if not vh_files:
        raise FileNotFoundError(
            "VH TIFF not found in SAFE product"
        )

    vv_path = vv_files[0]
    vh_path = vh_files[0]

    print("\nVV:", vv_path)
    print("VH:", vh_path)

    # ========================================================
    # LOAD MODEL
    # ========================================================

    print("\nLoading U-Net model...")

    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device
    )

    if (
        isinstance(checkpoint, dict)
        and "state_dict" in checkpoint
    ):
        model.load_state_dict(
            checkpoint["state_dict"]
        )
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()

    print("Model loaded successfully.")

    # ========================================================
    # OPEN SAR
    # ========================================================

    vv_src = rasterio.open(vv_path)
    vh_src = rasterio.open(vh_path)

    try:

        if (
            vv_src.width != vh_src.width
            or vv_src.height != vh_src.height
        ):
            raise ValueError(
                "VV and VH dimensions do not match"
            )

        width = vv_src.width
        height = vv_src.height

        print("\nSAR image:")
        print("Width :", width)
        print("Height:", height)

        # ====================================================
        # OUTPUT MASK
        # ====================================================

        full_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        prediction_count = np.zeros(
            (height, width),
            dtype=np.uint16
        )

        # ====================================================
        # TILE POSITIONS
        # ====================================================

        step = TILE_SIZE - OVERLAP

        rows = list(
            range(0, height, step)
        )

        cols = list(
            range(0, width, step)
        )

        total_tiles = (
            len(rows) * len(cols)
        )

        print("\nTile size :", TILE_SIZE)
        print("Overlap   :", OVERLAP)
        print("Total tiles:", total_tiles)

        # ====================================================
        # PREDICTION
        # ====================================================

        tile_number = 0

        with torch.no_grad():

            for row in rows:

                for col in cols:

                    tile_number += 1

                    row_end = min(
                        row + TILE_SIZE,
                        height
                    )

                    col_end = min(
                        col + TILE_SIZE,
                        width
                    )

                    actual_h = row_end - row
                    actual_w = col_end - col

                    # ----------------------------------------
                    # READ VV + VH
                    # ----------------------------------------

                    vv = vv_src.read(
                        1,
                        window=(
                            (row, row_end),
                            (col, col_end)
                        )
                    ).astype(np.float32)

                    vh = vh_src.read(
                        1,
                        window=(
                            (row, row_end),
                            (col, col_end)
                        )
                    ).astype(np.float32)

                    # ----------------------------------------
                    # THIRD CHANNEL
                    # ----------------------------------------

                    third = np.mean(
                        np.stack(
                            [vv, vh],
                            axis=2
                        ),
                        axis=2
                    )

                    image = np.stack(
                        [vv, vh, third],
                        axis=2
                    )

                    # ----------------------------------------
                    # PAD EDGE TILES
                    # ----------------------------------------

                    if (
                        actual_h != TILE_SIZE
                        or actual_w != TILE_SIZE
                    ):

                        padded = np.zeros(
                            (
                                TILE_SIZE,
                                TILE_SIZE,
                                3
                            ),
                            dtype=np.float32
                        )

                        padded[
                            :actual_h,
                            :actual_w
                        ] = image

                        image = padded

                    # ----------------------------------------
                    # NORMALIZATION
                    # ----------------------------------------

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
                            (
                                channel - low
                            ) /
                            (
                                high - low
                                + 1e-8
                            ),
                            0,
                            1
                        )

                    # ----------------------------------------
                    # HWC -> CHW
                    # ----------------------------------------

                    tensor = torch.from_numpy(
                        image.transpose(2, 0, 1)
                    ).float()

                    tensor = (
                        tensor
                        .unsqueeze(0)
                        .to(device)
                    )

                    # ----------------------------------------
                    # MODEL
                    # ----------------------------------------

                    output = model(tensor)

                    probability = torch.sigmoid(
                        output
                    )

                    prediction = (
                        probability[0, 0]
                        .cpu()
                        .numpy()
                    )

                    mask = (
                        prediction >= THRESHOLD
                    ).astype(np.uint8)

                    # ----------------------------------------
                    # REMOVE PADDING
                    # ----------------------------------------

                    mask = mask[
                        :actual_h,
                        :actual_w
                    ]

                    # ----------------------------------------
                    # STITCH
                    # ----------------------------------------

                    full_mask[
                        row:row_end,
                        col:col_end
                    ] += mask

                    prediction_count[
                        row:row_end,
                        col:col_end
                    ] += 1

                    print(
                        f"\rProcessing tile "
                        f"{tile_number}/{total_tiles}",
                        end=""
                    )

        print(
            "\n\nStitching overlapping predictions..."
        )

        # ====================================================
        # FINAL MASK
        # ====================================================

        final_probability = (
            full_mask /
            np.maximum(
                prediction_count,
                1
            )
        )

        final_mask = (
            final_probability >= 0.5
        ).astype(np.uint8)

        # ====================================================
        # SAVE
        # ====================================================

        os.makedirs(
            os.path.dirname(
                output_mask
            ),
            exist_ok=True
        )

        profile = vv_src.profile.copy()

        profile.update(
            driver="GTiff",
            dtype="uint8",
            count=1,
            compress="lzw",
            nodata=0
        )

        with rasterio.open(
            output_mask,
            "w",
            **profile
        ) as dst:

            dst.write(
                final_mask,
                1
            )

        # ====================================================
        # RESULTS
        # ====================================================

        oil_pixels = int(
            np.sum(final_mask)
        )

        total_pixels = final_mask.size

        coverage = (
            oil_pixels /
            total_pixels *
            100
        )

        print("\n" + "=" * 60)
        print("              PREDICTION COMPLETE")
        print("=" * 60)

        print("Oil pixels :", oil_pixels)
        print("Total pixels:", total_pixels)
        print(
            f"Coverage   : {coverage:.2f}%"
        )

        if oil_pixels > 0:
            print(
                "Oil spill detected: YES"
            )
        else:
            print(
                "Oil spill detected: NO"
            )

        print("\nSaved:")
        print(output_mask)

        print("=" * 60)

        return {
            "oil_pixels": oil_pixels,
            "total_pixels": total_pixels,
            "coverage_percent": coverage,
            "detected": oil_pixels > 0,
            "output_mask": output_mask
        }

    finally:

        vv_src.close()
        vh_src.close()


def main():

    if len(sys.argv) != 3:

        print(
            "Usage:"
        )

        print(
            "python predict_sentinel.py "
            "<SAFE_DIR> <OUTPUT_MASK>"
        )

        sys.exit(1)

    safe_dir = sys.argv[1]
    output_mask = sys.argv[2]

    if not os.path.isdir(safe_dir):

        raise FileNotFoundError(
            f"SAFE directory not found: {safe_dir}"
        )

    predict(
        safe_dir,
        output_mask
    )


if __name__ == "__main__":
    main()
