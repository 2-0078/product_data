# fake user 들에게 100억씩 충전하는 스크립트입니다.
# 이 스크립트는 JWT 토큰을 줘서 gateway 통해 충전합니다.
# JWT는 하루마다 갱신되므로, 날이 바뀌면 login_input.py 스크립트를 통해 갱신해야 합니다.
import json
import requests
from config import BASE_URL, JWT_PATH

CHARGE_URL = f"{BASE_URL}/payment-service/api/v1/money"

def load_users():
    with open(JWT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def charge_user(user):
    headers = {
        "Authorization": f"Bearer {user['jwt']}",
        "X-Member-Uuid": user["memberUuid"]
    }

    payload = {
        "amount": 100_000_000_000,
        "isPositive": True,
        "historyType": "DEPOSIT",
        "historyDetail": "fake data 입금",
    }

    res = requests.post(CHARGE_URL, json=payload, headers=headers)
    res.raise_for_status()
    return res.status_code

def main():
    users = load_users()
    print(f"💰 총 {len(users)}명에게 충전 시작")

    for idx, user in enumerate(users, start=1):
        try:
            status = charge_user(user)
            print(f"[{idx}] ✅ 충전 성공 - {user['email']}")
        except Exception as e:
            print(f"[{idx}] ❌ 충전 실패 - {user['email']} - {e}")

    print("🎉 전체 충전 완료")

if __name__ == "__main__":
    main()
