import json
from pathlib import Path

BASE = Path(r"D:\oilspill_project")
PRED = BASE / "predictions"

spill_file = PRED / "spill_characterization_real.json"
meta_file = PRED / "sentinel_metadata_real.json"

spill = {
    "spill_detected": True,
    "source": "real Sentinel-1 U-Net candidate detection",
    "detected_pixels": 39165,
    "estimated_area_km2": 3.976,
    "centroid": {
        "latitude": 28.648235,
        "longitude": 48.747471
    },
    "bounds": {
        "north": 28.666246,
        "south": 28.624774,
        "east": 48.755047,
        "west": 48.731720
    },
    "bounding_box_area_km2": 10.52,
    "notes": [
        "Candidate is the largest connected U-Net detection.",
        "Area is approximate because Sentinel-1 GRD geolocation/pixel spacing is not perfectly uniform.",
        "Detection is an AI candidate and is not independently confirmed as oil."
    ]
}

metadata = {
    "satellite": "Sentinel-1A",
    "product": "S1A_IW_GRDH_1SDV",
    "acquisition_start": "2020-08-10T14:50:24.997Z",
    "acquisition_end": "2020-08-10T14:50:49.997Z",
    "source": "Copernicus Data Space Ecosystem",
    "product_name": "S1A_IW_GRDH_1SDV_20200810T145024_20200810T145049_033846_03ECAE_2460_COG.SAFE"
}

with open(spill_file, "w", encoding="utf-8") as f:
    json.dump(spill, f, indent=4)

with open(meta_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("Created:")
print(spill_file)
print(meta_file)