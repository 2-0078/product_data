# product id 크롤러
# kream 에서 검색한 상품 목록을 보고, product id를 추출하는 스크립트입니다.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # 추가 설치 필요: pip install webdriver-manager
from bs4 import BeautifulSoup
import os, sys

# 이 파일(__file__)이 있는 곳(data_iput/data)에서 루트까지 올려서 추가
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(root)

from config import CRAWLING_ITEMS

# 크롬 드라이버 경로 설정
# CHROMEDRIVER_PATH = 'C:/Users/sujin/Downloads/chromedriver-win64/chromedriver.exe'

# 크롬 옵션 설정
options = Options()
options.add_argument('--headless')  # 창 숨김
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.120 Safari/537.36")

# 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for item in CRAWLING_ITEMS:
    PRODUCT = item['PRODUCT']
    URL = item['URL']
    MAIN_CATEGORY = item['MAIN_CATEGORY']
    SUB_CATEGORY = item['SUB_CATEGORY']

    # KREAM 검색 결과 페이지 접속 (현재는 시계만 검색한 url입니다.)
    driver.get(URL)

    # 요소 로딩 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.search_result_list"))
        )
    except:
        print("검색 결과 리스트가 로드되지 않았습니다.")

    # 페이지 소스 가져오기
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    search_result = soup.find("div", class_="search_result")
    if search_result:
        search_result_list = search_result.find("div", class_="search_result_list")
        if search_result_list:
            products = search_result_list.find_all("div", class_="search_result_item product")
            print(f"발견된 상품 수: {len(products)}")

            with open(f'./product_ids_{PRODUCT}.txt', 'w', encoding='utf-8') as f:
                for PRODUCT in products:
                    product_id = PRODUCT.get("data-product-id")
                    if product_id:
                        print(f"상품 ID: {product_id}")
                        f.write(product_id + '\n')
        else:
            print("search_result_list 영역을 찾지 못했습니다.")
    else:
        print("search_result 영역을 찾지 못했습니다.")

driver.quit()
