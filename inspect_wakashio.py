import requests

product_id = "d9b01bbf-81b2-5ca4-8fc3-0d74c4d3dac0"

url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/Nodes"

r = requests.get(url)

print("Status:", r.status_code)
print(r.text[:10000])