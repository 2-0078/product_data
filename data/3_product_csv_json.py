import csv
import json
import random
import os, sys

# 이 파일(__file__)이 있는 곳(data_iput/data)에서 루트까지 올려서 추가
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(root)

from config import CRAWLING_ITEMS

for item in CRAWLING_ITEMS:
    PRODUCT = item['PRODUCT']
    MAIN_CATEGORY = item['MAIN_CATEGORY']
    SUB_CATEGORY = item['SUB_CATEGORY']

    input_filename = f'output_{PRODUCT}.csv'
    output_filename = f'converted_products_{PRODUCT}.json'

    products = []

    with open(input_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                purchase_price = int(row['가격'].replace(',', '').replace('원', '').strip())
            except ValueError:
                continue
            
            # storageLocation을 [물류A, 물류B, 물류C] 중 랜덤으로 설정
            storage_location = random.choice(["물류A", "물류B", "물류C"])
            
            # profileImageUrlList 추가
            profile_image_urls = row['이미지URL(들)'].split('|')[:3] if '이미지URL(들)' in row else []  # 최대 3개의 이미지 URL만 저장

            product = {
                "productName": row['한글명'],
                "purchasePrice": purchase_price,
                "status": "STORED",
                "storageLocation": storage_location,
                "description": row['영문명'],
                "mainCategory": {
                    "categoryName": MAIN_CATEGORY
                },
                "subCategory": {
                    "categoryName": SUB_CATEGORY
                },
                "profileImageUrlList": profile_image_urls,  # 이미지 URL 리스트 추가
            }
            products.append(product)

    with open(output_filename, 'w', encoding='utf-8-sig') as jsonfile:
        json.dump(products, jsonfile, ensure_ascii=False, indent=4)

    print(f"{output_filename} 파일이 생성되었습니다.")
