# 🎂 Piece of Cake - 데이터 입력 자동화

이 프로젝트는 **Piece of Cake** 플랫폼의 데이터베이스에 상품, 펀딩, 조각거래, 투표, 경매 등의 데이터를 자동으로 입력하는 Python 스크립트 모음입니다.

## 📂 프로젝트 구조

```
data_iput/
├── data/                          # 크롤링 데이터 및 크롤링 스크립트
│   ├── 1_kream_product_id_crawler.py    # KREAM 상품 ID 크롤링
│   ├── 2_kream_product_detail_crawler.py # KREAM 상품 상세정보 크롤링
│   ├── 3_product_csv_json.py            # CSV를 JSON으로 변환
│   ├── product_ids_*.txt                # 크롤링된 상품 ID 목록
│   ├── output_*.csv                     # 크롤링된 상품 정보 CSV
│   └── converted_products_*.json        # JSON 변환된 상품 데이터
├── config.py                      # 공통 설정 파일
├── 1_user_input.py               # 사용자 생성
├── 2_login_input.py              # 로그인 및 JWT 토큰 생성
├── 3_money_input.py              # 사용자 계좌 충전
├── 4_product_input.py            # 상품 등록
├── 5_funding_input.py            # 펀딩 생성
├── 6_funding_participant_input.py # 펀딩 참여
├── 7_piece_participant_input.py   # 조각거래 시뮬레이션
├── 8_vote_create.py              # 판매 투표 생성
├── 9_vote_participant.py         # 투표 참여
├── 10_auction_participant_input.py # 경매 참여
└── *_redis_delete.py             # Redis 데이터 삭제 (개발용)
```

## 🚀 실행 순서

### 1단계: 크롤링 데이터 준비 (선택사항)
```bash
# KREAM에서 상품 데이터 크롤링 (이미 준비된 데이터가 있다면 생략 가능)
python data/1_kream_product_id_crawler.py    # 상품 ID 수집
python data/2_kream_product_detail_crawler.py # 상품 상세정보 수집
python data/3_product_csv_json.py            # CSV → JSON 변환
```

### 2단계: 기본 데이터 입력
```bash
python 1_user_input.py    # 가짜 사용자 생성
python 2_login_input.py   # 로그인 및 JWT 토큰 생성
python 3_money_input.py   # 사용자 계좌에 예치금 충전
python 4_product_input.py # 상품 등록 (카테고리 자동 생성)
```

### 3단계: 펀딩 프로세스
```bash
python 5_funding_input.py              # 펀딩 생성
python 6_funding_participant_input.py  # 펀딩 참여
```

**⚠️ 중요 단계**: 펀딩 참여 완료 후 **DB에서 직접 `funding_deadline`을 해당 일의 과거 시간으로 변경**해야 합니다.
```sql
--25년 7월 7일의 경우
UPDATE funding SET funding_deadline = '2025-07-07 00:00:00' WHERE status = 'FUNDING';
```

### 4단계: 조각거래
```bash
python 7_piece_participant_input.py   # 조각거래 시뮬레이션
```

### 5단계: 투표 프로세스
```bash
python 8_vote_create.py        # 판매 투표 생성
python 9_vote_participant.py   # 투표 참여
```

**⚠️ 중요 단계**: 투표 참여 완료 후 **DB에서 직접 `vote.end_date`를 과거 시간으로 변경**해야 합니다.
```sql
UPDATE vote SET end_date = '2024-01-01 00:00:00' WHERE status = 'ONGOING';
```

### 6단계: 경매 프로세스
```bash
python 10_auction_participant_input.py # 경매 참여
```
**⚠️ 중요 단계**: 경매 참여 완료 후 종료를 원하면, **DB에서 직접 `auction.end_date`를 과거 시간으로 변경**한 뒤 auction 서버를 재시작해야 합니다.
- auction의 종료는 taskScheduler를 이용하여 기록하기 때문에, auction이 생성될 때 메모리에 종료일자가 저장되게 됩니다. DB를 직접 변경해도 이 내역은 유지됩니다.
- 서버 재실행 시 auction DB의 해당 내용을 순회하여 taskScheduler에 기록하기 때문에, end_date 변경 후에는 auction 서버를 재시작해야 합니다.

## ⚙️ 설정 변경

### config.py 주요 설정 항목

