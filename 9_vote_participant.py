# Vote 참가 스크립트
# 투표 목록을 조회하고, 각 상품의 조각 소유자들이 찬반 투표를 진행합니다.

import requests
import json
import random
import time
from config import BASE_URL, JWT_PATH

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Vote 목록 조회 함수
def get_vote_list(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/auction-service/api/v1/vote/list", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

# 조각 소유자 목록 조회 함수
def get_piece_owners(piece_product_uuid, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    res = requests.get(f"{BASE_URL}/piece-service/api/v1/piece/owned/{piece_product_uuid}/list", headers=headers)
    res.raise_for_status()
    return res.json()["result"]

# 투표 참여 함수
def participate_vote(vote_uuid, vote_choice, user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    payload = {
        "voteUuid": vote_uuid,
        "voteChoice": vote_choice
    }
    res = requests.post(f"{BASE_URL}/auction-service/api/v1/vote/detail", json=payload, headers=headers)
    res.raise_for_status()
    return res.json()

# 사용자 UUID로 사용자 정보 찾기
def find_user_by_uuid(users, member_uuid):
    return next((user for user in users if user["memberUuid"] == member_uuid), None)

def main():
    users = load_users()
    any_user = random.choice(users)
    
    try:
        # 1. 투표 목록 조회
        vote_list = get_vote_list(any_user)
        
        if not vote_list:
            print("❌ 진행중인 투표가 없습니다.")
            return
        
        print(f"📊 진행중인 투표: {len(vote_list)}개")
        print("-" * 50)
        
        for vote_idx, vote in enumerate(vote_list, start=1):
            vote_uuid = vote["voteUuid"]
            piece_product_uuid = vote.get("pieceProductUuid", "Unknown")
            product_uuid = vote.get("productUuid", "Unknown")
            
            print(f"[투표 {vote_idx}] 🗳️  투표 UUID: {vote_uuid}")
            print(f"[투표 {vote_idx}] 📦 상품 UUID: {product_uuid}")
            print(f"[투표 {vote_idx}] 🧩 조각 상품 UUID: {piece_product_uuid}")
            
            try:
                # 2. 해당 조각 상품의 소유자 목록 조회
                piece_owners = get_piece_owners(piece_product_uuid, any_user)
                
                if not piece_owners:
                    print(f"[투표 {vote_idx}] ⚠️  조각 소유자가 없습니다.")
                    continue
                
                print(f"[투표 {vote_idx}] 👥 조각 소유자: {len(piece_owners)}명")
                
                # 3. 각 소유자가 투표 참여
                for owner_idx, owner in enumerate(piece_owners, start=1):
                    member_uuid = owner["memberUuid"]
                    piece_quantity = owner["pieceQuantity"]
                    
                    # 해당 memberUuid로 사용자 정보 찾기
                    owner_user = find_user_by_uuid(users, member_uuid)
                    
                    if not owner_user:
                        print(f"[투표 {vote_idx}][소유자 {owner_idx}] ⚠️  사용자 정보를 찾을 수 없습니다: {member_uuid}")
                        continue
                    
                    try:
                        # 랜덤 투표 선택 (70% 찬성, 30% 반대)
                        vote_choice = "AGREE" if random.random() < 0.7 else "DISAGREE"
                        
                        participate_vote(vote_uuid, vote_choice, owner_user)
                        
                        choice_emoji = "👍" if vote_choice == "AGREE" else "👎"
                        print(f"[투표 {vote_idx}][소유자 {owner_idx}] {choice_emoji} 투표 완료 - {owner_user.get('email', member_uuid)[:15]}... | 보유: {piece_quantity}조각 | 선택: {vote_choice}")
                                                
                    except Exception as e:
                        print(f"[투표 {vote_idx}][소유자 {owner_idx}] ❌ 투표 실패 - {member_uuid}: {e}")
                
                print(f"[투표 {vote_idx}] ✅ 투표 완료")
                print("-" * 30)
                
            except Exception as e:
                print(f"[투표 {vote_idx}] ❌ 조각 소유자 조회 실패: {e}")
        
        print("🎉 모든 투표 참여 완료!")
        
    except Exception as e:
        print(f"❌ 투표 목록 조회 실패: {e}")

if __name__ == "__main__":
    main()
