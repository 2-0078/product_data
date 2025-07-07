# 실시간 조각 거래 시뮬레이션 스크립트
# 랜덤 사용자가 매도/매수 예약을 생성합니다.

import requests
import json
import random
import time
from config import BASE_URL, JWT_PATH

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_headers(user):
    """API 요청에 필요한 공통 헤더 반환"""
    return {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }

# 진행중인 조각 상품 UUID 목록을 가져오는 함수
def get_piece_product_uuids(user):
    headers = get_headers(user)
    
    res = requests.get(f"{BASE_URL}/product-read-service/api/v1/piece/list", headers=headers)
    res.raise_for_status()
    return res.json()["result"]["pieceProductUuidList"]

# 매도 예약 생성 함수
def create_sell_order(piece_product_uuid, price, quantity, user):
    headers = get_headers(user)
    payload = {
        "pieceProductUuid": piece_product_uuid,
        "registeredPrice": price,
        "desiredQuantity": quantity
    }
    res = requests.post(f"{BASE_URL}/piece-service/api/v1/piece/sell", json=payload, headers=headers)
    res.raise_for_status()
    return res.json()

# 매수 예약 생성 함수
def create_buy_order(piece_product_uuid, price, quantity, user):
    headers = get_headers(user)
    payload = {
        "pieceProductUuid": piece_product_uuid,
        "registeredPrice": price,
        "desiredQuantity": quantity
    }
    res = requests.post(f"{BASE_URL}/piece-service/api/v1/piece/buy", json=payload, headers=headers)
    res.raise_for_status()
    return res.json()

# 시장가 조회 함수
def get_market_price(piece_product_uuid, user):
    headers = get_headers(user)
    try:
        res = requests.get(f"{BASE_URL}/piece-service/api/v1/piece/product/market-price/{piece_product_uuid}", headers=headers)
        res.raise_for_status()
        return res.json()["result"]["marketPrice"]
    except Exception as e:
        print(f"⚠️ 시장가 조회 실패: {e}")
        return 10000  # 기본값 반환

# 상품에 따른 소유자&보유조각 확인 함수
def get_piece_owners(piece_product_uuid, user):
    headers = get_headers(user)
    try:
        res = requests.get(f"{BASE_URL}/piece-service/api/v1/piece/owned/{piece_product_uuid}/list", headers=headers)
        res.raise_for_status()
        return res.json()["result"]
    except Exception as e:
        print(f"⚠️ 소유자 목록 조회 실패: {e}")
        return []

# 호가 단위 계산 함수
def get_tick_size(price):
    if price < 1_000:
        return 1
    elif price < 5_000:
        return 5
    elif price < 10_000:
        return 10
    elif price < 50_000:
        return 50
    elif price < 100_000:
        return 100
    elif price < 500_000:
        return 500
    else:
        return 1_000

# 가격 생성 함수 - 테스트용 로직 적용
def generate_price(market_price, is_sell):
    tick_size = get_tick_size(market_price)
    
    if is_sell:
        # 매도: 아래 호가 3단위 ~ 위 호가 5단위
        step = random.randint(-3, 5)

    else:
        # 매수: 아래 호가 5단위 ~ 위 호가 3단위
        step = random.randint(-5, 3)

    price = market_price + (step * tick_size)
    price = 1 if price < 1 else price  # 가격이 1 미만이 되지 않도록 보정
    
    return price

# 랜덤 수량 생성 함수
def generate_random_quantity(max_quantity=20):
    return random.randint(1, max_quantity)

