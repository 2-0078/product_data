import redis

# Redis 서버에 연결
r = redis.Redis(host='localhost', port=6379, db=0, password='1234')

# 삭제할 키 패턴 지정
pattern = "funding:*"

# 해당 패턴에 맞는 모든 키 검색
keys = r.scan_iter(match=pattern)

# 삭제 진행
deleted = 0
for key in keys:
    r.delete(key)
    deleted += 1
    print(f"Deleted key: {key.decode()}")

print(f"\n총 {deleted}개의 키가 삭제되었습니다.")
