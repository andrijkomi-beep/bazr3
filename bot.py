import requests
from bs4 import BeautifulSoup
import time
import json
import re

TOKEN = "ТВІЙ_TOKEN"
CHAT_ID = "ТВІЙ_CHAT_ID"

BASE_URL = "https://auto.bazos.sk/"
MIN_PRICE = 500

PAGES = 10
INTERVAL = 120  # 2 хв

SAVE_FILE = "seen.json"


# ---------------- Load seen ----------------
try:
    with open(SAVE_FILE, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()


def save_seen():
    with open(SAVE_FILE, "w") as f:
        json.dump(list(seen), f)


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def extract_price(text):
    m = re.search(r"(\d+)\s*€", text.replace(" ", ""))
    if m:
        return int(m.group(1))
    return None


def extract_id(link):
    m = re.search(r"/(\d+)\.html", link)
    return m.group(1) if m else None


print("🚀 Auto bot started...")


while True:
    try:
        for page in range(0, PAGES):

            url = f"{BASE_URL}{page*20}/"
            html = requests.get(url, timeout=10).text

            soup = BeautifulSoup(html, "html.parser")

            ads = soup.find_all("div", class_="inzerat")

            for ad in ads:

                # ❌ Пропускаємо TOP
                if "inzeratynad" in str(ad):
                    continue

                a = ad.find("a", href=True)
                if not a:
                    continue

                link = a["href"]
                ad_id = extract_id(link)

                if not ad_id or ad_id in seen:
                    continue

                title = a.get_text(strip=True)

                price_tag = ad.find("div", class_="inzeratycena")
                if not price_tag:
                    continue

                price = extract_price(price_tag.get_text())

                if price is None or price < MIN_PRICE:
                    continue

                msg = f"🚗 НОВЕ авто ≥{MIN_PRICE}€\n\n{title}\n💶 {price}€\n{link}"
                send(msg)

                print("Sent:", title)

                seen.add(ad_id)
                save_seen()

        time.sleep(INTERVAL)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)