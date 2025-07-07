# 투표 종료 후 자동으로 auction 생성
# 현재 auction 종류를 조회해서 입찰하는 로직

import requests
import json
import random
import time
from config import BASE_URL, JWT_PATH

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 진행중인 경매 목록 조회 함수
def get_ongoing_auctions(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    params = {"status": "ONGOING"}
    res = requests.get(f"{BASE_URL}/auction-service/api/v1/auction/list", headers=headers, params=params)
    res.raise_for_status()
    return res.json()["result"]

# 경매별 최고 입찰가 조회 함수
def get_auction_highest_price(auction_uuid, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/auction-service/api/v1/auction/highest-price/{auction_uuid}", headers=headers)
    res.raise_for_status()
    return res.json()["highestBidPrice"]

# 입찰 생성 함수
def create_bid(auction_uuid, bid_price, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    payload = {
        "auctionUuid": auction_uuid,
        "bidPrice": bid_price
    }
    res = requests.post(f"{BASE_URL}/auction-service/api/v1/bid", json=payload, headers=headers)
    res.raise_for_status()
    return res.json()  # 응답 메시지를 반환

# 경매별 입찰가 생성 함수 (현재 최고가보다 높은 가격으로 점진적 증가)
def generate_bid_prices(starting_price, num_bids=10):
    """시작가를 기준으로 점진적으로 증가하는 입찰가들을 생성"""
    bid_prices = []
    current_price = starting_price
    
    for i in range(num_bids):
        # 이전 가격보다 1-10% 높게 입찰
        increase_rate = random.uniform(0.01, 0.10)
        current_price = int(current_price * (1 + increase_rate))
        # 1000원 단위로 반올림
        current_price = (current_price // 1000) * 1000
        bid_prices.append(current_price)
    
    return bid_prices

def main():
    users = load_users()
    any_user = random.choice(users)
    
    try:
        # 1. 진행중인 경매 목록 조회
        ongoing_auctions = get_ongoing_auctions(any_user)
        
        if not ongoing_auctions:
            print("❌ 진행중인 경매가 없습니다.")
            return
        
        print(f"🏆 진행중인 경매: {len(ongoing_auctions)}개")
        print("-" * 50)
        
        for auction_idx, auction in enumerate(ongoing_auctions, start=1):
            auction_uuid = auction["auctionUuid"]
            product_uuid = auction["productUuid"]
            
            print(f"[경매 {auction_idx}] 🎯 경매 UUID: {auction_uuid}")
            print(f"[경매 {auction_idx}] 📦 상품 UUID: {product_uuid}")
            
            try:
                # 현재 최고 입찰가 조회
                highest_bid_price = get_auction_highest_price(auction_uuid, any_user)
                # 시작가 설정 (최고가가 0이면 기본값 사용)
                starting_price = highest_bid_price
                
                print(f"[경매 {auction_idx}] 💰 현재 최고가: {highest_bid_price:,}원")
                print(f"[경매 {auction_idx}] 🎯 시작 입찰가: {starting_price:,}원")
                
            except Exception as e:
                print(f"[경매 {auction_idx}] ⚠️  최고가 조회 실패, 기본값 사용: {e}")
                print(f"[경매 {auction_idx}] 💰 기본 시작가: {starting_price:,}원")
            
            # 경매당 10개의 입찰가 생성
            bid_prices = generate_bid_prices(starting_price, 10)
            
            print(f"[경매 {auction_idx}] 👥 입찰자 수: {len(bid_prices)}명")
            
            # 각 입찰가에 대해 랜덤 사용자가 입찰
            for bid_idx, bid_price in enumerate(bid_prices, start=1):
                try:
                    # 랜덤 사용자 선택
                    bidder = random.choice(users)
                    
                    # 입찰 생성
                    bid_response = create_bid(auction_uuid, bid_price, bidder)
                    
                    print(f"[경매 {auction_idx}][입찰 {bid_idx}] 💵 입찰 완료 - {bidder['email'][:15]}... | 입찰가: {bid_price:,}원")
                    print(f"[경매 {auction_idx}][입찰 {bid_idx}] 📩 응답 메시지: {bid_response}")
                    
                    # 요청 간격 (0.5~2초)
                    time.sleep(random.uniform(0.5, 2))
                    
                except Exception as e:
                    print(f"[경매 {auction_idx}][입찰 {bid_idx}] ❌ 입찰 실패 - {bidder['memberUuid'][:15]}... | 입찰가: {bid_price:,}원: {e}")

            print(f"[경매 {auction_idx}] ✅ 경매 입찰 완료")
            print(f"[경매 {auction_idx}] 🏁 최종 최고가: {max(bid_prices):,}원")
            print("-" * 30)
        
        print("🎉 모든 경매 입찰 완료!")
        
    except Exception as e:
        print(f"❌ 경매 목록 조회 실패: {e}")

if __name__ == "__main__":
    main()

