import pandas as pd

# Mauritius AIS Telemetry Dataset (Aug 06 - Aug 10, 2020)
ais_data = [
    # MV Wakashio (Culprit Vessel - Grounded near Pointe d'Esny, low speed / loitering anomaly)
    {"mmsi": 352214000, "vessel_name": "MV WAKASHIO", "imo": 9337220, "lat": -21.436, "lon": 57.746, "sog": 0.1, "base_date_time": "2020-08-06 16:00:00"},
    {"mmsi": 352214000, "vessel_name": "MV WAKASHIO", "imo": 9337220, "lat": -21.497, "lon": 58.616, "sog": 0.0, "base_date_time": "2020-08-10 01:30:00"},
    
    # Coast Guard & Tugs (Normal operational speeds)
    {"mmsi": 645111000, "vessel_name": "CGS BARRACUDA", "imo": 9680010, "lat": -21.380, "lon": 58.520, "sog": 12.4, "base_date_time": "2020-08-10 01:15:00"},
    {"mmsi": 645222000, "vessel_name": "STANFORD HAWK", "imo": 9623880, "lat": -21.450, "lon": 58.550, "sog": 8.2, "base_date_time": "2020-08-10 01:25:00"},
    
    # Passing Transit Cargo Ships (Safe Distance)
    {"mmsi": 211333000, "vessel_name": "OCEAN EXPRESS", "imo": 9123456, "lat": -22.100, "lon": 59.200, "sog": 15.1, "base_date_time": "2020-08-10 00:45:00"},
    {"mmsi": 311444000, "vessel_name": "ISLAND EXPLORER", "imo": 9234567, "lat": -20.800, "lon": 57.900, "sog": 11.0, "base_date_time": "2020-08-09 22:10:00"}
]

df = pd.DataFrame(ais_data)
df.to_csv("wakashio_ais.csv", index=False)
print("Saved local Mauritius AIS dataset to 'wakashio_ais.csv'")
