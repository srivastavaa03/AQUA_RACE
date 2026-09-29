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
