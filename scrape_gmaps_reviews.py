# source .venv/bin/activate
# export HEADLESS=0
# export USER_DATA_DIR=./chrome_profile
# python3 scrape_gmaps_reviews.py

import os
import time
import csv

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ================= CONFIG =================

load_dotenv()

FOLDER_PATH = "./data/raw/"

MAPS_URL = os.getenv("MAPS_URL")
OUTPUT = FOLDER_PATH + os.getenv("OUTPUT_CSV")
HEADLESS = int(os.getenv("HEADLESS", "0") == "1")
USER_DATA_DIR = os.getenv("USER_DATA_DIR")
MAX_SCROLL = int(os.getenv("MAX_SCROLL") or 100)
WAIT_SEC = 20
MAX_STUCK = 25        # กี่รอบที่ไม่มีรีวิวใหม่แล้วหยุด
SCROLL_PAUSE = 1.2

# ================= DRIVER =================

def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--lang=th-TH")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-blink-features=AutomationControlled")

    if USER_DATA_DIR:
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")

    return webdriver.Chrome(options=options)


# ================= OPEN ALL REVIEWS =================

def open_all_reviews(driver):
    wait = WebDriverWait(driver, WAIT_SEC)

    # รอหน้า place โหลด
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)

    # พยายามคลิก "ดูรีวิวทั้งหมด / More reviews"
    candidates = [
        "//button[contains(.,'ดูรีวิว')]",
        "//button[contains(.,'รีวิว')]",
        "//button[contains(.,'reviews')]",
        "//button[contains(.,'Reviews')]",
        "//button[contains(@aria-label,'รีวิว')]",
        "//button[contains(@aria-label,'reviews')]",
    ]

    clicked = False
    for xp in candidates:
        buttons = driver.find_elements(By.XPATH, xp)
        if buttons:
            driver.execute_script("arguments[0].click();", buttons[0])
            clicked = True
            break

    if not clicked:
        raise RuntimeError("❌ ไม่พบปุ่มเปิดรีวิวทั้งหมด")

    # รอ dialog รีวิวจริง ๆ
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']")))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jftiEf")))


# ================= SCROLL CONTAINER =================

def find_scroll_container(driver):
    card = driver.find_element(By.CSS_SELECTOR, "div.jftiEf")

    container = driver.execute_script(
        """
        let el = arguments[0];
        while (el && el !== document.body) {
            const st = window.getComputedStyle(el).overflowY;
            if ((st === 'auto' || st === 'scroll') && el.scrollHeight > el.clientHeight) {
                return el;
            }
            el = el.parentElement;
        }
        return null;
        """,
        card,
    )

    if not container:
        raise RuntimeError("❌ หา scroll container ไม่เจอ")

    return container


# ================= HELPERS =================

def expand_more_buttons(driver):
    buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
    for b in buttons:
        try:
            driver.execute_script("arguments[0].click();", b)
        except Exception:
            pass


def parse_visible_reviews(driver, seen, rows):
    cards = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    new_count = 0

    for card in cards:
        try:
            review_id = card.get_attribute("data-review-id")
            if not review_id or review_id in seen:
                continue

            seen.add(review_id)

            author = card.find_element(By.CSS_SELECTOR, "div.d4r55").text
            text = card.find_element(By.CSS_SELECTOR, "span.wiI7pd").text

            # rating จาก aria-label เช่น "5 ดาว"
            rating = None
            try:
                star = card.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                aria = star.get_attribute("aria-label") or ""
                for n in ["1", "2", "3", "4", "5"]:
                    if aria.strip().startswith(n):
                        rating = int(n)
                        break
            except Exception:
                rating = None

            rows.append(
                {
                    "review_id": review_id,
                    "author": author,
                    "rating": rating,
                    "text": text,
                }
            )
            new_count += 1

        except Exception:
            continue

    return new_count, cards


# ================= MAIN =================

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, WAIT_SEC)

    print("🌐 Opening:", MAPS_URL)
    driver.get(MAPS_URL)

    open_all_reviews(driver)
    container = find_scroll_container(driver)

    seen = set()
    rows = []

    stuck = 0
    round_i = 0

    while stuck < MAX_STUCK and len(rows) < MAX_SCROLL:
        expand_more_buttons(driver)

        new_count, cards = parse_visible_reviews(driver, seen, rows)

        print(
            f"🔄 round {round_i} | visible={len(cards)} "
            f"| total_saved={len(rows)} | new={new_count}"
        )

        if new_count == 0:
            stuck += 1
        else:
            stuck = 0

        # scroll container
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight * 0.9;",
            container,
        )

        time.sleep(SCROLL_PAUSE)
        round_i += 1

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jftiEf")))
        except Exception:
            pass

    print(f"✅ Collected {len(rows)} reviews (unique)")

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["review_id", "author", "rating", "text"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"📁 Saved: {OUTPUT}")
    driver.quit()



if __name__ == "__main__":
    os.makedirs(FOLDER_PATH, exist_ok=True)
    main()
