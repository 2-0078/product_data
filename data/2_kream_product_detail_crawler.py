# 크롤링 코드
# 이미 product_id를 모아둔 csv 파일이 있다고 가정하고, 
#   해당 파일에서 product_id를 읽어와서 상세 정보를 크롤링합니다.


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # 추가 설치 필요: pip install webdriver-manager
from bs4 import BeautifulSoup
import csv
import time
import os, sys
import json

# 이 파일(__file__)이 있는 곳(data_iput/data)에서 루트까지 올려서 추가
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(root)

from config import CRAWLING_ITEMS

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.120 Safari/537.36")
options.add_argument('--disable-logging')  # 로깅 비활성화
options.add_argument('--log-level=3')  # 최소 로그 수준 설정

# 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for item in CRAWLING_ITEMS:
    PRODUCT = item['PRODUCT']
    URL = item['URL']
    MAIN_CATEGORY = item['MAIN_CATEGORY']
    SUB_CATEGORY = item['SUB_CATEGORY']

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

        linked_group = soup.find("div", class_="product-linked-group-list")
        image_urls = []
        if linked_group:
            linked_items = linked_group.find_all("div", class_="linked-group-item")
            for item in linked_items:
                img_tag = item.find("img")
                if img_tag and img_tag.has_attr("src"):
                    image_urls.append(img_tag["src"])

        return {
            "product_id": product_id,
            "eng_name": eng_name,
            "kor_name": kor_name,
            "price": price,
            "images": image_urls
        }

    csv_file = f'output_{PRODUCT}.csv'
    with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["상품ID", "영문명", "한글명", "가격", "이미지URL(들)"])

        with open(f"product_ids_{PRODUCT}.txt", "r", encoding="utf-8") as id_file:
            for line in id_file:
                pid = line.strip()
                if not pid:
                    continue
                print(f"[진행중] 상품 ID: {pid}")
                data = crawl_product(pid)
                
                # 데이터 검증: price가 "-"이거나 images가 비어 있으면 건너뜀
                if data:
                    if data["price"] != "-" and data["images"]:
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
                
                time.sleep(1)

    driver.get(URL)

    product_details = crawl_product(PRODUCT)
    if product_details:
        with open(f'./product_details_{PRODUCT}.json', 'w', encoding='utf-8') as f:
            json.dump(product_details, f, ensure_ascii=False, indent=4)

driver.quit()
print(f"크롤링 완료, 결과는 {csv_file} 파일에 저장됨")
