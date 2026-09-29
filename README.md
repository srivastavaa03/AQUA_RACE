# AQUA_RACE

Oil spill detection and investigation platform: SAR-based spill segmentation, geolocation, AIS vessel correlation, drift hindcast, and a React investigation dashboard.

## Structure

- `app.py`: FastAPI backend
- `run_pipeline.py`: runs the processing scripts in sequence
- `oilspill-frontend (2)/oilspill-frontend/`: React + Vite dashboard
- `.env.example`: credentials template

## Setup

1. Copy `.env.example` to `.env` and fill in your own credentials.
2. Install the Python dependencies and start the backend:

   uvicorn app:app --reload

3. Start the frontend:

   cd "oilspill-frontend (2)/oilspill-frontend"
   npm install
   npm run dev

## Not included in this repo

- The trained model file (`*.pth`, about 98 MB)
- Downloaded Sentinel and AIS data and generated predictions
- Your `.env` credentials

Place the model file in the location the prediction script expects before running detection.

## Install order (GPU)

Install PyTorch first, then the rest of the requirements:

    pip install torch --index-url https://download.pytorch.org/whl/cu128
    pip install -r requirements.txt

Development was done with torch 2.11.0+cu128. For a CPU-only machine, run `pip install torch` instead.

## Trained model

The trained segmentation model (`best_oilspill_unet.pth`, about 93 MB) is not stored in the repository. Download it from the release page:

https://github.com/srivastavaa03/AQUA_RACE/releases/tag/v1.0-model

Place the file in the project root, next to `predict_sentinel.py`:

    AQUA_RACE/
      best_oilspill_unet.pth
      predict_sentinel.py
      run_pipeline.py
