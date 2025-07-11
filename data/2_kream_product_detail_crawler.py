from random import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import os, sys
import json

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root)
from config import CRAWLING_ITEMS

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 ...")
options.add_argument('--disable-logging')
options.add_argument('--log-level=3')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ─────────────────────────────────────────────────────────────────
# 전체 루프를 try/except/finally로 감싸서 중간 중단 시에도 저장 및 드라이버 종료를 보장
try:
    for item in CRAWLING_ITEMS:
        PRODUCT       = item['PRODUCT']
        URL           = item['URL']
        MAIN_CATEGORY = item['MAIN_CATEGORY']
        SUB_CATEGORY  = item['SUB_CATEGORY']

        def crawl_product(product_id):
            url = f"https://kream.co.kr/products/{product_id}"
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "main-title-container"))
                )
            except:
                print(f"[{product_id}] 페이지 로딩 실패")
                return None

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            title_container = soup.find("div", class_="main-title-container")
            if title_container:
                eng_name = title_container.find("p", class_="title").get_text(strip=True) if title_container.find("p", class_="title") else ""
                kor_name = title_container.find("p", class_="sub-title").get_text(strip=True) if title_container.find("p", class_="sub-title") else ""
            else:
                eng_name, kor_name = "", ""

            price_tag = soup.find("span", class_="text-lookup display_paragraph price")
            if not price_tag:
                price_tag = soup.select_one(".text-lookup.display_paragraph.price")
            price = price_tag.get_text(strip=True) if price_tag else ""

            # 이미지 수집 로직 (변경된 부분)
            image_urls = []
            selector = (
                "div.slide_content div.product, "
                "div.slide_item div.product"
            )
            for slide in soup.select(selector):
                img_tag = slide.select_one("picture.product_img img.full_width.image")
                if img_tag:
                    src = img_tag.get("src") or img_tag.get("data-src")
                    image_urls.append(src)

            return {
                "product_id": product_id,
                "eng_name": eng_name,
                "kor_name": kor_name,
                "price": price,
                "images": image_urls
            }

        csv_file = f'./data/output_{PRODUCT}.csv'
        # with 구문으로 열어두면 자동으로 flush & close
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["상품ID", "영문명", "한글명", "가격", "이미지URL(들)"])

            with open(f"./data/product_ids_{PRODUCT}.txt", "r", encoding="utf-8") as id_file:
                for line in id_file:
                    pid = line.strip()
                    if not pid:
                        continue

                    print(f"[진행중] 상품 ID: {pid}")
                    data = crawl_product(pid)

                    if data:
                        if data["price"] != "-" and data["images"] and int(re.sub(r"[^\d]", "", data["price"])) >= 5000000:
                            writer.writerow([
                                data["product_id"],
                                data["eng_name"],
                                data["kor_name"],
                                data["price"],
                                "|".join(data["images"])
                            ])
                        else:
                            print(f"[건너뜀] 상품 ID: {pid} - 유효하지 않은 데이터 (가격: {data['price']}, 이미지 수: {len(data['images'])})")
                    else:
                        print(f"[건너뜀] 상품 ID: {pid} - 데이터 없음")
                        time.sleep(300)  # 데이터가 없을 경우 5분 대기

                    time.sleep(random.uniform(1.0, 2.0))

        # PRODUCT 단건 정보 저장
        driver.get(URL)
        product_details = crawl_product(PRODUCT)
        if product_details:
            with open(f'./data/product_details_{PRODUCT}.json', 'w', encoding='utf-8') as f_json:
                json.dump(product_details, f_json, ensure_ascii=False, indent=4)

# 중간에 Ctrl+C 등으로 중단될 때 잡아내는 블록
except KeyboardInterrupt:
    print("\n[중단됨] 키보드 인터럽트로 크롤링을 종료합니다. 지금까지 수집된 데이터는 CSV 파일에 저장되어 있습니다.")
# 다른 예외가 발생했을 때도 저장은 유지되도록
except Exception as e:
    print(f"\n[에러] {e} 가 발생하여 크롤링을 중단합니다. 지금까지 수집된 데이터는 CSV 파일에 저장되어 있습니다.")
finally:
    # 드라이버는 무조건 종료
    driver.quit()
    print("드라이버 종료 완료")
# ─────────────────────────────────────────────────────────────────
