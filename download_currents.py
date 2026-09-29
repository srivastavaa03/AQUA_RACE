import sys
import os
from datetime import datetime, timedelta

import copernicusmarine


DATASET_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m_202311"


def download_currents(
    latitude,
    longitude,
    start_date,
    end_date,
    output_file
):

    latitude = float(latitude)
    longitude = float(longitude)

    start = datetime.strptime(
        start_date,
        "%Y-%m-%d"
    )

    end = datetime.strptime(
        end_date,
        "%Y-%m-%d"
    )

    if end < start:
        raise ValueError(
            "End date cannot be before start date."
        )

    # Small area around detected spill.
    north = min(90.0, latitude + 1.0)
    south = max(-90.0, latitude - 1.0)
    west = max(-180.0, longitude - 1.0)
    east = min(180.0, longitude + 1.0)

    os.makedirs(
        os.path.dirname(
            os.path.abspath(output_file)
        ),
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("       COPERNICUS OCEAN CURRENT DOWNLOAD")
    print("=" * 60)

    print(f"Dataset   : {DATASET_ID}")
    print(f"Latitude  : {latitude}")
    print(f"Longitude : {longitude}")
    print(f"Dates     : {start_date} to {end_date}")

    print(
        f"Area      : "
        f"{north:.3f}, "
        f"{west:.3f}, "
        f"{south:.3f}, "
        f"{east:.3f}"
    )

    print(f"Output    : {output_file}")

    print("=" * 60)
    print()

    print("Downloading Copernicus ocean currents...")

    copernicusmarine.subset(
        dataset_id=DATASET_ID,

        variables=[
            "uo",
            "vo",
        ],

        minimum_longitude=west,
        maximum_longitude=east,

        minimum_latitude=south,
        maximum_latitude=north,

        start_datetime=start_date,
        end_datetime=end_date,

        output_filename=os.path.basename(
            output_file
        ),

        output_directory=os.path.dirname(
            os.path.abspath(output_file)
        ),

        force_download=True,
    )

    print()
    print("Download complete:")
    print(output_file)


def main():

    if len(sys.argv) != 6:

        print("Usage:")

        print(
            "python download_currents.py "
            "<LATITUDE> "
            "<LONGITUDE> "
            "<START_DATE> "
            "<END_DATE> "
            "<OUTPUT_NC>"
        )

        print()

        print("Example:")

        print(
            "python download_currents.py "
            "28.65 48.75 "
            "2020-08-10 2020-08-10 "
            "currents.nc"
        )

        sys.exit(1)

    download_currents(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
    )


if __name__ == "__main__":
    main()
