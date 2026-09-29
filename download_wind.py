import sys
import os
from datetime import datetime, timedelta
import cdsapi


DATASET = "reanalysis-era5-single-levels"


def build_dates(start_date, end_date):

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end < start:
        raise ValueError("End date cannot be before start date.")

    dates = []

    current = start

    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    return dates


def download_wind(
    latitude,
    longitude,
    start_date,
    end_date,
    target
):

    latitude = float(latitude)
    longitude = float(longitude)

    dates = build_dates(
        start_date,
        end_date
    )

    # Small area around target location.
    # ERA5 area format:
    # North, West, South, East

    north = min(90.0, latitude + 1.0)
    south = max(-90.0, latitude - 1.0)
    west = max(-180.0, longitude - 1.0)
    east = min(180.0, longitude + 1.0)

    years = sorted(
        {d.strftime("%Y") for d in dates}
    )

    months = sorted(
        {d.strftime("%m") for d in dates}
    )

    days = sorted(
        {d.strftime("%d") for d in dates}
    )

    times = [
        f"{hour:02d}:00"
        for hour in range(24)
    ]

    request = {
        "product_type": ["reanalysis"],

        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
        ],

        "year": years,

        "month": months,

        "day": days,

        "time": times,

        "area": [
            north,
            west,
            south,
            east,
        ],

        "data_format": "netcdf",

        "download_format": "unarchived",
    }

    os.makedirs(
        os.path.dirname(
            os.path.abspath(target)
        ),
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("          ERA5 WIND DOWNLOAD")
    print("=" * 60)

    print(f"Latitude : {latitude}")
    print(f"Longitude: {longitude}")

    print(
        f"Area     : "
        f"{north:.3f}, "
        f"{west:.3f}, "
        f"{south:.3f}, "
        f"{east:.3f}"
    )

    print(
        f"Dates    : "
        f"{start_date} to {end_date}"
    )

    print(
        f"Target   : {target}"
    )

    print("=" * 60)
    print()

    client = cdsapi.Client()

    print("Downloading ERA5 historical wind...")

    client.retrieve(
        DATASET,
        request,
        target
    )

    print()
    print("Download complete:")
    print(target)


def main():

    if len(sys.argv) != 6:

        print("Usage:")
        print(
            "python download_wind.py "
            "<LATITUDE> "
            "<LONGITUDE> "
            "<START_DATE> "
            "<END_DATE> "
            "<OUTPUT_NC>"
        )

        print()
        print("Example:")
        print(
            "python download_wind.py "
            "28.65 48.75 "
            "2020-08-06 2020-08-10 "
            "wind.nc"
        )

        sys.exit(1)

    latitude = sys.argv[1]
    longitude = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]
    target = sys.argv[5]

    download_wind(
        latitude,
        longitude,
        start_date,
        end_date,
        target
    )


if __name__ == "__main__":
    main()
