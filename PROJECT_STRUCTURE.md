# PROJECT_STRUCTURE.md

이 문서는 matchscale 프로젝트의 상위 디렉터리 구조와 각 구성의 책임을 설명합니다.  
모듈화, 문서화, 테스트 분리를 통한 LLM 중심 개발을 목표로 합니다.

---

## 최상위 구조

```
matchscale/
├─ backend/               # Flask 백엔드
├─ frontend/              # Jinja2 템플릿 + 정적 자원
├─ docs/                  # 문서 모음
├─ tests/                 # 단위 및 통합 테스트
├─ CHANGELOG.md           # 변경 이력
├─ README.md              # 프로젝트 개요
├─ CODING_RULES.md        # 코드 스타일 및 문서화 규칙
├─ PROJECT_STRUCTURE.md   # 전체 구조 설명
└─ requirements.txt       # Python 의존성
```

---

## 폴더별 역할 요약

| 폴더 | 설명 |
|------|------|
| `backend/` | Flask 앱, 라우트, 서비스, 데이터 로직 포함 |
| `frontend/` | 사용자와 상호작용하는 HTML, CSS, JS, 템플릿 |
| `docs/` | 설계 문서, API 명세, 프롬프트, 구조 등 기술 문서 |
| `tests/` | 기능 단위 테스트 코드 모음 |
| `CHANGELOG.md` | SemVer 기반 변경 이력 문서 |
| `README.md` | 실행법, 소개 등 전체 가이드 |
| `CODING_RULES.md` | 함수/주석/문서화 스타일 명세 |

---

## 문서 기반 개발 흐름

1. 기능 설계 문서를 `docs/`에 작성
2. 구조/로직을 `backend/`, `frontend/`에 구현
3. 각 기능별 테스트 추가
4. 변경 내용은 `CHANGELOG.md`에 기록
5. 문서와 코드가 항상 동기화되도록 유지 