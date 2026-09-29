from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import subprocess
import sys
import uuid
import json


app = FastAPI(
    title="SIH26143 Oil Spill Investigation API",
    description="API wrapper for the SAR oil-spill investigation pipeline",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_DIR = Path(__file__).resolve().parent
PIPELINE_FILE = PROJECT_DIR / "run_pipeline.py"
PREDICTIONS_DIR = PROJECT_DIR / "predictions"
HISTORY_FILE = PROJECT_DIR / "investigation_history.json"

investigations = {}

def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(investigations.values()), f, indent=2)
    except Exception:
        pass

def load_history():
    global investigations
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            investigations = {
                item["id"]: item
                for item in saved
                if "id" in item
            }
        except Exception:
            investigations = {}

load_history()


class InvestigationRequest(BaseModel):
    latitude: float
    longitude: float
    date: str


def run_pipeline(investigation_id: str, latitude: float, longitude: float, date: str):
    investigations[investigation_id]["status"] = "running"

    try:
        command = [
            sys.executable,
            str(PIPELINE_FILE),
            "--lat", str(latitude),
            "--lon", str(longitude),
            "--date", date
        ]

        result = subprocess.run(
            command,
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True
        )

        investigations[investigation_id]["stdout"] = result.stdout
        investigations[investigation_id]["stderr"] = result.stderr

        if result.returncode == 0:
            summary_file = PREDICTIONS_DIR / "pipeline_summary.json"

            if summary_file.exists():
                with open(summary_file, "r", encoding="utf-8") as f:
                    result_data = json.load(f)

                characterization_file = PREDICTIONS_DIR / "spill_characterization.json"
                if characterization_file.exists():
                    with open(characterization_file, "r", encoding="utf-8") as f:
                        result_data["spill_characterization"] = json.load(f)

                drift_file = PREDICTIONS_DIR / "drift_hindcast.json"
                if drift_file.exists():
                    with open(drift_file, "r", encoding="utf-8") as f:
                        result_data["drift_data"] = json.load(f)

                origin_file = PREDICTIONS_DIR / "origin_zone.json"
                if origin_file.exists():
                    with open(origin_file, "r", encoding="utf-8") as f:
                        result_data["origin_data"] = json.load(f)

                corridor_file = PREDICTIONS_DIR / "origin_corridor.geojson"
                if corridor_file.exists():
                    with open(corridor_file, "r", encoding="utf-8") as f:
                        result_data["origin_corridor"] = json.load(f)

                ais_file = PREDICTIONS_DIR / "ais_ranked_candidates.json"
                if ais_file.exists():
                    with open(ais_file, "r", encoding="utf-8") as f:
                        result_data["ais_data"] = json.load(f)

                investigations[investigation_id]["result"] = result_data

            investigations[investigation_id]["status"] = "completed"

        else:
            output = (
                result.stdout.strip()
                or result.stderr.strip()
                or "Investigation pipeline failed."
            )

            error_type = "pipeline_error"

            if "No Sentinel-1 SAR imagery is available" in output:
                error_type = "no_sentinel_coverage"

            elif "No Sentinel-1 GRD SAR scene was found" in output:
                error_type = "no_sentinel_scene"

            elif "temporarily unavailable" in output:
                error_type = "sentinel_catalogue_unavailable"

            investigations[investigation_id]["status"] = "failed"
            investigations[investigation_id]["error_type"] = error_type
            investigations[investigation_id]["error"] = output

        save_history()

    except Exception as e:
        investigations[investigation_id]["status"] = "failed"
        investigations[investigation_id]["error"] = str(e)
        save_history()

@app.get("/")
def root():
    return {
        "name": "SIH26143 Oil Spill Investigation API",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/investigate")
def investigate(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks
):
    investigation_id = str(uuid.uuid4())

    investigations[investigation_id] = {
        "id": investigation_id,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "date": request.date,
        "status": "queued"
    }

    save_history()

    background_tasks.add_task(
        run_pipeline,
        investigation_id,
        request.latitude,
        request.longitude,
        request.date
    )

    return {
        "investigation_id": investigation_id,
        "status": "queued",
        "message": "Investigation started"
    }


@app.post("/api/investigation/{investigation_id}/retry")
def retry_investigation(
    investigation_id: str,
    background_tasks: BackgroundTasks
):
    if investigation_id not in investigations:
        return {
            "error": "Investigation not found"
        }

    investigation = investigations[investigation_id]

    latitude = investigation["latitude"]
    longitude = investigation["longitude"]
    date = investigation["date"]

    investigation["status"] = "queued"
    investigation.pop("error", None)
    investigation.pop("error_type", None)
    investigation.pop("stdout", None)
    investigation.pop("stderr", None)

    save_history()

    background_tasks.add_task(
        run_pipeline,
        investigation_id,
        latitude,
        longitude,
        date
    )

    return {
        "investigation_id": investigation_id,
        "status": "queued",
        "message": "Investigation retry started"
    }


@app.get("/api/investigations")
def get_investigations():
    return {
        "investigations": list(investigations.values())
    }


@app.get("/api/investigation/{investigation_id}")
def get_investigation(investigation_id: str):
    if investigation_id not in investigations:
        return {
            "error": "Investigation not found"
        }

    investigation = investigations[investigation_id]
    result = investigation.get("result")

    if isinstance(result, dict):
        characterization_file = PREDICTIONS_DIR / "spill_characterization.json"

        if characterization_file.exists():
            try:
                with open(characterization_file, "r", encoding="utf-8") as f:
                    result["spill_characterization"] = json.load(f)
            except Exception:
                pass

    return investigation

@app.get("/api/investigation/{investigation_id}/mask")
def get_investigation_mask(investigation_id: str):
    if investigation_id not in investigations:
        return {"error": "Investigation not found"}

    mask_path = PREDICTIONS_DIR / "sentinel_mask.tif"

    if not mask_path.exists():
        return {"error": "Mask file not found"}

    return FileResponse(
        path=mask_path,
        media_type="image/tiff",
        filename="sentinel_mask.tif"
    )

@app.get("/api/investigation/{investigation_id}/status")
def get_status(investigation_id: str):
    if investigation_id not in investigations:
        return {
            "error": "Investigation not found"
        }

    investigation = investigations[investigation_id]

    return {
        "investigation_id": investigation_id,
        "status": investigation["status"]
    }





@app.get("/api/investigation/{investigation_id}/mask-preview")
def get_investigation_mask_preview(investigation_id: str):
    if investigation_id not in investigations:
        return {"error": "Investigation not found"}

    mask_path = PREDICTIONS_DIR / "sentinel_mask.tif"
    preview_path = PREDICTIONS_DIR / "sentinel_mask_preview.png"

    if not mask_path.exists():
        return {"error": "Mask file not found"}

    if not preview_path.exists():
        import rasterio
        import numpy as np
        from PIL import Image

        with rasterio.open(mask_path) as src:
            mask = src.read(1, out_shape=(1, 1024, 1024))

        mask = (mask > 0).astype(np.uint8) * 255
        Image.fromarray(mask, mode="L").save(preview_path, format="PNG")

    return FileResponse(
        path=preview_path,
        media_type="image/png",
        filename="sentinel_mask_preview.png"
    )
