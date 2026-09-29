import os
import sys
import json
import math
import numpy as np
import torch
import rasterio
import cv2
import segmentation_models_pytorch as smp
from rasterio.features import shapes
from shapely.geometry import shape, mapping


# ============================================================
# SETTINGS
# ============================================================

MODEL_PATH = r"D:\oilspill_project\best_oilspill_unet.pth"
OUTPUT_DIR = r"D:\oilspill_project\predictions"

IMAGE_SIZE = 512

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ============================================================
# INPUT
# ============================================================

if len(sys.argv) < 2:
    print("Usage:")
    print("python predict.py <path_to_sar_image.tif>")
    sys.exit(1)

IMAGE_PATH = sys.argv[1]

if not os.path.exists(IMAGE_PATH):
    print("ERROR: Input file does not exist:")
    print(IMAGE_PATH)
    sys.exit(1)


# ============================================================
# DEVICE
# ============================================================

print()
print("======================================")
print("        OIL SPILL AI DETECTION")
print("======================================")

print("Device:", DEVICE)

if DEVICE == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("Loading U-Net model...")

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights=None,
    in_channels=3,
    classes=1
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(checkpoint)

model = model.to(DEVICE)
model.eval()

print("Model loaded successfully.")


# ============================================================
# READ SAR IMAGE
# ============================================================

print()
print("Reading SAR image:")
print(IMAGE_PATH)

with rasterio.open(IMAGE_PATH) as src:

    image = src.read()

    original_height = src.height
    original_width = src.width

    transform = src.transform
    crs = src.crs

    profile = src.profile.copy()

    bounds = src.bounds

    acquisition_time = (
        src.tags().get("TIFFTAG_DATETIME")
        or src.tags().get("ACQUISITION_DATETIME")
        or None
    )


print()
print("Image size:", original_width, "x", original_height)
print("Bands:", image.shape[0])
print("CRS:", crs)
print("Bounds:", bounds)
print("Transform:", transform)


# ============================================================
# CHW -> HWC
# ============================================================

image = np.transpose(
    image,
    (1, 2, 0)
)


# ============================================================
# HANDLE CHANNELS
# ============================================================

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


# ============================================================
# NORMALIZATION
# SAME APPROACH AS TRAINING
# ============================================================

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


# ============================================================
# RESIZE FOR MODEL
# ============================================================

resized = cv2.resize(
    image,
    (IMAGE_SIZE, IMAGE_SIZE),
    interpolation=cv2.INTER_AREA
)


# HWC -> CHW

resized = np.transpose(
    resized,
    (2, 0, 1)
)


# ============================================================
# TORCH TENSOR
# ============================================================

tensor = torch.tensor(
    resized,
    dtype=torch.float32
)

tensor = tensor.unsqueeze(0)

tensor = tensor.to(DEVICE)


# ============================================================
# AI PREDICTION
# ============================================================

print()
print("Running AI prediction...")

with torch.no_grad():

    output = model(tensor)

    probability = torch.sigmoid(
        output
    )

    prediction = (
        probability > 0.5
    ).float()


# ============================================================
# MASK
# ============================================================

mask_small = prediction[
    0,
    0
].cpu().numpy()


# ============================================================
# RESIZE MASK BACK TO ORIGINAL IMAGE
# ============================================================

mask = cv2.resize(
    mask_small.astype(np.uint8),
    (original_width, original_height),
    interpolation=cv2.INTER_NEAREST
)


# ============================================================
# CLEAN MASK
# ============================================================

mask = (
    mask > 0
).astype(np.uint8)


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# SAVE GEOREFERENCED MASK
# ============================================================

mask_path = os.path.join(
    OUTPUT_DIR,
    "predicted_mask.tif"
)

mask_profile = profile.copy()

mask_profile.update(
    driver="GTiff",
    dtype=rasterio.uint8,
    count=1,
    compress="lzw"
)

with rasterio.open(
    mask_path,
    "w",
    **mask_profile
) as dst:

    dst.write(
        mask,
        1
    )


print()
print("Saved georeferenced mask:")
print(mask_path)


# ============================================================
# BASIC MEASUREMENTS
# ============================================================

oil_pixels = np.where(
    mask > 0
)

oil_pixel_count = len(
    oil_pixels[0]
)

total_pixels = (
    original_width *
    original_height
)

coverage_percent = (
    oil_pixel_count /
    total_pixels
) * 100


# ============================================================
# NO SPILL
# ============================================================

if oil_pixel_count == 0:

    result = {

        "input_file": os.path.basename(
            IMAGE_PATH
        ),

        "oil_spill_detected": False,

        "oil_pixels": 0,

        "coverage_percent": 0.0,

        "area_km2": 0.0,

        "geolocation": None

    }

    json_path = os.path.join(
        OUTPUT_DIR,
        "prediction.json"
    )

    with open(
        json_path,
        "w"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )

    print()
    print("Oil spill detected: NO")
    print("Prediction complete.")

    sys.exit(0)


# ============================================================
# ACTUAL OIL PIXEL CENTROID
# ============================================================

ys, xs = oil_pixels

mean_x = float(
    xs.mean()
)

mean_y = float(
    ys.mean()
)


centroid_lon, centroid_lat = (
    rasterio.transform.xy(
        transform,
        mean_y,
        mean_x
    )
)

centroid_lon = float(
    centroid_lon
)

centroid_lat = float(
    centroid_lat
)


