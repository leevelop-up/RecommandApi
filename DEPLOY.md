# Synology NAS Docker 배포 가이드 - RecommandApi

## 프로젝트 개요
RecommandApi는 FastAPI 기반의 주식 데이터 및 추천 API 서버입니다.

## 기능
- RESTful API 제공
- 종목 정보 조회
- AI 추천 결과 제공
- 시장 지수 및 뉴스 데이터

## 시놀로지 NAS 배포

### 방법 1: Docker Compose (권장)

1. **프로젝트를 NAS로 복사**
   ```
   /volume1/docker/RecommandApi/
   ```

2. **SSH로 NAS 접속**
   ```bash
   ssh admin@your-nas-ip
   cd /volume1/docker/RecommandApi
   ```

3. **환경 변수 파일 생성**
   ```bash
   nano .env
   ```
   
   내용:
   ```env
   MARIADB_HOST=mariadb
   MARIADB_PORT=3306
   MARIADB_DATABASE=recommand_stock
   MARIADB_USER=root
   MARIADB_PASSWORD=your_password
   REDIS_HOST=redis
   REDIS_PORT=6379
   ```

4. **Docker Compose로 실행**
   ```bash
   sudo docker-compose up -d --build
   ```

5. **API 접속 확인**
   - `http://your-nas-ip:8000`
   - `http://your-nas-ip:8000/docs` (API 문서)

### 방법 2: 개별 컨테이너 실행

1. **이미지 빌드**
   ```bash
   sudo docker build -t recommandapi:latest .
   ```

2. **컨테이너 실행**
   ```bash
   sudo docker run -d \
     --name recommandapi \
     -p 8000:8000 \
     --env-file .env \
     --network recommand-network \
     recommandapi:latest
   ```

## API 엔드포인트

### 기본 엔드포인트
- `GET /` - API 정보
- `GET /health` - 헬스체크
- `GET /docs` - API 문서 (Swagger UI)
- `GET /redoc` - API 문서 (ReDoc)

### 주식 데이터
- `GET /api/v1/stocks` - 종목 목록
- `GET /api/v1/stocks/{ticker}` - 종목 상세
- `GET /api/v1/market/indices` - 시장 지수

### 추천 및 뉴스
- `GET /api/v1/recommendations` - AI 추천 종목
- `GET /api/v1/news` - 뉴스 목록

## 유용한 명령어

### 로그 확인
```bash
sudo docker logs recommandapi
sudo docker logs -f recommandapi  # 실시간
```

### 컨테이너 재시작
```bash
sudo docker restart recommandapi
```

### 컨테이너 중지
```bash
sudo docker stop recommandapi
```

### API 테스트
```bash
# 헬스체크
curl http://localhost:8000/health

# 종목 목록
curl http://localhost:8000/api/v1/stocks

# 추천 종목
curl http://localhost:8000/api/v1/recommendations
```

## 프론트엔드 연동

RecommandStock 프론트엔드에서 API를 사용하려면:

1. **환경 변수 설정** (RecommandStock/.env)
   ```env
   VITE_API_URL=http://your-nas-ip:8000
   ```

2. **CORS 설정**
   - `main.py`의 `allow_origins`에 프론트엔드 도메인 추가

## 전체 시스템 통합

RecommandAi, RecommandApi, RecommandStock을 함께 실행:

1. **통합 네트워크 생성**
   ```bash
   sudo docker network create recommand-network
   ```

2. **각 서비스 실행**
   ```bash
   # RecommandAi
   cd /volume1/docker/RecommandAi
   sudo docker-compose up -d
   
   # RecommandApi
   cd /volume1/docker/RecommandApi
   sudo docker-compose up -d
   
   # RecommandStock
   cd /volume1/docker/RecommandStock
   sudo docker-compose up -d
   ```

3. **접속**
   - Frontend: `http://your-nas-ip:3000`
   - API: `http://your-nas-ip:8000`
   - API Docs: `http://your-nas-ip:8000/docs`

## 트러블슈팅

### 포트 충돌
```bash
# 다른 포트로 변경
sudo docker run -p 8080:8000 ...
```

### 데이터베이스 연결 실패
- MariaDB 컨테이너가 실행 중인지 확인
- 네트워크 설정 확인

### CORS 오류
- `main.py`의 `allow_origins` 설정 확인

## 개발 모드

로컬 개발 시:
```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
