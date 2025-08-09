# 이상형 선택률 계산기 🎯

통계 기반 이상형 선택률 분석 웹 서비스

## 프로젝트 개요

이상형 선택률 계산기는 사용자가 입력한 이상형 조건을 바탕으로 실제 인구 통계를 기반으로 **전체 이성 중 몇 %를 원하는지**를 계산하고, 현실적인 해석과 공유 가능한 이미지를 생성하는 Flask 기반 웹 서비스입니다.

### 핵심 기능

- **통계 기반 선택률 계산**: 실제 인구 비율을 활용한 정확한 선택률 분석
- **다양한 조건 지원**: 키, 학력, 연봉, 직업, 지역, 나이, 흡연 여부 등
- **실시간 피드백**: 조건 선택 시 즉시 비율 정보 표시
- **현실적 해석**: 선택률에 따른 현실적인 조언 제공
- **공유 기능**: 결과 카드 이미지 생성 및 다운로드

## 기술 스택

- **Backend**: Flask, Python
- **Frontend**: Jinja2 Templates, HTML/CSS/JavaScript
- **이미지 처리**: Pillow (PIL)
- **테스트**: Pytest
- **스타일**: 모던 CSS3, 반응형 디자인

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행 (가장 간단한 방법)
```bash
python backend/wsgi.py
```

### 3. 환경 변수 설정 후 실행 (선택사항)
```bash
# Windows PowerShell
$env:FLASK_CONFIG="development"
python backend/wsgi.py

# 또는 Flask 명령어 사용
$env:FLASK_APP="backend.wsgi"
python -m flask run
```

### 4. 웹 브라우저에서 접속
서버가 실행되면 다음 주소로 접속하세요:
- `http://localhost:5000`
- `http://127.0.0.1:5000`

## 사용 방법

1. **이상형 성별 선택**: 분석할 대상의 성별을 선택합니다
2. **조건 입력**: 원하는 이상형 조건들을 선택합니다
   - 키, 학력, 연봉, 직업, 지역, 나이(범위), 흡연 여부
   - 각 조건의 인구 비율이 실시간으로 표시됩니다
3. **선택률 계산**: "선택률 계산하기" 버튼을 클릭합니다
4. **결과 확인**: 전체 이성 중 몇 %를 원하는지 확인합니다
5. **현실적 해석**: 선택률에 따른 현실적인 조언을 받습니다
6. **공유하기**: 결과 카드를 다운로드하거나 공유합니다

## 선택률 등급 시스템

- **극히 드문 조건** (< 0.1%): 로또 당첨보다 어려운 조건
- **매우 드문 조건** (< 1%): 100명 중 1명도 안 되는 비율
- **드문 조건** (< 5%): 20명 중 1명 정도의 비율
- **보통 조건** (< 15%): 7명 중 1명 정도의 비율
- **흔한 조건** (< 30%): 3명 중 1명 정도의 비율
- **매우 흔한 조건** (≥ 30%): 3명 중 1명 이상의 비율

## API 엔드포인트

### 선택률 계산
```
POST /api/calculate
Content-Type: application/json

{
    "gender": "남성",
    "height": "165-170",
    "education": "4년제",
    "salary": "3000-4000만원",
    "age_range": [25, 34]
}
```

### 이미지 생성
```
POST /api/generate-image
Content-Type: application/json

{
    "probability": 12.5,
    "selection_level": "보통 조건",
    "filters": {...}
}
```

### 서비스 상태 확인
```
GET /api/health
```

## 프로젝트 구조

```
matchscale/
├─ backend/               # Flask 백엔드
│  ├─ app/
│  │  ├─ blueprints/      # 라우터 분리
│  │  ├─ services/        # 비즈니스 로직
│  │  └─ config.py        # 환경 설정
│  └─ wsgi.py            # 서버 진입점
├─ frontend/              # 템플릿 및 정적 파일
│  ├─ templates/          # Jinja2 템플릿
│  └─ static/             # CSS, JS, 이미지
├─ tests/                 # 단위 테스트
├─ docs/                  # 문서
└─ requirements.txt       # Python 의존성
```

## 개발 가이드

### 코드 스타일
- Google 스타일 docstring 사용
- 함수 길이 20줄 이내 유지
- snake_case 네이밍 규칙

### 테스트 실행
```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_stats_service.py

# 커버리지 포함 테스트
pytest --cov=app
```

