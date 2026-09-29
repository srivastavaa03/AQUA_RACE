import csv
import io
import zipfile
from pathlib import Path

ZIP_FILE = Path(
    r"D:\oilspill_project\predictions\AIS_2020_08_10.zip"
)

OUTPUT = Path(
    r"D:\oilspill_project\predictions\ais_real_20200810_region.csv"
)

# Our 96-hour origin search region
MIN_LAT = 28.8883
MAX_LAT = 29.0680

MIN_LON = 48.5280
MAX_LON = 48.7332

print("=" * 70)
print("AIS REGIONAL EXTRACTION")
print("=" * 70)

print()
print(f"Latitude : {MIN_LAT} → {MAX_LAT}")
print(f"Longitude: {MIN_LON} → {MAX_LON}")

matched = 0
total = 0

with zipfile.ZipFile(ZIP_FILE, "r") as z:

    name = z.namelist()[0]

    print()
    print("Reading:", name)

    with z.open(name) as raw:

        text = io.TextIOWrapper(
            raw,
            encoding="utf-8",
            errors="replace",
            newline=""
        )

        reader = csv.DictReader(text)

        print()
        print("Columns:")
        print(reader.fieldnames)

        OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            OUTPUT,
            "w",
            newline="",
            encoding="utf-8"
        ) as out:

            writer = None

            for row in reader:

                total += 1

                try:
                    lat = float(
                        row.get("LAT", row.get("lat"))
                    )

                    lon = float(
                        row.get("LON", row.get("lon"))
                    )

                except (TypeError, ValueError):
                    continue

                if (
                    MIN_LAT <= lat <= MAX_LAT
                    and
                    MIN_LON <= lon <= MAX_LON
                ):

                    if writer is None:
                        writer = csv.DictWriter(
                            out,
                            fieldnames=reader.fieldnames
                        )
                        writer.writeheader()

                    writer.writerow(row)

                    matched += 1

                    if matched % 1000 == 0:
                        print(
                            f"Matched records: {matched}"
                        )


print()
print("=" * 70)
print("EXTRACTION COMPLETE")
print("=" * 70)

print()
print("Total AIS records scanned:", total)
print("Records in region         :", matched)

print()
print("Saved:")
print(OUTPUT)