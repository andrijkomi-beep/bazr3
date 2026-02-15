import requests
from bs4 import BeautifulSoup
import json
import time
import re

# =========================
# Налаштування
# =========================
TOKEN = "8469023268:AAEi-dahnEE0XzsuroEA2xLkf1KtbYg81Aw"
CHAT_ID = "453173481"
BASE_URL = "https://auto.bazos.sk/"
CATEGORY = "auta"  # можна змінити на потрібну категорію
MIN_PRICE = 500
CHECK_INTERVAL = 180  # секунд між перевірками
NUM_PAGES = 50       # скільки сторінок перевіряти
SAVE_FILE = "seen_ads.json"

# =========================
# Завантаження історії
# =========================
try:
    with open(SAVE_FILE, "r") as f:
        seen_ids = set(json.load(f))
except:
    seen_ids = set()

# =========================
# Функції
# =========================
def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def save_seen():
    with open(SAVE_FILE, "w") as f:
        json.dump(list(seen_ids), f)

def extract_price(text):
    nums = re.findall(r"\d+", text.replace(" ", ""))
    if nums:
        return int("".join(nums))
    return 0

# =========================
# Головний цикл
# =========================
print("🚀 Бот запущений...")

while True:
    try:
        for page in range(1, NUM_PAGES + 1):
            url = f"{BASE_URL}{CATEGORY}/?page={page}"
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Кожне оголошення
            ads = soup.find_all("div", class_="inzerat")  # основний блок оголошення
            for ad in ads:
                # Пропускаємо топові оголошення
                if ad.find(class_="top"):
                    continue

                # Отримуємо ID з посилання
                link_tag = ad.find("a", href=True)
                if not link_tag:
                    continue
                link = link_tag["href"]
                ad_id_match = re.search(r'/(\d+)\.html', link)
                if not ad_id_match:
                    continue
                ad_id = ad_id_match.group(1)

                if ad_id in seen_ids:
                    continue

                # Отримуємо title та ціну
                title_tag = ad.find("h3")
                title = title_tag.text.strip() if title_tag else "Без назви"

                price_tag = ad.find("p", class_="cena")
                price = extract_price(price_tag.text) if price_tag else 0
                if price < MIN_PRICE:
                    continue

                # Відправляємо повідомлення
                msg = f"🚗 Нове авто ({price}€+)\n\n{title}\n💰 {price}€\n🔗 {link}"
                send_message(msg)
                print("Відправлено:", title)

                # Додаємо до історії
                seen_ids.add(ad_id)
                save_seen()

    except Exception as e:
        print("❌ Помилка:", e)

    time.sleep(CHECK_INTERVAL)