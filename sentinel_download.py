import os
import sys
import requests


TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

DOWNLOAD_URL = (
    "https://download.dataspace.copernicus.eu/"
    "odata/v1/Products({})/$value"
)


def get_token():

    username = os.getenv("CDSE_USERNAME")
    password = os.getenv("CDSE_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "CDSE_USERNAME and CDSE_PASSWORD environment variables "
            "are not set."
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": username,
            "password": password,
        },
        timeout=60
    )

    response.raise_for_status()

    return response.json()["access_token"]


def download_product(product_id, output_path):

    token = get_token()

    url = DOWNLOAD_URL.format(product_id)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    print()
    print("Downloading Sentinel-1 product...")
    print(f"Product ID : {product_id}")
    print(f"Output     : {output_path}")

    with requests.get(
        url,
        headers=headers,
        stream=True,
        timeout=120
    ) as response:

        response.raise_for_status()

        total = int(
            response.headers.get(
                "content-length",
                0
            )
        )

        downloaded = 0

        with open(output_path, "wb") as f:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if not chunk:
                    continue

                f.write(chunk)

                downloaded += len(chunk)

                if total:
                    percent = (
                        downloaded / total
                    ) * 100

                    print(
                        f"\rProgress: "
                        f"{percent:6.2f}%",
                        end=""
                    )

    print()
    print("Download complete.")


def main():

    if len(sys.argv) != 3:

        print(
            "Usage:\n"
            "python sentinel_download.py "
            "<product_id> <output_path>"
        )

        sys.exit(1)

    product_id = sys.argv[1]
    output_path = sys.argv[2]

    try:

        download_product(
            product_id,
            output_path
        )

    except Exception as e:

        print()
        print("ERROR:")
        print(e)

        sys.exit(1)


if __name__ == "__main__":
    main()
