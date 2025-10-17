import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.gsmarena.com/"

def get_brands():
    """All brands collect করে list বানায়"""
    brands = []
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    brand_list = soup.select(".brandmenu-v2 li a")
    for b in brand_list:
        name = b.text.strip()
        url = BASE_URL + b.get("href")
        brands.append({"name": name, "url": url})
    return brands

def get_phones_for_brand(brand_url, brand_name):
    """একটা ব্র্যান্ডের সব ফোনের নাম + ইমেজ + লিংক নিয়ে আসে"""
    phones = []
    page_url = brand_url
    while True:
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        phone_list = soup.select(".makers ul li a")
        if not phone_list:
            break

        for p in phone_list:
            model_name = p.select_one("strong").text.strip() if p.select_one("strong") else p.text.strip()
            phone_link = BASE_URL + p.get("href")
            img_tag = p.select_one("img")
            img_url = img_tag.get("src") if img_tag else ""

            phones.append({
                "brand": brand_name,
                "model": model_name,
                "url": phone_link,
                "image": img_url
            })

        # Next page আছে কিনা
        next_page = soup.select_one("a.pages-next")
        if next_page:
            page_url = BASE_URL + next_page.get("href")
            time.sleep(1)
        else:
            break
    return phones

def main():
    print("📡 Starting GSMArena Scraper...")
    brands = get_brands()
    print(f"✅ Found {len(brands)} brands")

    all_phones = []
    for b in brands:
        print(f"🔹 Scraping {b['name']} ...")
        phones = get_phones_for_brand(b['url'], b['name'])
        print(f"   └─ {len(phones)} phones found")
        all_phones.extend(phones)
        time.sleep(1)

    os.makedirs("data", exist_ok=True)
    with open("data/phones.json", "w", encoding="utf-8") as f:
        json.dump(all_phones, f, ensure_ascii=False, indent=2)

    print(f"📁 Saved {len(all_phones)} phones to data/phones.json")

if __name__ == "__main__":
    main()
