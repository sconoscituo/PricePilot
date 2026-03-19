# PricePilot - 프로젝트 설정 가이드

## 프로젝트 소개

PricePilot은 Google Gemini AI와 쿠팡파트너스 API를 활용하여 상품 가격을 추적하고, 최저가 알림 및 가격 분석 리포트를 제공하는 SaaS 서비스입니다. APScheduler로 주기적인 가격 수집을 자동화합니다.

- **기술 스택**: FastAPI, SQLAlchemy, Alembic, SQLite, Google Gemini AI, APScheduler
- **인증**: JWT 24시간 만료
- **외부 API**: Gemini AI, 쿠팡파트너스

---

## 필요한 API 키 / 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | JWT 서명용 비밀 키 | 직접 생성 (`openssl rand -hex 32`) |
| `COUPANG_ACCESS_KEY` | 쿠팡파트너스 액세스 키 | [https://partners.coupang.com](https://partners.coupang.com) > API 관리 |
| `COUPANG_SECRET_KEY` | 쿠팡파트너스 시크릿 키 | [https://partners.coupang.com](https://partners.coupang.com) > API 관리 |
| `DATABASE_URL` | DB 연결 URL (기본: SQLite) | - |
| `DEBUG` | 디버그 모드 (기본: `true`) | - |

---

## GitHub Secrets 설정 방법

저장소의 **Settings > Secrets and variables > Actions** 에서 아래 Secrets를 등록합니다.

```
GEMINI_API_KEY        = <Google AI Studio에서 발급한 키>
SECRET_KEY            = <openssl rand -hex 32 으로 생성한 값>
COUPANG_ACCESS_KEY    = <쿠팡파트너스 액세스 키>
COUPANG_SECRET_KEY    = <쿠팡파트너스 시크릿 키>
```

---

## 로컬 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/sconoscituo/PricePilot.git
cd PricePilot
```

### 2. Python 가상환경 생성 및 의존성 설치

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
COUPANG_ACCESS_KEY=your_coupang_access_key_here
COUPANG_SECRET_KEY=your_coupang_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./pricepilot.db
DEBUG=true
```

### 4. DB 마이그레이션 (Alembic)

```bash
alembic upgrade head
```

---

## 실행 방법

### 로컬 실행 (uvicorn)

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker Compose로 실행

```bash
docker-compose up --build
```

### 테스트 실행

```bash
pytest tests/
```
