import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://gsmarena.com/"
OUTPUT_FILE = "data/phones.json"

def scrape_brands():
    print("📡 Scraping brand list...")
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    brand_links = soup.select('.brandmenu-v2 ul li a')
    brands = []
    for link in brand_links:
        name = link.text.strip()
        url = BASE_URL + link['href']
        brands.append({'name': name, 'url': url})
    return brands

def scrape_phones(brand_url):
    print(f"📲 Scraping phones from {brand_url}")
    res = requests.get(brand_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    phone_links = soup.select('.makers ul li a')
    phones = []
    for a in phone_links:
        model = a.find('strong').text.strip() if a.find('strong') else "Unknown"
        thumb = a.find('img')['src'] if a.find('img') else None
        url = BASE_URL + a['href']
        phones.append({
            'model': model,
            'url': url,
            'thumb': thumb
        })
    return phones

def main():
    brands = scrape_brands()
    all_data = []
    for brand in brands:
        try:
            phones = scrape_phones(brand['url'])
            all_data.append({
                'brand': brand['name'],
                'phones': phones
            })
            time.sleep(1)  # prevent blocking
        except Exception as e:
            print(f"⚠️ Error scraping {brand['name']}: {e}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved scraped data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
