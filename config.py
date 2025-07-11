# config.py
# 모든 스크립트에서 사용할 공통 설정

# 크롤링 관련
PRODUCT = "신발"
URL = "https://kream.co.kr/search?tab=products&price=4900000-&keyword=%EC%97%AC%EC%84%B1+%EB%B0%B1&sort=pricepremium"
MAIN_CATEGORY = "패션"
SUB_CATEGORY = "명품 가방"

CRAWLING_ITEMS = [
    {"PRODUCT": "의류", "URL": "https://kream.co.kr/search?tab=products&price=5000000-&keyword=%EC%9D%98%EB%A5%98&sort=pricepremium", "MAIN_CATEGORY": "패션", "SUB_CATEGORY": "명품 의류"},
    {"PRODUCT": "가방", "URL": "https://kream.co.kr/search?tab=products&price=4900000-&keyword=%EC%97%AC%EC%84%B1+%EB%B0%B1&sort=pricepremium", "MAIN_CATEGORY": "패션", "SUB_CATEGORY": "명품 가방"},
    {"PRODUCT": "신발", "URL": "https://kream.co.kr/search?tab=products&price=4000000-&keyword=%EC%9A%B4%EB%8F%99%ED%99%94&sort=pricepremium", "MAIN_CATEGORY": "패션", "SUB_CATEGORY": "명품 신발"},
    {"PRODUCT": "시계", "URL": "https://kream.co.kr/search?tab=products&price=4000000-&keyword=%EC%8B%9C%EA%B3%84&sort=pricepremium", "MAIN_CATEGORY": "시계", "SUB_CATEGORY": "명품 시계"},
    {"PRODUCT": "쥬얼리", "URL": "https://kream.co.kr/search?tab=products&price=4000000-&keyword=%EC%A5%AC%EC%96%BC%EB%A6%AC&sort=pricepremium", "MAIN_CATEGORY": "보석/주얼리", "SUB_CATEGORY": "명품 브랜드 주얼리"}
]

# API 서버 URL
# BASE_URL = "https://api.pieceofcake.site"
BASE_URL = "http://localhost:8000"

# USER_PATH = "./users_remote.json"
USER_PATH = "./users_local.json"
# JWT 파일 경로
# JWT_PATH = "./login_jwt_memberUuid_remote.json"
JWT_PATH = "./login_jwt_memberUuid_local.json"

# 기타 공통 설정
DEFAULT_REQUEST_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 100000