#### 환경 설정
```python
# 서버 환경 (운영/개발)
BASE_URL = "https://api.pieceofcake.site"  # 운영 서버
# BASE_URL = "http://localhost:8000"       # 로컬 서버

# 사용자 데이터 파일
USER_PATH = "./users_remote.json"          # 운영 환경
JWT_PATH = "./login_jwt_memberUuid_remote.json"
# USER_PATH = "./users_local.json"         # 로컬 환경
# JWT_PATH = "./login_jwt_memberUuid_local.json"
```

#### 크롤링 설정
```python
CRAWLING_ITEMS = [
    {"PRODUCT": "가방", "URL": "...", "MAIN_CATEGORY": "패션", "SUB_CATEGORY": "명품 가방"},
    {"PRODUCT": "신발", "URL": "...", "MAIN_CATEGORY": "패션", "SUB_CATEGORY": "명품 신발"},
    {"PRODUCT": "시계", "URL": "...", "MAIN_CATEGORY": "시계", "SUB_CATEGORY": "명품 시계"},
    {"PRODUCT": "쥬얼리", "URL": "...", "MAIN_CATEGORY": "쥬얼리", "SUB_CATEGORY": "명품 브랜드 쥬얼리"}
]
```

### 스크립트별 설정 가능 항목

#### 1_user_input.py
- `USER_COUNT`: 생성할 사용자 수 (기본값: 50)
- `BIRTH_START_YEAR`, `BIRTH_END_YEAR`: 출생년도 범위
- `PHONE_PREFIXES`: 전화번호 접두사 목록

#### 3_money_input.py
- `CHARGE_AMOUNT`: 충전 금액 (기본값: 100억원)

#### 4_product_input.py
- `truncate_price()`: 가격 버림 단위 (현재: 10,000원 단위)
- `AI_DESCRIPTIONS`: AI 설명 템플릿 목록
- `STORAGE_LOCATIONS`: 보관소 위치 목록

#### 5_funding_input.py
- `determine_total_pieces()`: 상품 가격에 따른 조각 수 결정 로직

#### 7_piece_participant_input.py
- `SIMULATION_ROUNDS`: 시뮬레이션 라운드 수
- `PRICE_FLUCTUATION_RATE`: 가격 변동률
- `TICK_SIZE`: 호가 단위

#### 8_vote_create.py
- `VOTE_DURATION_DAYS`: 투표 기간 (기본값: 7일)
- `VOTE_TYPES`: 투표 유형 목록

#### 9_vote_participant.py
- `VOTE_RATIO`: 찬반 투표 비율
- `PARTICIPATION_RATE`: 참여율

#### 10_auction_participant_input.py
- `BID_INCREMENT`: 입찰 증가 단위
- `AUCTION_DURATION`: 경매 기간

## 🔧 개발 도구

### Redis 데이터 삭제 (개발용)
```bash
python funding_redis_delete.py      # 펀딩 관련 Redis 데이터 삭제
python order_piece_redis_delete.py  # 조각거래 관련 Redis 데이터 삭제
```

## 📋 주의사항

1. **JWT 토큰 갱신**: JWT 토큰은 하루마다 만료되므로, 날이 바뀌면 `2_login_input.py`를 다시 실행해야 합니다.

2. **DB 직접 수정 필요**: 
   - 펀딩 완료 후 `funding_deadline` 과거 시간으로 변경
   - 투표 완료 후 `vote.end_date` 과거 시간으로 변경
   - 이는 백엔드 스케줄러가 자동으로 다음 단계를 실행하기 위함입니다.

3. **실행 순서 준수**: 각 스크립트는 순서대로 실행해야 하며, 이전 단계가 완료되지 않으면 다음 단계에서 오류가 발생할 수 있습니다.

4. **환경 설정**: 로컬/운영 환경에 맞게 `config.py`의 설정을 변경해야 합니다.

5. **데이터 검증**: 각 단계 완료 후 데이터가 정상적으로 입력되었는지 확인하는 것을 권장합니다.

## 🔍 문제 해결

### 자주 발생하는 오류
- **JWT 토큰 만료**: `2_login_input.py` 재실행
- **상품 데이터 없음**: `data/` 폴더의 JSON 파일 확인
- **API 연결 오류**: `config.py`의 `BASE_URL` 확인
- **DB 연결 오류**: 데이터베이스 서버 상태 확인

### 로그 확인
각 스크립트는 실행 과정에서 상세한 로그를 출력합니다. 오류 발생 시 로그를 확인하여 원인을 파악할 수 있습니다.

---

💡 **팁**: 전체 프로세스를 한 번에 실행하려면 배치 스크립트를 작성하여 순차적으로 실행할 수 있습니다.
