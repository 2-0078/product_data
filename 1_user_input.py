from faker import Faker
import requests
import random
from datetime import datetime
import time
import re
import json
from config import BASE_URL, USER_PATH, JWT_PATH

faker = Faker('ko_KR')  # 한국어 환경

API_URL = f"{BASE_URL}/auth-service/api/v1/signup"
GENDERS = ["남성", "여성"]

all_users = []

# 중복 방지용 집합
used_emails = set()
used_nicknames = set()
used_phones = set()

def generate_unique_phone():
    while True:
        number = f"010{random.randint(10000000, 99999999)}"
        if number not in used_phones:
            used_phones.add(number)
            return number

def generate_clean_nickname():
    while True:
        raw_nick = faker.user_name()
        # 1. 특수문자 제거 (영문자, 숫자, 한글만 허용)
        cleaned = re.sub(r'[^a-zA-Z0-9가-힣]', '', raw_nick)
        # 2. 길이 제한 (2~10자)
        if 2 <= len(cleaned) <= 10 and cleaned not in used_nicknames:
            used_nicknames.add(cleaned)
            return cleaned

def generate_unique_user():
    while True:
        email = faker.unique.email()
        if email not in used_emails:
            used_emails.add(email)
            break

    phone = generate_unique_phone()
    nickname = generate_clean_nickname()
    birth_date = faker.date_of_birth(minimum_age=20, maximum_age=40)

    return {
        "email": email,
        "password": "qwerty123!",
        "name": faker.name(),
        "phoneNumber": phone,
        "birthdate": birth_date.strftime("%Y-%m-%dT00:00:00"),
        "nickname": nickname,
        "gender": random.choice(GENDERS)
    }

success = 0
fail = 0

for i in range(10):
    user_data = generate_unique_user()

    try:
        response = requests.post(API_URL, json=user_data)

        if response.status_code in [200, 201]:
            print(f"[{i+1}/100] ✅ Success: {user_data['nickname']} ({user_data['email']})")
            all_users.append(user_data)
            success += 1
        else:
            print(f"[{i+1}/100] ❌ Fail ({response.status_code}): {response.text}")
            fail += 1
    except Exception as e:
        print(f"[{i+1}/100] ❌ Exception: {e}")
        fail += 1

with open(USER_PATH, "w", encoding="utf-8") as f:
    json.dump(all_users, f, ensure_ascii=False, indent=2)

print(f"\n🎉 완료! 성공: {success}, 실패: {fail}")
