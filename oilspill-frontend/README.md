# SIH26143 — Oil Spill Origin Investigation Dashboard (Frontend)

Standalone React frontend for the SIH26143 pipeline. Connected to the real
FastAPI backend at `http://127.0.0.1:8000`. Does **not** touch `app.py`,
`run_pipeline.py`, or the U-Net model — this is a separate app meant to
live at `D:\oilspill_project\frontend`.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Open the printed local URL (defaults to `http://localhost:5173`). Make
sure the FastAPI backend is running at `http://127.0.0.1:8000` first
(`/health` should return `healthy`).

## Build for production

```bash
npm run build
npm run preview   # serve the built dist/ locally to sanity-check
```

## How it talks to the backend

All data access goes through `src/api/investigationApi.js` — nothing else
in the component tree calls `fetch` or knows the backend's URL.

- `BASE_URL` is set to `http://127.0.0.1:8000`. Change it there if the
  backend moves.
- Clicking **Analyze Location** posts `{ latitude, longitude, date }` to
  `POST /api/investigate`, then polls `GET /api/investigation/{id}/status`
  every 3 seconds until the backend reports `complete` (or an error),
  then fetches `GET /api/investigation/{id}` for the full result.
- The backend has no "list all investigations" endpoint, so the sidebar's
  list is this browser's own request history (id, coordinates, date,
  status), kept in `localStorage`. It's real data about what you've asked
  for — not a mock backend list.

### If the field names don't line up

The exact JSON shape `GET /api/investigation/{id}` returns wasn't fully
specified, so `normalizeResult()` in `investigationApi.js` defensively
tries several plausible key spellings for each field (snake_case,
camelCase, nested under a stage name, matching the pipeline's own
`sentinel_metadata.json` / `spill_characterization.json` /
`drift_hindcast.json` / `origin_zone.json` / `ais_ranked_candidates.json`
key names seen in your pipeline run). If a field still shows
**"Data unavailable"** in the UI but the backend is actually returning it
under a different key, add that key to the relevant `pick([...], [...])`
call in `normalizeResult()` — nothing else needs to change.

**Nothing is ever invented.** If a field genuinely isn't in the response,
it stays `undefined` and every panel renders an explicit "Data
unavailable" (or a whole-panel "not returned by the backend yet" message)
instead of guessing a value.

## States handled

- **Queued / running** — status tracker shows the current stage, polling
  continues automatically.
- **Complete** — full result renders across the four tabs.
- **Error** — if the backend returns a non-2xx response, can't be reached
  (e.g. CORS not enabled, server not running), or its `/status` endpoint
  reports an error stage, a dedicated error screen replaces the panels
  with a **Retry** button.
- **Partial data** — any field or whole section the backend hasn't filled
  in yet shows "Data unavailable" rather than blank or fabricated values.

## Troubleshooting

- **"Could not reach the backend…"** — confirm `uvicorn`/FastAPI is
  running at `127.0.0.1:8000`, and that it has CORS middleware enabling
  `http://localhost:5173` (the frontend dev server's origin). This
  frontend doesn't touch `app.py`, so that middleware needs to already be
  present there.
- **Fields stuck on "Data unavailable"** — see "If the field names don't
  line up" above.

## Where things live

```
src/
  api/investigationApi.js     ← the only file that talks to the backend
  mockData.js                 ← now just PIPELINE_STAGES (UI labels), no fake data
  components/
    layout/                   ← Header, Sidebar (session investigation history)
    investigation/            ← Location/date form ("Analyze Location"), status tracker
    panels/                   ← One panel per pipeline stage's output, each with its
                                 own "Data unavailable" fallback
    map/                      ← Leaflet investigation map (only plots layers it has
                                 real coordinates for)
    timeline/                 ← Evidence/audit timeline, built only from fields present
  pages/Dashboard.jsx          ← Owns app state: selection, polling, loading, error
```

## Notes

- Default location/date in the form are the values from your last known
  pipeline run (28.5875, 48.5678, 2020-08-10) — just a convenient
  starting point, not a restriction. Any latitude, longitude and date can
  be entered.
- No real vessel/AIS data is fabricated anywhere — AIS candidates without
  a backend-provided position are listed in the AIS tab but not plotted
  on the map (no invented coordinates).
- Tailwind tokens (palette, fonts) live in `tailwind.config.js` under a
  maritime command-console theme (`hull`, `deck`, `sonar`, `flare`,
  `hazard`, `mist`).
