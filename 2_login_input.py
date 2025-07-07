# 유저들의 로그인 정보를 json 형태로 저장하는 스크립트입니다.
# 이 스크립트는 users.json 파일에서 이메일을 읽어와 로그인 시도 후 JWT 토큰과 memberUuid를 저장합니다.
# 결과는 jwt_memberUuid.json 파일에 저장됩니다.

import requests
import json
import os
from config import BASE_URL, JWT_PATH, USER_PATH

AUTH_URL = f"{BASE_URL}/auth-service/api/v1/login"

def load_users():
    with open(USER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password})
    res.raise_for_status()
    result = res.json().get("result")
    return {
        "email": email,
        "jwt": result.get("accessToken"),
        "memberUuid": result.get("memberUuid")
    }

def main():
    users = load_users()
    results = []
    failed_count = 0

    for idx, user in enumerate(users, start=1):
        email = user["email"]
        try:
            data = login_user(email, "qwerty123!")
            results.append(data)
            print(f"[{idx}] ✅ 로그인 성공 - {email}")
        except Exception as e:
            print(f"[{idx}] ❌ 로그인 실패 - {email} - {e}")
            failed_count += 1

    # 실패가 한 번이라도 있으면 저장하지 않음
    if failed_count > 0:
        print(f"\n❌ 로그인 실패 {failed_count}건이 발생했습니다. 데이터를 저장하지 않습니다.")
        print(f"📊 총 {len(users)}명 중 {len(results)}명 성공, {failed_count}명 실패")
        return

    # 모든 로그인이 성공한 경우에만 저장
    with open(JWT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"📝 로그인 결과 저장 완료 → {JWT_PATH}")

if __name__ == "__main__":
    main()