# 통합된 거래 시뮬레이션 함수
def simulate_trading(users, piece_product_uuids, mode="time", duration=30, iterations=200):
    """
    조각 거래 시뮬레이션을 실행합니다.
    
    매개변수:
    - mode: "time" (시간 기준) 또는 "count" (반복 횟수 기준)
    - duration: 시간 기준 모드에서 시뮬레이션 지속 시간(분)
    - iterations: 반복 횟수 기준 모드에서 총 반복 횟수
    """
    
    # 시뮬레이션 초기화
    start_time = time.time()
    end_time = start_time + (duration * 60) if mode == "time" else float('inf')
    order_count = 0
    success_count = 0
    
    # 모드에 따른 메시지 설정
    if mode == "time":
        mode_msg = f"{duration}분간"
    else:
        mode_msg = f"{iterations}회 반복"
    
    print(f"🔥 조각 거래 시뮬레이션 시작 ({mode_msg}, 소유권 확인)")
    print(f"👥 사용자 수: {len(users)}")
    print(f"📦 거래 상품 수: {len(piece_product_uuids)}")
    print("-" * 50)
    
    # 시뮬레이션 실행
    while (mode == "time" and time.time() < end_time) or (mode == "count" and order_count < iterations):
        order_count += 1
        
        try:
            # 랜덤 상품 선택
            # piece_product_uuid = random.choice(product_uuids)
            piece_product_uuid = piece_product_uuids[0]

            # 시장가 조회
            user = random.choice(users)  # 랜덤 사용자 선택
            market_price = get_market_price(piece_product_uuid, user)
            
            # 매도/매수 랜덤 선택
            is_sell = random.choice([True, False])
            
            print(f"[{is_sell}, {order_count}] 📊 시장가 조회 - {user['email'][:10]}... | 상품 UUID: {piece_product_uuid} | 시장가: {market_price:,}원")
            # 항상 소유권 확인 진행
            if is_sell:
                # 모든 소유자 목록 조회 (아무 사용자로 조회)
                any_user = random.choice(users)
                piece_owners = get_piece_owners(piece_product_uuid, any_user)
                
                if not piece_owners:
                    print(f"[{order_count}] ⚠️ 상품 {piece_product_uuid}의 소유자가 없습니다.")
                    continue
                
                # 소유자 중 랜덤 선택
                owner_data = random.choice(piece_owners)
                owner_uuid = owner_data["memberUuid"]
                
                # 소유자 UUID와 일치하는 사용자 찾기
                user = next((u for u in users if u["memberUuid"] == owner_uuid), None)
                
                if not user:
                    print(f"[{order_count}] ⚠️ 소유자 {owner_uuid}와 일치하는 사용자 정보가 없습니다.")
                    continue
                
                max_quantity = owner_data["pieceQuantity"]
                quantity = generate_random_quantity(max_quantity)  # 보유 수량 이하로 랜덤 생성
            
            # 매수인 경우: 아무 사용자나 선택
            else:
                user = random.choice(users)
                quantity = generate_random_quantity()  # 일반 랜덤 수량
            
            # 시장가 조회
            market_price = get_market_price(piece_product_uuid, user)
            print(f"[{order_count}] 📊 시장가 조회 - {user['email'][:10]}... | 상품 UUID: {piece_product_uuid} | 시장가: {market_price:,}원")
            
            # 가격 생성
            price = generate_price(market_price, is_sell)
            tick_size = get_tick_size(market_price)
            
            print(f"[{order_count}] 📈 가격 생성 - {user['email'][:10]}... | 시장가: {market_price:,}원 | 호가단위: {tick_size}원 | 가격: {price:,}원 | 수량: {quantity}/{max_quantity if is_sell else 'N/A'}조각")

            # 주문 생성 및 로그 출력
            if is_sell:
                create_sell_order(piece_product_uuid, price, quantity, user)
                print(f"[{order_count}] 📤 매도 주문 - {user['email'][:10]}... | 시장가: {market_price:,}원 | 호가단위: {tick_size}원 | 가격: {price:,}원 | 수량: {quantity}/{max_quantity}조각")
            else:
                create_buy_order(piece_product_uuid, price, quantity, user)
                print(f"[{order_count}] 📥 매수 주문 - {user['email'][:10]}... | 시장가: {market_price:,}원 | 호가단위: {tick_size}원 | 가격: {price:,}원 | 수량: {quantity}조각")
            
            success_count += 1
            
            # 요청 간격 (0.5~2초)
            time.sleep(random.uniform(1, 1.5))
                
        except Exception as e:
            print(f"[{order_count}] ❌ 주문 실패: {e}")
            break
    
    print("-" * 50)
    print(f"🎉 거래 시뮬레이션 완료! 총 {order_count}개 시도, {success_count}개 성공")

def main():
    users = load_users()
    any_user = random.choice(users)
    
    try:
        # 진행중인 조각 상품 UUID 목록 가져오기
        piece_product_uuids = get_piece_product_uuids(any_user)
        
        if not piece_product_uuids:
            print("❌ 진행중인 조각 상품이 없습니다.")
            return
        
        print(f"📋 진행중인 조각 상품: {len(piece_product_uuids)}개")
        for i, piece_product_uuid in enumerate(piece_product_uuids, 1):
            print(f"  {i}. {piece_product_uuid}")
        
        # 시뮬레이션 모드 선택
        print("\n💻 실행할 시뮬레이션을 선택하세요:")
        print("1. 시간 기준 시뮬레이션 (30분)")
        print("2. 횟수 기준 시뮬레이션 (200회)")
        
        choice = input("\n선택 (1-2, 기본값=2): ").strip() or "2"
        
        if choice == "1":
            # 시간 기준 시뮬레이션
            simulate_trading(users, piece_product_uuids, mode="time", duration=30)
        else:
            # 횟수 기준 시뮬레이션
            simulate_trading(users, piece_product_uuids, mode="count", iterations=200)
            
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")

if __name__ == "__main__":
    main()
