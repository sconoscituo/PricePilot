# PricePilot
> 쿠팡/네이버쇼핑 최저가 자동 추적 + 가격 알림 SaaS

## 개요

PricePilot은 온라인 쇼핑 상품의 가격을 자동으로 추적하고, 목표 가격 도달 시 사용자에게 알림을 발송하는 서비스입니다.
Gemini API를 활용해 상품 정보를 분석하고, APScheduler로 1시간마다 가격을 자동 갱신합니다.

**수익 구조**: 무료 플랜(상품 5개 추적) / 프리미엄 플랜 월 구독(무제한 추적 + 즉시 알림)

## 기술 스택

- **Backend**: FastAPI 0.104, Python 3.11
- **DB**: SQLAlchemy 2.0 (async) + SQLite (aiosqlite)
- **AI**: Google Gemini API
- **스케줄러**: APScheduler 3.10
- **스크래핑**: httpx, BeautifulSoup4
- **인증**: JWT (python-jose) + bcrypt
- **배포**: Docker + docker-compose

## 시작하기

### 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값을 설정합니다:

| 변수명 | 설명 |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `DATABASE_URL` | SQLite DB 경로 (기본값 사용 가능) |
| `SECRET_KEY` | JWT 서명용 시크릿 키 |
| `COUPANG_ACCESS_KEY` | 쿠팡 파트너스 Access Key |
| `COUPANG_SECRET_KEY` | 쿠팡 파트너스 Secret Key |
| `DEBUG` | 개발 환경 여부 (True/False) |

### 실행 방법

#### Docker (권장)

```bash
docker-compose up -d
```

#### 직접 실행

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

서버 실행 후 http://localhost:8000/docs 에서 API 문서를 확인하세요.

## API 문서

| 메서드 | 엔드포인트 | 설명 |
|---|---|---|
| GET | `/` | 헬스체크 |
| GET | `/health` | 서버 상태 확인 |
| POST | `/users/register` | 회원가입 |
| POST | `/users/login` | 로그인 (JWT 발급) |
| GET | `/users/me` | 내 정보 조회 |
| POST | `/products/` | 상품 추적 등록 |
| GET | `/products/` | 추적 중인 상품 목록 |
| GET | `/products/{id}` | 상품 상세 조회 |
| DELETE | `/products/{id}` | 상품 추적 해제 |
| PUT | `/products/{id}/alert` | 목표 가격 알림 설정 |

## 수익 구조

- **무료 플랜**: 상품 5개까지 추적, 가격 갱신 1시간 간격
- **프리미엄 플랜** (월 4,900원): 상품 무제한 추적, 실시간 가격 알림, 가격 히스토리 조회
- **쿠팡 파트너스**: 상품 링크 클릭 시 수수료 수익

## 라이선스

MIT
