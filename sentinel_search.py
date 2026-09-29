import requests
import sys
import json
from datetime import date


CATALOGUE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Sentinel-1A launched in 2014.
SENTINEL1_START_DATE = date(2014, 4, 3)


def search_sentinel1(lat, lon, start_date, end_date):

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError("Start date cannot be after end date.")

    if end < SENTINEL1_START_DATE:
        return {
            "error_type": "no_sentinel_coverage",
            "error": (
                "No Sentinel-1 SAR imagery is available for the "
                "requested date. Sentinel-1 coverage begins in 2014."
            )
        }

    # If the requested range starts before Sentinel-1,
    # search only from the beginning of Sentinel-1 coverage.
    search_start = max(start, SENTINEL1_START_DATE)

    params = {
        "$filter": (
            "startswith(Name,'S1') "
            "and contains(Name,'_IW_GRDH') "
            f"and ContentDate/Start ge {search_start.isoformat()}T00:00:00Z "
            f"and ContentDate/Start le {end.isoformat()}T23:59:59Z "
            "and OData.CSC.Intersects("
            f"area=geography'SRID=4326;POINT({lon} {lat})'"
            ") eq true"
        ),
        "$top": 20
    }

    try:
        response = requests.get(
            CATALOGUE_URL,
            params=params,
            timeout=60
        )

        response.raise_for_status()

    except requests.HTTPError as e:

        status_code = e.response.status_code if e.response is not None else None

        if status_code == 503:
            raise RuntimeError(
                "The Copernicus Sentinel catalogue is temporarily "
                "unavailable. Please retry in a few minutes."
            ) from e

        raise RuntimeError(
            f"Sentinel catalogue request failed with HTTP {status_code}."
        ) from e

    except requests.RequestException as e:

        raise RuntimeError(
            f"Unable to reach the Copernicus Sentinel catalogue: {e}"
        ) from e

    products = response.json().get("value", [])

    if not products:
        return {
            "error_type": "no_scene",
            "error": (
                "No Sentinel-1 GRD SAR scene was found for the "
                "requested location and date."
            )
        }

    cog_products = [
        p for p in products
        if "_COG" in p.get("Name", "")
    ]

    selected = cog_products[0] if cog_products else products[0]

    return {
        "id": selected.get("Id"),
        "name": selected.get("Name"),
        "acquisition_start": (
            selected.get("ContentDate", {}).get("Start")
        ),
        "acquisition_end": (
            selected.get("ContentDate", {}).get("End")
        ),
        "online": selected.get("Online"),
        "size": selected.get("ContentLength"),
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "is_cog": "_COG" in selected.get("Name", "")
    }


def main():

    json_mode = "--json" in sys.argv

    args = [
        arg for arg in sys.argv[1:]
        if arg != "--json"
    ]

    if len(args) != 4:

        message = (
            "Usage: python sentinel_search.py "
            "<latitude> <longitude> "
            "<start_date> <end_date> --json"
        )

        if json_mode:
            print(json.dumps({"error": message}))
        else:
            print(message)

        sys.exit(1)

    try:
        lat = float(args[0])
        lon = float(args[1])
        start_date = args[2]
        end_date = args[3]

        # Validate dates before contacting the API.
        date.fromisoformat(start_date)
        date.fromisoformat(end_date)

    except ValueError as e:

        if json_mode:
            print(json.dumps({
                "error_type": "invalid_input",
                "error": f"Invalid input: {e}"
            }))
        else:
            print()
            print("ERROR: Invalid input.")
            print(e)

        sys.exit(1)

    try:

        result = search_sentinel1(
            lat,
            lon,
            start_date,
            end_date
        )

    except RuntimeError as e:

        if json_mode:
            print(json.dumps({
                "error_type": "catalogue_error",
                "error": str(e)
            }))
        else:
            print()
            print("ERROR: Sentinel catalogue unavailable.")
            print(e)

        sys.exit(1)

    except ValueError as e:

        if json_mode:
            print(json.dumps({
                "error_type": "invalid_input",
                "error": str(e)
            }))
        else:
            print()
            print("ERROR: Invalid date range.")
            print(e)

        sys.exit(1)

    # Expected user-facing "no coverage" result.
    if result.get("error_type") == "no_sentinel_coverage":

        if json_mode:
            print(json.dumps(result))
        else:
            print()
            print("NO SENTINEL-1 COVERAGE")
            print("-" * 70)
            print(result["error"])

        sys.exit(2)

    # Valid Sentinel period but no scene at this location/date.
    if result.get("error_type") == "no_scene":

        if json_mode:
            print(json.dumps(result))
        else:
            print()
            print("NO SENTINEL-1 SCENE FOUND")
            print("-" * 70)
            print(result["error"])

        sys.exit(2)

    if json_mode:
        print(json.dumps(result, indent=4))
        return

    print("=" * 70)
    print("SENTINEL-1 SEARCH")
    print("=" * 70)

    print()
    print(f"Latitude  : {lat}")
    print(f"Longitude : {lon}")
    print(f"Date range: {start_date} → {end_date}")

    print()
    print("SELECTED PRODUCT")
    print("-" * 70)

    print("Name      :", result["name"])
    print("ID        :", result["id"])
    print("Acquired  :", result["acquisition_start"])
    print("Online    :", result["online"])
    print("COG       :", result["is_cog"])

    print()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()