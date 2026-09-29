import requests
import getpass

username = input("Copernicus username: ")
password = getpass.getpass("Copernicus password: ")

url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

data = {
    "client_id": "cdse-public",
    "username": username,
    "password": password,
    "grant_type": "password"
}

r = requests.post(url, data=data)

print("Status:", r.status_code)

if r.status_code == 200:
    print("LOGIN SUCCESS ✅")
    print("Token received:", len(r.json()["access_token"]))
else:
    print("LOGIN FAILED ❌")
    print(r.text)