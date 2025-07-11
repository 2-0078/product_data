# product id 크롤러
# kream 에서 검색한 상품 목록을 보고, product id를 추출하는 스크립트입니다.

import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ─── 프로젝트 루트 경로 설정 ───────────────────────────────────────────────────
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root)
from config import CRAWLING_ITEMS  # [{"PRODUCT":..., "URL":...}, ...]

# ─── 크롬 드라이버 옵션 설정 ───────────────────────────────────────────────────
options = Options()
# 화면이 보이도록 헤드리스 모드 해제
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
# DevTools 메시지 억제
options.add_experimental_option('excludeSwitches', ['enable-logging'])
service = Service(ChromeDriverManager().install(), log_path=os.devnull)

driver = webdriver.Chrome(service=service, options=options)

for item in CRAWLING_ITEMS:
    PRODUCT = item['PRODUCT']
    URL     = item['URL']

    driver.get(URL)

    # 1) 초기 로딩 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.search_result_list"))
        )
    except TimeoutException:
        print(f"[{PRODUCT}] search_result_list 로딩 실패")
        continue

    # 2) 반복 스크롤 설정
    INITIAL_STEP   = 500     # 처음 한번에 내릴 픽셀
    SMALL_STEP     = 500      # 이후 단계별 픽셀
    SMALL_ROUNDS   = 20        # 단계별 반복 횟수
    PAUSE          = 0.1      # 스크롤 후 대기 (초)
    OUTER_ROUNDS   = 30       # 전체 반복 최대 횟수
    driver.execute_script("window.scrollBy(0, arguments[0]);", INITIAL_STEP)
    time.sleep(PAUSE)

    total_prev = len(driver.find_elements(
        By.CSS_SELECTOR,
        "div.search_result_list div.search_result_item.product"
    ))

    for i in range(OUTER_ROUNDS):
        added = False

        # 단계별 소폭 스크롤
        for _ in range(SMALL_ROUNDS):
            prev_count = len(driver.find_elements(
                By.CSS_SELECTOR,
                "div.search_result_list div.search_result_item.product"
            ))

            driver.execute_script("window.scrollBy(0, arguments[0]);", SMALL_STEP)
            time.sleep(PAUSE)

            # 로딩된 상품 수 증가 대기
            try:
                WebDriverWait(driver, 2).until(
                    lambda d: len(d.find_elements(
                        By.CSS_SELECTOR,
                        "div.search_result_list div.search_result_item.product"
                    )) > prev_count
                )
                added = True
            except:
                # 변화 없으면 다음 스텝 진행
                pass

        # 한 사이클 끝나고 전체 상품 수 비교
        total_now = len(driver.find_elements(
            By.CSS_SELECTOR,
            "div.search_result_list div.search_result_item.product"
        ))
        if total_now == total_prev and not added:
            print(f"[{PRODUCT}] 더 이상 로드된 상품이 없어 {i}번 반복 후 중지")
            break

        total_prev = total_now

        # 다음 사이클: 한 번에 3500px 더 내려주기
        driver.execute_script("window.scrollBy(0, arguments[0]);", INITIAL_STEP)
        time.sleep(PAUSE)

    # 3) 파싱 및 상품 ID 추출
    soup     = BeautifulSoup(driver.page_source, 'html.parser')
    products = soup.select("div.search_result_list div.search_result_item.product")
    print(f"[{PRODUCT}] 최종 총 상품 수: {len(products)}")

    # 4) ID 저장
    with open(f'./data/product_ids_{PRODUCT}.txt', 'w', encoding='utf-8') as f:
        for p in products:
            pid = p.get("data-product-id")
            if pid:
                f.write(pid + '\n')

driver.quit()
