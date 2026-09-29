import requests

url = "https://download.dataspace.copernicus.eu/odata/v1/Products(d9b01bbf-81b2-5ca4-8fc3-0d74c4d3dac0)/Nodes(S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE)/Nodes"

r = requests.get(url)

print("Status:", r.status_code)
print(r.text[:20000])