# ============================================================
# PIXEL BOUNDING BOX
# ============================================================

x_min = int(xs.min())
x_max = int(xs.max())

y_min = int(ys.min())
y_max = int(ys.max())


# ============================================================
# GEOGRAPHIC BOUNDS
# ============================================================

west, south, east, north = (
    rasterio.transform.array_bounds(
        original_height,
        original_width,
        transform
    )
)


# ============================================================
# AREA CALCULATION
# ============================================================

pixel_width_deg = abs(
    transform.a
)

pixel_height_deg = abs(
    transform.e
)


# Approximate meters per degree

meters_per_degree_lat = 111320.0

meters_per_degree_lon = (
    111320.0 *
    math.cos(
        math.radians(
            centroid_lat
        )
    )
)


pixel_width_m = (
    pixel_width_deg *
    meters_per_degree_lon
)

pixel_height_m = (
    pixel_height_deg *
    meters_per_degree_lat
)


pixel_area_m2 = (
    pixel_width_m *
    pixel_height_m
)


area_km2 = (
    oil_pixel_count *
    pixel_area_m2
) / 1_000_000


# ============================================================
# SPILL POLYGON
# ============================================================

polygon_features = []

for geom, value in shapes(
    mask,
    mask=mask.astype(bool),
    transform=transform
):

    if value == 1:

        polygon_features.append(
            shape(geom)
        )


spill_polygon = None

if polygon_features:

    combined = polygon_features[0]

    for polygon in polygon_features[1:]:

        combined = combined.union(
            polygon
        )

    spill_polygon = mapping(
        combined
    )


# ============================================================
# SAVE GEOJSON
# ============================================================

geojson_path = os.path.join(
    OUTPUT_DIR,
    "spill_polygon.geojson"
)

if spill_polygon:

    geojson = {

        "type": "FeatureCollection",

        "features": [

            {
                "type": "Feature",

                "properties": {
                    "area_km2": round(
                        area_km2,
                        4
                    )
                },

                "geometry":
                    spill_polygon
            }

        ]
    }

    with open(
        geojson_path,
        "w"
    ) as f:

        json.dump(
            geojson,
            f
        )


# ============================================================
# OVERLAY IMAGE
# ============================================================

display_image = cv2.resize(
    image,
    (original_width, original_height),
    interpolation=cv2.INTER_LINEAR
)

display_image = (
    display_image * 255
).clip(
    0,
    255
).astype(
    np.uint8
)


# Convert RGB → BGR

display_image = cv2.cvtColor(
    display_image,
    cv2.COLOR_RGB2BGR
)


overlay = display_image.copy()

oil_pixels_mask = (
    mask > 0
)

overlay[
    oil_pixels_mask
] = (
    0.5 *
    overlay[
        oil_pixels_mask
    ]
    +
    0.5 *
    np.array(
        [0, 0, 255],
        dtype=np.uint8
    )
).astype(
    np.uint8
)


overlay_path = os.path.join(
    OUTPUT_DIR,
    "oil_spill_overlay.png"
)

cv2.imwrite(
    overlay_path,
    overlay
)


# ============================================================
# RESULT JSON
# ============================================================

result = {

    "input_file":
        os.path.basename(
            IMAGE_PATH
        ),

    "oil_spill_detected":
        True,

    "oil_pixels":
        int(
            oil_pixel_count
        ),

    "coverage_percent":
        round(
            float(
                coverage_percent
            ),
            2
        ),

    "area_km2":
        round(
            float(
                area_km2
            ),
            4
        ),

    "image_dimensions": {

        "width":
            int(
                original_width
            ),

        "height":
            int(
                original_height
            )
    },

    "bounding_box_pixels": {

        "x_min": x_min,

        "y_min": y_min,

        "x_max": x_max,

        "y_max": y_max
    },

    "geolocation": {

        "crs":
            str(crs),

        "centroid": {

            "latitude":
                round(
                    centroid_lat,
                    8
                ),

            "longitude":
                round(
                    centroid_lon,
                    8
                )
        },

        "bounds": {

            "north":
                round(
                    float(north),
                    8
                ),

            "south":
                round(
                    float(south),
                    8
                ),

            "west":
                round(
                    float(west),
                    8
                ),

            "east":
                round(
                    float(east),
                    8
                )
        }
    },

    "acquisition_time":
        acquisition_time
}


json_path = os.path.join(
    OUTPUT_DIR,
    "prediction.json"
)

with open(
    json_path,
    "w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("======================================")
print("       OIL SPILL DETECTION RESULT")
print("======================================")

print(
    "Oil spill detected: YES"
)

print(
    f"Oil pixels: {oil_pixel_count}"
)

print(
    f"Coverage: {coverage_percent:.2f}%"
)

print(
    f"Estimated area: {area_km2:.4f} km²"
)

print()
print("SPILL LOCATION")

print(
    f"Latitude: {centroid_lat:.8f}"
)

print(
    f"Longitude: {centroid_lon:.8f}"
)

print()
print("SPILL BOUNDS")

print(
    f"North: {north:.8f}"
)

print(
    f"South: {south:.8f}"
)

print(
    f"West: {west:.8f}"
)

print(
    f"East: {east:.8f}"
)

print()
print("OUTPUT FILES")

print(
    mask_path
)

print(
    overlay_path
)

print(
    json_path
)

print(
    geojson_path
)

print()
print("======================================")
print("Prediction complete.")
print("======================================")