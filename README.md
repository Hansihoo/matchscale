# MatchScale

이상형 매칭 확률 계산 및 이미지 생성 웹 서비스

## 프로젝트 개요

MatchScale은 사용자가 입력한 이상형 조건을 바탕으로 매칭 확률을 계산하고 관련 이미지를 생성하는 Flask 기반 웹 서비스입니다.

## 기술 스택

- **Backend**: Flask, Python
- **Frontend**: Jinja2 Templates, HTML/CSS/JavaScript
- **Database**: SQLite (선택적)
- **Testing**: Pytest

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# 개발 환경
export FLASK_ENV=development
export FLASK_APP=backend.wsgi
```

### 3. 서버 실행
```bash
flask run
```

## 프로젝트 구조

```
matchscale/
├─ backend/               # Flask 백엔드
├─ frontend/              # Jinja2 템플릿 + 정적 자원
├─ docs/                  # 문서 모음
├─ tests/                 # 단위 및 통합 테스트
├─ requirements.txt       # Python 의존성
└─ README.md              # 프로젝트 개요
```

## 개발 가이드

- 코드 스타일은 `CODING_RULES.md` 참조
- 프로젝트 구조는 `PROJECT_STRUCTURE.md` 참조
- 변경 이력은 `CHANGELOG.md`에 기록 