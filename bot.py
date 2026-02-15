import requests
from bs4 import BeautifulSoup
import time
import json
import re

TOKEN = "8469023268:AAEi-dahnEE0XzsuroEA2xLkf1KtbYg81Aw"
CHAT_ID = "453173481"

BASE_URL = "https://auto.bazos.sk/"
MIN_PRICE = 500

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13)"
}

SAVE_FILE = "seen.json"


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


def extract_price(txt):
    m = re.search(r"(\d+)\s*€", txt.replace(" ", ""))
    return int(m.group(1)) if m else None


def extract_id(link):
    m = re.search(r"(\d+)\.html", link)
    return m.group(1) if m else None


print("🚀 Bot started...")

while True:
    try:
        html = requests.get(BASE_URL, headers=HEADERS, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        links = soup.select("a[href*='.html']")

        for a in links:
            link = a.get("href")
            ad_id = extract_id(link)

            if not ad_id or ad_id in seen:
                continue

            title = a.get_text(strip=True)
            if not title:
                continue

            # пробуємо знайти ціну поруч
            parent = a.parent.get_text(" ", strip=True)
            price = extract_price(parent)

            if price and price >= MIN_PRICE:
                msg = f"🚗 Нове авто\n{title}\n💶 {price}€\n{link}"
                send(msg)

                seen.add(ad_id)
                save_seen()

        time.sleep(120)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)