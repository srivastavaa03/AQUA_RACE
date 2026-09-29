import requests

name = "S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE"

url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

params = {
    "$filter": f"Name eq '{name}'"
}

r = requests.get(url, params=params)

print("Status:", r.status_code)
print(r.text[:5000])