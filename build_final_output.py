import json
from pathlib import Path

BASE = Path(r"D:\oilspill_project\predictions")


def load_json(filename):
    path = BASE / filename
    if not path.exists():
        print(f"WARNING: Missing {filename}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


prediction = load_json("prediction.json")
characterization = load_json("spill_characterization.json")
sentinel = load_json("sentinel_metadata.json")
drift = load_json("drift_result.json")
ais = load_json("ais_candidate_vessels.json")


# -----------------------------
# Spill information
# -----------------------------

centroid = characterization.get("centroid", {})
bounds = characterization.get("bounds", {})

spill = {
    "detected": characterization.get(
        "spill_detected",
        prediction.get("spill_detected", False)
    ),
    "area_km2": characterization.get("total_area_km2"),
    "oil_pixels": characterization.get("total_oil_pixels"),
    "centroid": {
        "latitude": centroid.get("latitude"),
        "longitude": centroid.get("longitude")
    },
    "bounds": bounds,
    "component_count": characterization.get("component_count"),
    "largest_component": characterization.get("largest_component"),
    "border_contact": characterization.get("border_contact")
}


# -----------------------------
# Sentinel information
# -----------------------------

satellite = {
    "satellite": sentinel.get("satellite"),
    "sensor": sentinel.get("sensor"),
    "mode": sentinel.get("mode"),
    "product_type": sentinel.get("product_type"),
    "polarization": sentinel.get("polarization"),
    "acquisition_start": sentinel.get("acquisition_start"),
    "acquisition_end": sentinel.get("acquisition_end"),
    "orbit": sentinel.get("orbit"),
    "product_name": sentinel.get("product_name")
}


# -----------------------------
# Drift information
# -----------------------------

drift_output = {
    "current_speed_mps": drift.get("current_speed_mps"),
    "current_direction_deg": drift.get("current_direction_deg"),
    "current_source": drift.get("current_source"),
    "backward_track": drift.get("backward_track", []),
    "forward_track": drift.get("forward_track", [])
}


# -----------------------------
# AIS information
# -----------------------------

ais_output = {
    "candidate_count": ais.get("candidate_count", 0),
    "candidates": ais.get("candidates", []),
    "data_source": ais.get("ais_file"),
    "status": "demo_only"
}


# -----------------------------
# Final response
# -----------------------------

final_output = {
    "project": "SIH26143",
    "pipeline": "SAR Oil-Spill Detection and Investigation",

    "status": "oil_spill_detected"
        if spill["detected"]
        else "no_oil_spill_detected",

    "spill": spill,

    "satellite_observation": satellite,

    "environment": {
        "ocean_current": drift_output
    },

    "drift_analysis": {
        "backward_hours": 96,
        "forward_hours": 24,
        "backward_track": drift_output["backward_track"],
        "forward_track": drift_output["forward_track"]
    },

    "ais_correlation": ais_output,

    "limitations": [
        "Current drift model uses a constant local ocean current approximation.",
        "AIS candidate data is currently demonstration data and must not be treated as real vessel attribution.",
        "Historical AIS correlation should be rerun when legitimate AIS data for the scene becomes available."
    ]
}


# Save
output_path = BASE / "final_ai_output.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=4)

print("=" * 60)
print("FINAL AI OUTPUT")
print("=" * 60)

print(f"Spill detected : {spill['detected']}")
print(
    f"Centroid       : "
    f"{centroid.get('latitude')}, {centroid.get('longitude')}"
)
print(f"Area           : {spill['area_km2']} km²")
print(f"Acquisition    : {satellite['acquisition_start']}")
print(
    f"AIS candidates : "
    f"{ais_output['candidate_count']}"
)

print()
print(f"Saved: {output_path}")