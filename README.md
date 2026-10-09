# AQUA_RACE
### AI-Powered Oil Spill Detection and Maritime Investigation

AQUA_RACE is an end-to-end prototype for detecting potential oil spills in Sentinel-1 Synthetic Aperture Radar (SAR) imagery, characterizing detected regions, estimating spill drift and possible origin zones, and correlating results with vessel AIS data.

## Features

- **SAR oil spill detection:** U-Net-based deep learning segmentation.
- **Geospatial characterization:** Estimates spill area, centroid, bounds, and polygon geometry.
- **Drift analysis:** Uses ocean currents and wind data for spill trajectory hindcasting.
- **Origin-zone estimation:** Estimates a possible upstream source region.
- **AIS correlation:** Screens vessel activity near the estimated spill trajectory when data access is configured.
- **Investigation dashboard:** React-based interface with an interactive map and investigation results.
- **FastAPI backend:** Runs the investigation pipeline and exposes its status and results.

> AIS proximity is an investigative lead, not proof that a vessel caused a spill. Detection and trajectory results require validation.

## Technology Stack

- **Frontend:** React, Vite, Leaflet, Tailwind CSS, Recharts
- **Backend:** Python, FastAPI
- **AI/ML:** PyTorch, U-Net, segmentation-models-pytorch
- **Geospatial and scientific computing:** Rasterio, NumPy, SciPy, Xarray, PyProj, Shapely
- **Environmental data:** Copernicus Marine and ERA5/Copernicus Climate Data Store
- **Vessel screening:** Global Fishing Watch API, when configured

## Project Structure

```text
AQUA_RACE/
├── app.py
├── run_pipeline.py
├── sentinel_search.py
├── sentinel_download.py
├── predict_sentinel.py
├── extract_sentinel_metadata.py
├── characterize_candidate.py
├── geolocate_mask.py
├── download_currents.py
├── download_wind.py
├── drift_hindcast_wind.py
├── create_origin_zone.py
├── ais_correlator.py
├── train.py
├── requirements.txt
├── .env.example
└── oilspill-frontend (2)/
```

## Prerequisites

- Python 3.12 recommended
- Node.js and npm
- Git
- A compatible, georeferenced Sentinel-1 SAR GeoTIFF for investigation
- A trained model checkpoint
- Credentials for the external environmental-data services you intend to use

A CUDA-compatible GPU is recommended for faster model inference, but GPU availability depends on your PyTorch installation.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/srivastavaa03/AQUA_RACE.git
cd AQUA_RACE
```

### 2. Create a Python environment

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install the required PyTorch build for your hardware first, following the official [PyTorch installation guide](https://pytorch.org/get-started/locally/).

Then install the project dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter the credentials needed for your selected data services. Leave optional credentials blank if you are not using those integrations.

**Never commit `.env` or API tokens to GitHub.**

### 4. Configure the trained model

Download the model checkpoint from the project's [GitHub Releases](https://github.com/srivastavaa03/AQUA_RACE/releases/tag/v1.0-model), if that release contains the required checkpoint.

Place it at the path expected by the prediction code, or update the model path in the configuration/code to match your chosen location.

### 5. Start the backend

From the project root, activate the environment and run:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Backend API: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open a second PowerShell terminal:

```powershell
cd "D:\oilspill_project\oilspill-frontend (2)\oilspill-frontend"
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

For a fresh clone in a different directory, replace the example local path with your actual frontend directory.

## Investigation Workflow

1. Provide the location and acquisition date required by the investigation interface.
2. Search for and retrieve suitable SAR imagery using the configured data provider.
3. Run the trained model to generate an oil-spill candidate mask.
4. Characterize the detected region and geolocate its geometry.
5. Retrieve available wind and current data to estimate drift and a possible origin zone.
6. Correlate the trajectory with available AIS information.
7. Review the results in the investigation dashboard.

Data availability, credentials, imagery compatibility, and model quality affect which steps can complete successfully.

## Configuration and Data

- Use `.env.example` as the template for configuration.
- Keep API credentials in a local `.env` file.
- Store large datasets, downloaded imagery, generated predictions, and temporary files outside Git where practical.
- Follow the source providers' licensing and usage conditions.
- Use compatible georeferenced imagery and validate model predictions before drawing conclusions.

## Limitations

- The model can produce false positives and false negatives.
- Dark SAR features are not necessarily oil spills.
- Drift estimates depend on environmental data, assumptions, and time coverage.
- AIS coverage and access may be incomplete.
- This prototype supports investigation; it does not independently establish the source or cause of a spill.

## Contributing

Issues and improvements are welcome. Please avoid committing secrets, large raw datasets, generated outputs, or local environment folders.

## License

No license is specified here. Check the repository's licensing before redistributing or reusing this project.
