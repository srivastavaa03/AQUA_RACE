import json
import csv

INPUT = r"D:\oilspill_project\predictions\gfw_ais_20200806_10.json"
OUTPUT = r"D:\oilspill_project\predictions\ais_gfw_20200806_10.csv"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

records = []

for entry in data.get("entries", []):
    for value in entry.values():
        if isinstance(value, list):
            records.extend(value)

fields = [
    "shipName",
    "imo",
    "mmsi",
    "vesselType",
    "geartype",
    "flag",
    "lat",
    "lon",
    "date",
    "entryTimestamp",
    "exitTimestamp",
    "hours",
    "callsign",
    "vesselId"
]

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for r in records:
        writer.writerow({field: r.get(field, "") for field in fields})

print("Converted GFW records:", len(records))
print("Saved:", OUTPUT)
