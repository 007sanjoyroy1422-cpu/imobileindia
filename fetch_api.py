#!/usr/bin/env python3
"""
fetch_devices.py
Fetch phones from api-mobilespecs.azharimm.dev (default) and map to target schema.

Usage:
  API_SOURCE=azharimm LIMIT_BRANDS=60 python fetch_devices.py
  API_SOURCE=programminghero python fetch_devices.py
"""
import os, time, json, logging, requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
BASE = "https://api-mobilespecs.azharimm.dev"
USER_AGENT = "Mozilla/5.0 (compatible; ImobileindiaBot/1.0)"
OUT = "devices.json"
REQUEST_DELAY = 0.15

def safe_get(url):
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def build_device(detail):
    # best-effort mapping to your schema
    d = {
      "id": detail.get("phone_id") or detail.get("slug") or detail.get("phone_name"),
      "brand": detail.get("brand"),
      "model": detail.get("phone_name"),
      "series": None,
      "slug": detail.get("slug"),
      "release_date": detail.get("release_date") or detail.get("year"),
      "status": "launched",
      "price": None,
      "currency": "USD",
      "price_region": {},
      "affiliate_links": [],
      "dimensions": None,
      "weight": None,
      "build": None,
      "colors": detail.get("colors") or [],
      "display": {},
      "platform": {},
      "memory": {},
      "camera": {},
      "battery": {},
      "connectivity": {},
      "sensors": [],
      "audio": {},
      "images": detail.get("images") or {},
      "official_url": None,
      "notes": None,
      "meta_title": None,
      "meta_description": None
    }

    # parse specs if present (azharimm sometimes includes 'specifications' structure)
    specs = detail.get("specifications") or detail.get("specs") or []
    # specs may be a list of sections: convert to key->value quick map
    try:
        if isinstance(specs, list):
            spec_map = {}
            for sec in specs:
                title = sec.get("title") if isinstance(sec, dict) else None
                if title and isinstance(sec.get("specs"), list):
                    for item in sec.get("specs"):
                        k = item.get("key") if isinstance(item, dict) else None
                        v = item.get("val") if isinstance(item, dict) else None
                        if k:
                            spec_map.setdefault(title, {})[k] = v
            # Example extraction
            display_section = spec_map.get("Display") or {}
            platform_section = spec_map.get("Platform") or {}
            battery_section = spec_map.get("Battery") or {}
            camera_section = spec_map.get("Main Camera") or spec_map.get("Camera") or {}
            memory_section = spec_map.get("Memory") or {}
            d["display"] = {
                "type": display_section.get("Type") or display_section.get("Technology") or None,
                "size": display_section.get("Size") or None,
                "resolution": display_section.get("Resolution") or None,
                "refresh_rate": display_section.get("Refresh Rate") or None,
                "protection": display_section.get("Protection") or None
            }
            d["platform"] = {
                "os": platform_section.get("OS") or platform_section.get("Operating System") or None,
                "os_version": None,
                "ui": None,
                "chipset": platform_section.get("Chipset") or None,
                "cpu": None,
                "gpu": None
            }
            d["battery"] = {
                "capacity": battery_section.get("Capacity") or None,
                "charging": battery_section.get("Fast charging") or None,
                "wireless_charging": None,
                "reverse_charging": None
            }
            d["camera"] = {
                "rear": [{"position":"main","mp": camera_section.get("Resolution") or camera_section.get("Megapixels") or None}],
                "front": [],
                "video": None
            }
            d["memory"] = {
                "ram": memory_section.get("Internal") or None,
                "storage": None,
                "card_slot": None
            }
    except Exception as e:
        logging.debug("spec parse error: %s", e)

    return d

def fetch_azharimm(limit_brands=60):
    out = []
    logging.info("Fetching brands list...")
    data = safe_get(BASE + "/brands")
    brands = data.get("data") or data
    for idx, b in enumerate(brands[:limit_brands]):
        slug = b.get("brand_slug") or b.get("slug") or b.get("brand")
        logging.info("Brand %s (%d/%d)", slug, idx+1, min(limit_brands, len(brands)))
        page = 1
        while True:
            time.sleep(REQUEST_DELAY)
            url = f"{BASE}/brands/{slug}?page={page}"
            try:
                resp = safe_get(url)
            except Exception as e:
                logging.warning("brand page fail %s", e)
                break
            items = resp.get("data") or resp.get("phones") or []
            if not items:
                break
            for it in items:
                phone_slug = it.get("phone_slug") or it.get("slug")
                if not phone_slug:
                    continue
                try:
                    time.sleep(REQUEST_DELAY)
                    detail = safe_get(f"{BASE}/brands/{phone_slug}")
                    mapped = build_device(detail)
                    out.append(mapped)
                except Exception as ex:
                    logging.warning("detail fail %s", ex)
            page += 1
    return out

def fetch_programminghero():
    out = []
    base = "https://openapi.programming-hero.com/api/phones?search="
    queries = ['iphone','samsung','xiaomi','oneplus','oppo','vivo','realme','google','motorola','nokia']
    for q in queries:
        try:
            time.sleep(0.1)
            r = requests.get(base + q, headers={"User-Agent": USER_AGENT}, timeout=15).json()
            items = r.get("data") or r.get("phones") or []
            for it in items:
                out.append({
                  "id": it.get("slug") or it.get("phoneId"),
                  "brand": it.get("brand") or q,
                  "model": it.get("phone_name") or None,
                  "slug": it.get("slug") or None,
                  "release_date": None,
                  "status": "launched",
                  "images": {},
                })
        except Exception as e:
            logging.warning("prog hero fail %s", e)
    return out

if __name__ == "__main__":
    src = os.getenv("API_SOURCE", "azharimm")
    limit_brands = int(os.getenv("LIMIT_BRANDS", "60"))
    logging.info("Starting fetch_devices (source=%s limit_brands=%d)", src, limit_brands)
    devices = []
    if src == "programminghero":
        devices = fetch_programminghero()
    else:
        devices = fetch_azharimm(limit_brands=limit_brands)
    # dedupe by id
    seen = set(); dedup = []
    for d in devices:
        rid = str(d.get("id"))
        if rid and rid not in seen:
            seen.add(rid); dedup.append(d)
    Path(OUT).write_text(json.dumps(dedup, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info("Wrote %d devices to %s", len(dedup), OUT)