### 디버깅 가이드

#### 백엔드(Flask)

- 개발 모드 실행
  ```powershell
  # Windows PowerShell
  $env:FLASK_CONFIG="development"
  python backend/wsgi.py
  ```
  - 위 설정으로 `DevelopmentConfig`가 적용되어 `DEBUG=True` 및 자동 리로드가 활성화됩니다.

- 런타임 로깅 확인
  - 서버 콘솔에 요청/에러 로그가 출력됩니다.
  - 에러 발생 시 Flask 디버거 페이지에서 스택트레이스를 확인하세요.

- 브레이크포인트 사용
  - 디버그가 필요한 위치에 `breakpoint()`를 추가하고 서버를 실행합니다.
  - 자동 리로드로 프로세스가 2개일 수 있으니, 중단점이 트리거되지 않으면 파일 저장 후 재시도하세요.

- Flask CLI 도구로 인터랙티브 점검
  ```powershell
  $env:FLASK_APP="backend.wsgi"
  python -m flask shell
  ```
  - 예: `from app.services.stats_service import calculate_selection_probability` 로 직접 함수 호출/검증.

#### API 빠른 점검

- PowerShell에서 엔드포인트 호출
  ```powershell
  $body = @{ gender = "남성"; height = "165-170"; education = "4년제"; salary = "3000-4000만원"; age_range = @(25,34) } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/calculate -ContentType "application/json" -Body $body
  ```

#### 프론트엔드

- 브라우저 개발자 도구 활용
  - Network 탭에서 `/api/*` 요청/응답 페이로드를 확인합니다.
  - Console 탭에서 자바스크립트 오류를 확인합니다.

#### 테스트 디버깅

- 실패 테스트만 집중 실행
  ```bash
  pytest -k "stats_service" -vv -s
  ```
- 실패 시 즉시 중단 및 대화형 디버깅
  ```bash
  pytest -x --pdb
  ```

#### 자주 겪는 이슈 점검 포인트

- 현재 작업 디렉터리가 프로젝트 루트(`matchscale/`)인지 확인하세요. 상대 경로로 `frontend/templates` 및 `data/`를 로드합니다.
- 5000 포트 충돌 시 `backend/wsgi.py`의 포트를 변경하거나 `flask run --port=5001`로 실행하세요.
- 의존성 문제는 `pip install -r requirements.txt`로 재설치하세요.

### 새로운 기능 추가
1. `docs/`에 설계 문서 작성
2. `backend/app/services/`에 비즈니스 로직 구현
3. `backend/app/blueprints/`에 API 엔드포인트 추가
4. `tests/`에 테스트 코드 작성
5. `CHANGELOG.md`에 변경 사항 기록

## 문제 해결

### 템플릿을 찾을 수 없는 오류
- 프로젝트 루트 디렉터리에서 실행하고 있는지 확인
- `frontend/templates` 디렉터리가 존재하는지 확인

### 포트 충돌
- 5000번 포트가 사용 중인 경우 `backend/wsgi.py`에서 포트 변경
- 또는 다른 포트로 실행: `flask run --port=5001`

### 모듈을 찾을 수 없는 오류
- 의존성 재설치: `pip install -r requirements.txt`
- 가상환경 사용 권장

### 이미지 생성 오류
- Pillow 라이브러리가 설치되어 있는지 확인
- 시스템 폰트 설정 확인

## 향후 계획

### 1단계: MVP (현재)
- ✅ 기본 선택률 계산 기능
- ✅ 결과 이미지 생성
- ✅ 현실적 해석 시스템

### 2단계: UX 확장
- [ ] 자기 조건 입력 → 현실 속 나의 등급 계산
- [ ] 다양한 현실적 조언 랜덤 출력
- [ ] 결과 카드 커스터마이징

### 3단계: 커뮤니티 기능
- [ ] 조건 유사 사용자 노출
- [ ] 사용자 인증 시스템
- [ ] 허언 탐지/신뢰도 지표

### 4단계: 수익화
- [ ] 광고 삽입
- [ ] 프리미엄 기능
- [ ] 외부 서비스 제휴

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 연락처

프로젝트 링크: [https://github.com/yourusername/matchscale](https://github.com/yourusername/matchscale)

---

**이상형 선택률 계산기** - 당신이 원하는 이상형이 전체 이성 중 몇 %일까요? 🎯✨ 