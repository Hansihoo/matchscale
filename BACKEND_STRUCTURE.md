# BACKEND_STRUCTURE.md

이 문서는 Flask 기반 웹 서비스의 백엔드 디렉터리 구조와 각 구성 요소의 역할을 설명합니다.  
모듈화를 통해 LLM이 각 기능과 책임을 쉽게 파악할 수 있도록 구성되어 있습니다.

---

## 디렉터리 구조

```
backend/
├─ app/
│  ├─ __init__.py              # create_app() 정의 및 블루프린트 등록
│  ├─ config.py                # 환경 설정 클래스 (dev/test/prod)
│  ├─ extensions.py            # DB, 캐시 등 확장 기능 초기화
│  ├─ blueprints/              # 기능별 라우터 분리 (Flask Blueprint)
│  │  ├─ core/                 # 홈 및 입력 폼
│  │  │  └─ routes.py
│  │  ├─ stats/                # 확률 계산 API
│  │  │  └─ routes.py
│  │  └─ image/                # 이미지 생성 API
│  │     └─ routes.py
│  ├─ services/                # 핵심 비즈니스 로직 분리
│  │  ├─ stats_service.py
│  │  └─ image_service.py
│  ├─ models/                  # 데이터베이스 모델 정의 (선택적)
│  ├─ utils/                   # 공통 유틸리티 함수
│  └─ data/                    # 인구 통계 JSON 또는 CSV 저장
│
├─ tests/                      # 단위 및 통합 테스트
├─ wsgi.py                     # WSGI 서버 실행용 진입점
└─ README.md                   # 백엔드 개요 문서
```

---

## 구성 요소 설명

| 경로 | 설명 |
|------|------|
| `app/__init__.py` | Flask 앱 생성 및 Blueprint 등록, 템플릿/정적 파일 경로 설정 |
| `app/config.py` | 환경별 설정 클래스 (개발/테스트/운영) |
| `app/extensions.py` | 확장 기능 (DB, Redis 등) 초기화 |
| `blueprints/core/routes.py` | 홈 페이지 및 입력 폼 라우팅 |
| `blueprints/stats/routes.py` | 확률 계산 API |
| `blueprints/image/routes.py` | 이미지 생성 API |
| `services/` | 복잡한 비즈니스 로직 처리 (라우터에서 분리) |
| `models/` | DB 모델 정의 (사용 시) |
| `utils/` | 헬퍼 함수 모음 |
| `data/` | 통계 자료 JSON, CSV 등 저장소 |
| `tests/` | Pytest 기반 테스트 코드 저장소 |
| `wsgi.py` | 배포 시 앱 실행을 위한 진입점 |

---

## Flask 앱 설정

### 템플릿 및 정적 파일 경로
- `app/__init__.py`에서 `frontend/templates`와 `frontend/static` 디렉토리를 Flask 앱의 템플릿/정적 파일 경로로 설정
- 이를 통해 백엔드에서 프론트엔드 리소스에 접근 가능

### 실행 방법
```bash
# 가장 간단한 방법
python backend/wsgi.py

# 환경 변수 설정 후 실행
$env:FLASK_CONFIG="development"
python backend/wsgi.py
```

---

## 개발 및 문서화 지침

- 각 `routes.py`는 기능 단위 Blueprint로 분리
- 모든 함수는 Google 스타일 docstring 포함
- 기능 추가 전 `docs/`에 설계 문서를 먼저 작성
- 비즈니스 로직은 `services/`에서만 정의
- 모든 기능은 최소 1개의 테스트 작성 필수 