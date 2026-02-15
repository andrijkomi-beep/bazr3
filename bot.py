import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os

# =========================
# НАЛАШТУВАННЯ
# =========================

TOKEN = "8469023268:AAEi-dahnEE0XzsuroEA2xLkf1KtbYg81Aw"
CHAT_ID = "453173481"

URL = "https://auto.bazos.sk/"
MIN_PRICE = 500

SAVE_FILE = "seen_ads.json"
CHECK_INTERVAL = 180  # кожні 3 хвилини

# =========================
# ЗАВАНТАЖЕННЯ ІСТОРІЇ
# =========================

if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        seen_links = set(json.load(f))
else:
    seen_links = set()

# =========================
# ФУНКЦІЇ
# =========================

def save_seen():
    with open(SAVE_FILE, "w") as f:
        json.dump(list(seen_links), f)

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def extract_price(price_text):
    nums = re.findall(r"\d+", price_text.replace(" ", ""))
    if nums:
        return int("".join(nums))
    return 0

# =========================
# ГОЛОВНИЙ ЦИКЛ
# =========================

print("🚀 Бот запущений...")

while True:
    try:
        response = requests.get(URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        ads = soup.select(".inzeraty.inzeratyflex")

        for ad in ads[:20]:
            title = ad.select_one("h2").text.strip()

            link = ad.select_one("a")["href"]
            full_link = "https://auto.bazos.sk" + link

            price_text = ad.select_one(".inzeratycena").text.strip()
            price = extract_price(price_text)

            if price < MIN_PRICE:
                continue

            if full_link not in seen_links:
                seen_links.add(full_link)
                save_seen()

                msg = (
                    f"🚗 Нове авто ({price}€+)\n\n"
                    f"{title}\n"
                    f"💰 {price_text}\n"
                    f"🔗 {full_link}"
                )

                send_message(msg)
                print("Відправлено:", title)

        print("✅ Перевірено, чекаю...")

    except Exception as e:
        print("❌ Помилка:", e)

    time.sleep(CHECK_INTERVAL)
