# funding create 하는 api 입니다.
# 조각 수는 상품 가격에 따라 결정됩니다. determine_total_pieces 함수 확인

import requests
import math
import json
import random
from time import sleep
from config import BASE_URL, JWT_PATH

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
# 전체 product_uuids를 가져오는 함수 (상품 status = STORED)
def get_product_uuids(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/product-service/api/v1/product/list", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

# 상품 상세 정보를 가져오는 함수
def get_product_detail(product_uuid, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/product-read-service/api/v1/product/list/{product_uuid}", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

# 펀딩 데이터를 생성하는 함수
def create_funding(data, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.post(f"{BASE_URL}/funding-service/api/v1/funding", json=data, headers=headers)
    res.raise_for_status()
    return res.json()

# 펀딩 UUID 목록을 가져오는 함수 (status = READY)
def get_funding_uuid_list(user, status="READY"):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    params = {
        "size": 100000
    }
    res = requests.get(f"{BASE_URL}/funding-service/api/v1/funding/all/{status}", headers=headers, params=params)
    res.raise_for_status()

    # content 배열에서 fundingUuid만 추출
    funding_objects = res.json()["result"]["content"]
    return [funding["fundingUuid"] for funding in funding_objects]

# 펀딩 상태를 변경하는 함수 (READY -> FUNDING 등)
def update_funding_status(funding_uuid, funding_status, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    payload = {
        "fundingUuid": funding_uuid,
        "fundingStatus": funding_status
    }
    res = requests.put(f"{BASE_URL}/funding-service/api/v1/funding/status", json=payload, headers=headers)
    res.raise_for_status()
    return res.json()

# 조각 수를 결정하는 함수
# 5,000,000원 미만은 100조각, 5,000,000원 이상 10,000,000원 미만은 500조각,
# 10,000,000원 이상은 1000조각으로 설정합니다.
def determine_total_pieces(amount):
    if amount < 5_000_000:
        return 100
    elif amount < 10_000_000:
        return 500
    else:
        return 1000

# 10원 단위로 버림하는 함수
def truncate_to_ten(amount):
    return math.floor(amount / 10) * 10

def main():
    users = load_users()
    any_user = random.choice(users)
    product_uuids = get_product_uuids(any_user)
    print(f"📦 총 {len(product_uuids)}개 상품에 대해 펀딩 등록 시도")

    # 상품 상세 정보를 저장할 리스트
    product_details = []

    # product_uuids의 요소가 딕셔너리인 경우
    for idx, product in enumerate(product_uuids, start=1):
        product_uuid = product["productUuid"]  # 딕셔너리에서 UUID 추출
        
        try:
            detail = get_product_detail(product_uuid, any_user)
            price = detail["aiEstimatedPrice"]

            # 상품 상세 정보를 리스트에 추가
            product_details.append(detail)

            total_pieces = determine_total_pieces(price)
            piece_price_raw = math.floor(price / total_pieces)
            piece_price = truncate_to_ten(piece_price_raw)  # 10원 단위로 버림

            funding_payload = {
                "productUuid": product_uuid,
                "fundingAmount": price,
                "piecePrice": piece_price,
                "totalPieces": total_pieces
            }

            create_funding(funding_payload, any_user)
            print(f"[{idx}] ✅ 펀딩 등록 성공 - {detail['productName']} (조각당 가격: {piece_price:,}원)")

        except Exception as e:
            print(f"[{idx}] ❌ 펀딩 등록 실패 - UUID: {product_uuid} - {e}")

    print("🎉 펀딩 등록 완료")
    
    sleep(1)  # 잠시 대기 후 펀딩 상태 변경 시작

    # 펀딩 UUID 목록을 가져와서 상태 변경
    try:
        funding_uuid_list = get_funding_uuid_list(any_user)
        print(f"📋 총 {len(funding_uuid_list)}개 펀딩 상태 변경 시도")
        print(funding_uuid_list)
        
        for idx, funding_uuid in enumerate(funding_uuid_list, start=1):
            try:
                # 펀딩 상태를 "FUNDING"로 변경 (필요에 따라 다른 상태로 변경 가능)
                update_funding_status(funding_uuid, "FUNDING", any_user)
                print(f"[{idx}] ✅ 펀딩 상태 변경 성공 - UUID: {funding_uuid}")
                
            except Exception as e:
                print(f"[{idx}] ❌ 펀딩 상태 변경 실패 - UUID: {funding_uuid} - {e}")
        
        print("🎉 펀딩 상태 변경 완료")
        
    except Exception as e:
        print(f"❌ 펀딩 상태 변경 과정에서 오류: {e}")
    
    # 상품 상세 정보를 JSON 파일로 저장
    try:
        with open("product_details.json", "w", encoding="utf-8") as f:
            json.dump(product_details, f, ensure_ascii=False, indent=2)
        print(f"📄 상품 상세 정보 {len(product_details)}개를 product_details.json에 저장했습니다.")
    except Exception as e:
        print(f"❌ JSON 파일 저장 실패: {e}")

if __name__ == "__main__":
    main()
