import requests
from pathlib import Path

BASE = Path(r"D:\oilspill_project")
OUTPUT = BASE / "predictions" / "ais_real_20200806_10.csv"

URL = "https://data.pmel.noaa.gov/pmel/erddap/tabledap/AIS2020_AIS.csv"

query = (
    "MMSI,time,Lat,Lon,SOG,COG,Heading,"
    "VesselName,IMO,VesselType"
    "&time>=2020-08-06T14:50:24Z"
    "&time<=2020-08-10T14:50:24Z"
    "&Lat>=28.8883"
    "&Lat<=29.0680"
    "&Lon>=48.5280"
    "&Lon<=48.7332"
)

print("=" * 70)
print("REAL HISTORICAL AIS DOWNLOAD")
print("=" * 70)

print()
print("Source : NOAA PMEL AIS2020")
print("Time   : 2020-08-06 14:50 → 2020-08-10 14:50 UTC")
print("Region : 28.8883–29.0680 N")
print("         48.5280–48.7332 E")

try:
    response = requests.get(
        URL + "?" + query,
        timeout=180
    )

    print()
    print("HTTP status:", response.status_code)

    response.raise_for_status()

except Exception as e:

    print()
    print("ERROR:")
    print(e)
    raise SystemExit


text = response.text

if not text.strip():

    print()
    print("NO AIS RECORDS RETURNED.")
    raise SystemExit


if text.lstrip().startswith("<"):

    print()
    print("SERVER ERROR:")
    print(text[:2000])
    raise SystemExit


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT.write_text(
    text,
    encoding="utf-8"
)

lines = text.strip().splitlines()

print()
print("=" * 70)
print("DOWNLOAD COMPLETE")
print("=" * 70)

print()
print("AIS records:", max(0, len(lines) - 1))
print("Saved:", OUTPUT)

print()
print("First records:")
print("\n".join(lines[:6]))