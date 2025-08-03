# CODING_RULES.md

이 문서는 프로젝트 전반에 적용되는 코드 작성 규칙, 주석 스타일, 문서화 방식 등을 정의합니다.  
LLM 기반 개발을 위한 일관된 코드 스타일과 문맥 유지가 목적입니다.

---

## 1. 함수 작성 규칙

- 하나의 함수는 하나의 책임만 가짐
- 함수 길이는 20줄 이내로 유지
- 순수 함수 성향 유지 (입력 → 출력 명확)

---

## 2. 네이밍 규칙

- 함수, 변수: `snake_case`
- 클래스: `PascalCase`
- 파일/모듈: 기능 중심의 명사 사용 (예: `image_service.py`)
- 폴더: 기능/역할 단위 명사 사용 (예: `blueprints`, `services`)

---

## 3. 문서화(docstring) 규칙

모든 함수와 클래스는 Google 스타일 docstring 사용:

```python
def calculate_rarity(filters: dict) -> float:
    '''
    이상형 조건에 맞는 희귀 확률을 계산합니다.

    Args:
        filters (dict): 이상형 필터 조건

    Returns:
        float: 희귀 확률 (0~100)
    '''
```

- 단순 주석(`#`)보다 docstring 우선 사용
- 함수 인자, 반환값 모두 명시

---

## 4. 코드 주석 규칙

- 의미 없는 주석 금지 (`# 함수 시작`)
- 이유나 목적 위주로 설명 (`# 입력값은 로컬 캐시에서 먼저 조회`)
- 변경 필요성이 예상되는 부분은 `# NOTE:` 또는 `# TODO:` 사용

---

## 5. 커밋 메시지 규칙 (Conventional Commits)

- 형식: `type(scope): description`
- 예시:
  - `feat(stats): 확률 계산 기능 추가`
  - `fix(image): 이미지 크기 오류 수정`
  - `docs(api): API 스펙 문서 추가`

---

## 6. 디렉터리 구조 변경 시

- 구조가 변경되면 반드시 `PROJECT_STRUCTURE.md`, `FRONTEND_STRUCTURE.md`, `BACKEND_STRUCTURE.md` 동기화
- 주요 변경은 `CHANGELOG.md`에 기록 