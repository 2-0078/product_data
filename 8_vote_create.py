# Vote 생성 스크립트
# 상품에 대한 판매 투표를 생성합니다.

import requests
import json
import random
from datetime import datetime, timedelta
from config import BASE_URL, JWT_PATH

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# TRADING 상태의 조각 상품 목록 조회 함수
def get_trading_piece_products(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    params = {
        "size": 100000,
        "status": "TRADING"  # TRADING 상태의 상품을 조회 (은서님이 update 후 TRADING으로 변경할 것)
    }
    res = requests.get(f"{BASE_URL}/product-read-service/api/v1/piece/list", headers=headers, params=params)
    res.raise_for_status()
    return res.json()["result"]["pieceProductUuidList"]

# 조각 상품 상세 정보 조회 함수
def get_piece_product_detail(piece_product_uuid, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/product-read-service/api/v1/piece/list/{piece_product_uuid}", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

# Vote 생성 함수
def create_vote(product_uuid, piece_product_uuid, starting_price, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    payload = {
        "productUuid": product_uuid,
        "pieceProductUuid": piece_product_uuid,
        "startingPrice": starting_price,
    }
    res = requests.post(f"{BASE_URL}/auction-service/api/v1/vote", json=payload, headers=headers)
    res.raise_for_status()
    return res.json()

def main():
    users = load_users()
    any_user = random.choice(users)
    
    print("📦 TRADING 상태 조각 상품 목록 조회 중...")
    
    try:
        # TRADING 상태의 조각 상품 목록 조회
        trading_piece_products = get_trading_piece_products(any_user)

        if not trading_piece_products:
            print("❌ TRADING 상태의 조각 상품이 없습니다.")
            return
        
        print(f"🎯 총 TRADING 조각 상품 수: {len(trading_piece_products)}개")
        
        for idx, piece_product_uuid in enumerate(trading_piece_products, start=1):
            try:
                print(f"🔍 [{idx}/{len(trading_piece_products)}] 조각 상품 상세 정보 조회 중... (UUID: {piece_product_uuid})")
                
                # 조각 상품 상세 정보 조회하여 productUuid 획득
                piece_detail = get_piece_product_detail(piece_product_uuid, any_user)
                product_uuid = piece_detail["productUuid"]
                product_name = piece_detail["productName"]
                ai_estimated_price = piece_detail["aiEstimatedPrice"]
                
                # 정적 시작 가격 (AI 추정 가격을 기본값으로 사용, 없으면 기본값)
                starting_price = ai_estimated_price if ai_estimated_price > 0 else 17381000
                
                print(f"📊 투표 생성 시작")
                print(f"📦 상품 UUID: {product_uuid}")
                print(f"🧩 조각 상품 UUID: {piece_product_uuid}")
                print(f"🏷️  상품명: {product_name}")
                print(f"💰 시작 가격: {starting_price:,}원")
                print("-" * 50)
                
                result = create_vote(product_uuid, piece_product_uuid, starting_price, any_user)
                print(f"✅ 투표 생성 성공! 결과: {result}")
                
            except Exception as e:
                print(f"❌ [{idx}] 오류 발생: {e}")
        
        print("🎉 모든 조각 상품에 대해 투표 생성 완료!")
        
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")

if __name__ == "__main__":
    main()
