# FRONTEND_STRUCTURE.md

이 문서는 Flask 기반 웹 서비스의 프론트엔드 디렉터리 구조와 각 구성 요소의 역할을 설명합니다.  
Jinja2 템플릿 기반 구조로, HTML 렌더링 흐름과 정적 자산(css/js/img)을 분리 관리합니다.

---

## 디렉터리 구조

```
frontend/
├─ templates/
│  ├─ base.html        # 공통 레이아웃 템플릿
│  └─ index.html       # 이상형 입력 폼 화면
│
└─ static/
   ├─ css/
   │  └─ style.css      # 전체 스타일 정의
   ├─ js/
   │  ├─ main.js        # 입력 처리 및 페이지 동작
   │  └─ api.js         # API 통신 래퍼
   └─ img/
      └─ logo.png       # 정적 이미지 리소스
```

---

## 구성 요소 설명

| 경로 | 역할 |
|------|------|
| `templates/base.html` | 모든 페이지의 공통 레이아웃 (상단, footer 등 포함) |
| `templates/index.html` | 이상형 조건 입력 폼 (base 확장) |
| `static/css/` | 스타일 파일 저장 위치 |
| `static/js/main.js` | 사용자 입력 이벤트 핸들링 등 페이지 스크립트 |
| `static/js/api.js` | 백엔드 API 요청 함수 모듈화 |
| `static/img/` | 결과 이미지 또는 UI용 리소스 저장 |

---

## 템플릿 렌더링 흐름

1. `base.html`: 기본 레이아웃 제공 (`{% block content %}` 포함)
2. `index.html`: 사용자 입력용 (`base.html` 상속)

---

## 향후 확장 시 지침

- 템플릿 기능별 분할 권장 (예: `_form.html`, `_result_card.html`)
- JS는 `api.js`, `ui.js` 등 역할별로 파일 분리
- 공통 CSS는 `style.css` 외 별도 모듈로 확장 가능
- 템플릿에 포함되는 파이썬 변수는 반드시 주석(docstring-style)으로 명시 