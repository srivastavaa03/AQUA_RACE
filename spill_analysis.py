
import json
import cv2
import numpy as np


# =========================
# FILE PATHS
# =========================

JSON_PATH = r"D:\oilspill_project\predictions\prediction.json"

MASK_PATH = r"D:\oilspill_project\predictions\predicted_mask.png"


# =========================
# LOAD JSON
# =========================

with open(JSON_PATH, "r") as f:
    data = json.load(f)


# =========================
# LOAD MASK
# =========================

mask = cv2.imread(
    MASK_PATH,
    cv2.IMREAD_GRAYSCALE
)

if mask is None:
    print("ERROR: Mask not found.")
    exit()


binary = (
    mask > 0
).astype(np.uint8)


# =========================
# FIND CONTOURS
# =========================

contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)


# =========================
# CHARACTERIZATION
# =========================

total_area = 0
total_perimeter = 0

largest_area = 0
largest_perimeter = 0

for contour in contours:

    area = cv2.contourArea(contour)

    perimeter = cv2.arcLength(
        contour,
        True
    )

    total_area += area
    total_perimeter += perimeter

    if area > largest_area:

        largest_area = area
        largest_perimeter = perimeter


# =========================
# COMPACTNESS
# =========================

if largest_perimeter > 0:

    compactness = (
        4 * np.pi * largest_area
    ) / (
        largest_perimeter ** 2
    )

else:

    compactness = 0


# =========================
# READ GEOLOCATION
# =========================

geo = data.get(
    "geolocation"
)

if geo:

    latitude = geo["center"]["latitude"]
    longitude = geo["center"]["longitude"]

else:

    latitude = None
    longitude = None


# =========================
# RESULTS
# =========================

analysis = {

    "oil_spill_detected":
        data["oil_spill_detected"],

    "oil_pixels":
        data["oil_pixels"],

    "coverage_percent":
        data["coverage_percent"],

    "spill_regions":
        len(contours),

    "total_contour_area_pixels":
        int(total_area),

    "total_perimeter_pixels":
        round(
            float(total_perimeter),
            2
        ),

    "largest_spill_area_pixels":
        int(largest_area),

    "largest_spill_perimeter_pixels":
        round(
            float(largest_perimeter),
            2
        ),

    "compactness":
        round(
            float(compactness),
            4
        ),

    "center":

        {
            "latitude": latitude,
            "longitude": longitude
        }
}


# =========================
# SAVE ANALYSIS
# =========================

output_path = (
    r"D:\oilspill_project"
    r"\predictions"
    r"\spill_analysis.json"
)


with open(
    output_path,
    "w"
) as f:

    json.dump(
        analysis,
        f,
        indent=4
    )


# =========================
# PRINT
# =========================

print()
print("==============================")
print("SPILL CHARACTERIZATION")
print("==============================")

print(
    "Oil detected:",
    analysis["oil_spill_detected"]
)

print(
    "Oil pixels:",
    analysis["oil_pixels"]
)

print(
    "Coverage:",
    analysis["coverage_percent"],
    "%"
)

print(
    "Spill regions:",
    analysis["spill_regions"]
)

print(
    "Largest spill area:",
    analysis["largest_spill_area_pixels"],
    "pixels"
)

print(
    "Total perimeter:",
    analysis["total_perimeter_pixels"],
    "pixels"
)

print(
    "Compactness:",
    analysis["compactness"]
)

print()

print(
    "Location:",
    latitude,
    longitude
)

print()

print(
    "Saved:",
    output_path
)

print("==============================")

