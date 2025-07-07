import json
import requests
import random
import time
from config import BASE_URL, JWT_PATH

FUNDING_LIST_URL = f"{BASE_URL}/funding-service/api/v1/funding/all/FUNDING"
PARTICIPATE_URL = f"{BASE_URL}/funding-service/api/v1/participation"

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_funding_list(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }
    params = {
        "size": 100000
    }
    res = requests.get(FUNDING_LIST_URL, headers=headers, params=params)
    res.raise_for_status()
    
    # content 배열에서 fundingUuid만 추출
    funding_objects = res.json()["result"]["content"]
    return [funding["fundingUuid"] for funding in funding_objects]

def participate(funding_uuid, user, quantity):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }

    payload = {
        "fundingUuid": funding_uuid,
        "memberUuid": user["memberUuid"],
        "quantity": quantity
    }

    res = requests.post(PARTICIPATE_URL, json=payload, headers=headers)
    return res

def main():
    users = load_users()
    any_user = random.choice(users)
    fundings = get_funding_list(any_user)

    funding_done = set()
    target_done_count = 10
    attempt_limit = 10000

    print(f"👥 유저 수: {len(users)} / 🎯 전체 공모 수: {len(fundings)}")

    for attempt in range(attempt_limit):
        user = random.choice(users)
        funding_uuid = random.choice(fundings)
        
        quantity = random.randint(1, 200)

        if funding_uuid in funding_done:
            continue

        try:
            res = participate(funding_uuid, user, quantity)
            if res.status_code == 200:
                print(f"[{attempt+1}] ✅ 참여 성공: {user['email']} → {funding_uuid} ({quantity}조각)")
            elif "잔여 조각이 없습니다" in res.text:
                print(f"[{attempt+1}] 🧯 공모 완료: {funding_uuid}")
                funding_done.add(funding_uuid)
            else:
                print(f"[{attempt+1}] ⚠️ 참여 실패: {res.status_code} - {res.text}")

        except Exception as e:
            print(f"[{attempt+1}] ❌ 예외 발생 - {e}")

        if len(funding_done) >= target_done_count:
            print("🎉 목표 완료! 공모 완료된 수:", len(funding_done))
            break

        # 너무 빠른 요청 방지
        time.sleep(0.1)

    print(f"📝 총 시도 횟수: {attempt+1}, 공모 완료 수: {len(funding_done)}")

if __name__ == "__main__":
    main()
