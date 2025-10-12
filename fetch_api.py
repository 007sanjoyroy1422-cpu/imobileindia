#!/usr/bin/env python3
"""
fetch_api.py
Simple updater script that fetches phone data from a configured API and writes devices.json.

Expected:
- Environment variable API_URL (e.g. https://api.example.com/phones)
- Optionally API_KEY in env var
This script should be adapted to the target API's response format.
"""
import os, sys, json, requests

API_URL = os.getenv('API_URL') or ''
API_KEY = os.getenv('API_KEY') or ''

if not API_URL:
    print("Please set API_URL environment variable to a phones API endpoint.")
    sys.exit(1)

headers = {}
if API_KEY:
    headers['Authorization'] = f'Bearer {API_KEY}'

print("Fetching from", API_URL)
resp = requests.get(API_URL, headers=headers, timeout=30)
resp.raise_for_status()
data = resp.json()

# The following mapping assumes API returns a list of phone objects with expected fields.
# Adapt this part to match your actual API.

devices = []
for item in data:
    devices.append({
        "id": item.get("id") or item.get("slug") or item.get("model"),
        "brand": item.get("brand") or item.get("manufacturer"),
        "model": item.get("model") or item.get("phone_name"),
        "release": item.get("release_date") or item.get("release"),
        "display": item.get("display") or item.get("screen"),
        "os": item.get("os"),
        "chipset": item.get("chipset"),
        "ram": item.get("ram"),
        "storage": item.get("storage"),
        "battery": item.get("battery"),
        "camera": item.get("camera"),
        "price": item.get("price"),
        "images": item.get("images") or {}
    })

with open('devices.json', 'w', encoding='utf-8') as f:
    json.dump(devices, f, indent=2, ensure_ascii=False)
print("Wrote devices.json with", len(devices), "items")
