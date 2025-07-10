import json
from pymongo import MongoClient, UpdateOne

# 1. funding_sql.json 파일 읽기
with open('./data/funding_sql.json', 'r', encoding='utf-8') as f:
    product_json_data = json.load(f)

print(f"📦 읽어온 상품 데이터: {len(product_json_data)}개")

# 2. MongoDB 연결
mongo_client = MongoClient('mongodb_address')  # MongoDB 연결

# 먼저 사용 가능한 데이터베이스 목록 확인
db_list = mongo_client.list_database_names()
print(f"🗂️ 사용 가능한 데이터베이스: {db_list}")

# piece_of_cake 데이터베이스 연결
mongo_db = mongo_client['piece_of_cake']
print("✅ 'piece_of_cake' 데이터베이스 연결 완료")

# 컬렉션 목록 확인
collection_names = mongo_db.list_collection_names()
print(f"📋 사용 가능한 컬렉션: {collection_names}")

# product_read 컬렉션 연결
mongo_collection = mongo_db['product_read']

# product_read 컬렉션의 문서 수 확인
doc_count = mongo_collection.count_documents({})
print(f"📊 product_read 컬렉션의 문서 수: {doc_count}개")

# 첫 번째 문서 하나 조회해서 구조 확인
sample_doc = mongo_collection.find_one()
if sample_doc:
    print("🔍 샘플 문서 구조:")
    print(f"   - _id: {sample_doc.get('_id', 'N/A')}")
    print(f"   - productUuid: {sample_doc.get('productUuid', 'N/A')}")
    print(f"   - fundingRead: {sample_doc.get('fundingRead', 'N/A')}")
    if 'fundingRead' in sample_doc and sample_doc['fundingRead']:
        print(f"   - fundingRead.fundingDeadline: {sample_doc['fundingRead'].get('fundingDeadline', 'N/A')}")
    print(f"   - 기타 필드: {list(sample_doc.keys())}")
else:
    print("⚠️ 컬렉션에 문서가 없습니다.")

# funding_deadline 업데이트를 위한 데이터 준비
bulk_ops = []
updated_count = 0

for product_json in product_json_data:
    # productUuid가 있는지 확인
    if 'product_uuid' in product_json:
        product_uuid = product_json['product_uuid']
        
        # JSON에서 fundingDeadline 찾기 (여러 가능한 경로 확인)
        funding_deadline = None
        
        # 가능한 경로들 확인
        if 'funding_deadline' in product_json:
            funding_deadline = product_json['funding_deadline']
        
        if funding_deadline is not None:
            # 문자열인 경우 datetime으로 변환
            if isinstance(funding_deadline, str):
                from datetime import datetime
                try:
                    # SQL 형식: 2025-07-15 03:00:00.000000
                    if '.' in funding_deadline and len(funding_deadline.split('.')[-1]) == 6:
                        # 마이크로초가 있는 경우
                        funding_deadline = datetime.strptime(funding_deadline, '%Y-%m-%d %H:%M:%S.%f')
                    elif ' ' in funding_deadline and 'T' not in funding_deadline:
                        # 일반 SQL 형식: 2025-07-15 03:00:00
                        funding_deadline = datetime.strptime(funding_deadline, '%Y-%m-%d %H:%M:%S')
                    elif 'T' in funding_deadline:
                        # ISO 형식: 2025-08-01T08:31:53.755+00:00
                        funding_deadline = datetime.fromisoformat(funding_deadline.replace('Z', '+00:00'))
                    else:
                        # 날짜만 있는 경우: 2025-07-15
                        funding_deadline = datetime.strptime(funding_deadline, '%Y-%m-%d')
                    
                    print(f"🔄 날짜 변환 성공: {product_json['funding_deadline']} -> {funding_deadline}")
                    
                except ValueError as e:
                    print(f"⚠️ 날짜 형식 변환 실패: {funding_deadline} - {e}")
                    continue
            
            bulk_ops.append(
                UpdateOne(
                    {'productUuid': product_uuid},
                    {'$set': {'fundingRead.fundingDeadline': funding_deadline}},
                    upsert=False  # 문서가 없으면 생성하지 않음
                )
            )
            updated_count += 1
            print(f"✅ 업데이트 준비 [{updated_count}]: {product_uuid[:8]}... -> {funding_deadline}")
        else:
            print(f"⚠️ fundingDeadline 없음: {product_uuid[:8]}... (키: {list(product_json.keys())})")
    else:
        print(f"⚠️ productUuid 없음: {list(product_json.keys())}")

print(f"📝 준비된 업데이트 작업: {len(bulk_ops)}개")

# 4. 일괄 업데이트 실행
if bulk_ops:
    try:
        result = mongo_collection.bulk_write(bulk_ops)
        print("✅ fundingRead.fundingDeadline 업데이트 완료!")
        print(f"   - 수정된 문서: {result.modified_count}개")
        print(f"   - 매칭된 문서: {result.matched_count}개")
        print(f"   - 새로 생성된 문서: {result.upserted_count}개")
    except Exception as e:
        print(f"❌ 업데이트 실패: {e}")
else:
    print("⚠️ 업데이트할 데이터가 없습니다. productUuid와 fundingDeadline이 모두 있는 데이터를 확인해주세요.")

# 5. 연결 종료
mongo_client.close()
print("🔚 MongoDB 연결 종료")
