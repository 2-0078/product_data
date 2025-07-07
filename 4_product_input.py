# 이 스크립트는 converted_products.json 파일을 읽어 상품 데이터를 등록합니다.
# 등록 전, mainCategory와 subCategory가 존재하는지 확인하고 없으면 생성합니다.
# 상품 등록 시 가격 계산, 이미지 목록, AI 설명 등을 자동 생성합니다.
# 모든 등록은 REST API를 통해 서버에 전송됩니다.

# 이후 funding_input.py 스크립트를 사용하여 funding 데이터를 생성합니다.

import requests
import json
import os
import random
import math
from config import BASE_URL, JWT_PATH

DATA_PATH = "./data/converted_products_{}.json"

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

STORAGE_LOCATIONS = ["보관소 1", "보관소 2", "보관소 3"]
AI_DESCRIPTIONS = [
    "최상급 컨디션의 인기 제품입니다.",
    "희소성이 높아 투자 가치가 있습니다.",
    "시간이 지나도 변치 않는 클래식한 디자인입니다.",
    "보관 상태가 우수한 고급 상품입니다.",
    "소장용으로도 적합한 가치 있는 제품입니다."
]

IMAGE_URLS = [
    "https://pieceofcake-server-images.s3.ap-northeast-2.amazonaws.com/uploads/1751007228176-1.PNG",
    "https://pieceofcake-server-images.s3.ap-northeast-2.amazonaws.com/uploads/1751007259479-2.png",
    "https://pieceofcake-server-images.s3.ap-northeast-2.amazonaws.com/uploads/1751007273631-3.png"
]

def truncate_price(value, ratio):
    return int(value * ratio) // 10000 * 10000

def get_main_categories(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/product-service/api/v1/main-category/list", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

def create_main_category(name, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.post(f"{BASE_URL}/product-service/api/v1/main-category", json={"name": name}, headers=headers)
    res.raise_for_status()
    return res.json()["result"]

def get_sub_categories(main_category_id, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/product-service/api/v1/sub-category/list/{main_category_id}", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

def create_sub_category(main_category_id, name, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.post(f"{BASE_URL}/product-service/api/v1/sub-category", json={
        "mainCategoryId": main_category_id,
        "name": name
    }, headers=headers)
    res.raise_for_status()
    return res.json()["result"]

def create_product(product_data, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.post(f"{BASE_URL}/product-service/api/v1/product/no-ai", json=product_data, headers=headers)
    res.raise_for_status()
    return res.json()["result"]

def main():
    users = load_users()
    any_user = random.choice(users)
    
    # 설정 리스트에서 각 제품 카테고리마다 실행
    from config import CRAWLING_ITEMS
    
    all_products = []
    
    for item in CRAWLING_ITEMS:
        product_category = item['PRODUCT']
        current_path = DATA_PATH.format(product_category)
        
        if not os.path.exists(current_path):
            print(f"❌ JSON 파일이 존재하지 않습니다: {current_path}")
            continue

        with open(current_path, "r", encoding="utf-8-sig") as f:
            category_products = json.load(f)
            all_products.extend(category_products)
            print(f"📦 {product_category} 카테고리에서 {len(category_products)}개 상품 로드")
    
    products = all_products

    print(f"📦 총 {len(products)}개 상품 처리 시작")

    main_category_cache = {}
    sub_category_cache = {}

    for idx, product in enumerate(products, start=1):
        try:
            main_name = product["mainCategory"]["categoryName"]
            sub_name = product["subCategory"]["categoryName"]

            # 1. Main Category 확인/생성
            if main_name not in main_category_cache:
                main_cats = get_main_categories(any_user)
                main_cat = next((c for c in main_cats if c["categoryName"] == main_name), None)
                if not main_cat:
                    main_cat = create_main_category(main_name, any_user)
                    main_cat_id = main_cat["id"]
                else:
                    main_cat_id = main_cat["id"]
                main_category_cache[main_name] = main_cat_id
            else:
                main_cat_id = main_category_cache[main_name]

            # 2. Sub Category 확인/생성
            sub_key = (main_name, sub_name)
            if sub_key not in sub_category_cache:
                sub_cats = get_sub_categories(main_cat_id, any_user)
                sub_cat = next((c for c in sub_cats if c["categoryName"] == sub_name), None)
                if not sub_cat:
                    sub_cat = create_sub_category(main_cat_id, sub_name, any_user)
                    sub_cat_id = sub_cat["id"]
                else:
                    sub_cat_id = sub_cat["id"]
                sub_category_cache[sub_key] = sub_cat_id
            else:
                sub_cat_id = sub_category_cache[sub_key]

            # 3. Product 생성
            origin_price = product["purchasePrice"]
            purchase_price = truncate_price(origin_price, 0.5)
            ai_price = truncate_price(origin_price, 0.75)

            # 상품의 profileImageUrlList에서 이미지 사용
            profile_images = product.get("profileImageUrlList", [])
  

            product_payload = {
                "productName": product["productName"],
                "purchasePrice": purchase_price,
                "status": "STORED",
                "storageLocation": product.get("storageLocation", random.choice(STORAGE_LOCATIONS)),
                "description": product["description"],
                "productImageRequestVoList": [
                    {
                        "imageIndex": i,
                        "isThumbnail": (i == 0),  # 첫 번째 이미지만 썸네일
                        "fileName": img_url
                    } for i, img_url in enumerate(profile_images[:2])  # 최대 2개만 사용
                ],
                "mainCategory": {
                    "categoryId": main_cat_id,
                    "categoryName": main_name
                },
                "subCategory": {
                    "categoryId": sub_cat_id,
                    "categoryName": sub_name
                },
                "price": str(ai_price),
                "aiDescription": random.choice(AI_DESCRIPTIONS)
            }

            product_res = create_product(product_payload, any_user)
            # product_id = product_res["productId"]

            print(f"[{idx}] ✅ 등록 완료: {product['productName']}")

        except Exception as e:
            print(f"[{idx}] ❌ 에러: {product.get('productName', 'Unknown')} - {e}")

    print("🎉 전체 상품 등록 완료")

if __name__ == "__main__":
    main()
