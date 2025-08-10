# CHANGELOG.md

이 문서는 matchscale 프로젝트의 모든 중요 변경 사항을 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

---

## [Unreleased]

### Added
- 인구가중 미혼률 계산 도입
  - 단일 나이별 인구 × 5세 구간 미혼률을 가중해 마지막 단계에서 적용
  - 결과 스텝 문구 간소화(“미혼률 계산: A% → B%”)
- 희귀이상형 서비스 핵심 기능 구현
  - 통계 기반 확률 계산 서비스 (`StatsService`)
  - 결과 공유용 이미지 생성 서비스 (`ImageService`)
  - 코믹 멘트 시스템
  - 실시간 조건 요약 기능
- API 엔드포인트 추가
  - `POST /api/calculate`: 확률 계산 API
  - `POST /api/generate-image`: 이미지 생성 API
  - `GET /api/statistics`: 통계 요약 API
  - `GET /api/health`: 서비스 상태 확인 API
- 프론트엔드 UI/UX 개선
  - 모던하고 코믹한 디자인 적용
  - 반응형 웹 디자인
  - 실시간 조건 선택 피드백
  - 결과 카드 이미지 생성 및 다운로드
- 테스트 코드 추가
  - 통계 서비스 단위 테스트
  - 다양한 시나리오별 테스트 케이스
- Pillow 라이브러리 의존성 추가 (이미지 처리용)

### Changed
- 연령 구간 비중 계산 분모를 전체 연령 인구로 교정
- 미혼률 적용 순서를 마지막으로 이동
- 프로젝트명을 "MatchScale"에서 "희귀이상형"으로 변경
- 통계 데이터 구조 개선 (더 정확한 인구 비율 적용)
- 확률 계산 로직 개선 (곱셈 원리 기반)
- 희귀도 레벨 분류 체계 개선 (6단계: 극히 희귀 ~ 매우 흔함)
- UI/UX 전면 개편 (히어로 섹션, 애니메이션, 색상 테마)

### Deprecated
- 기존 MatchScale 관련 네이밍 및 구조

### Removed
- 기존 통계 데이터 구조 (새로운 구조로 교체)

### Fixed
- Flask 앱 설정 개선: `frontend/templates`와 `frontend/static` 디렉터리를 템플릿/정적 파일 경로로 설정
- 실행 방법 단순화: `python backend/wsgi.py`로 직접 실행 가능하도록 개선
- 템플릿을 찾을 수 없는 오류 해결
- Flask 앱의 템플릿 경로 설정 문제 수정

### Security
- 환경별 설정 클래스 추가 (개발/테스트/운영)
- 입력 데이터 검증 강화

---

## [0.2.0] - 2024-01-15

### Added
- 희귀이상형 서비스 MVP 기능 완성
- 통계 기반 확률 계산 시스템
- 결과 이미지 생성 기능
- 코믹 멘트 시스템
- 공유 기능

---

## [0.1.0] - 2024-01-01

### Added
- 프로젝트 초기 설정
- 기본 디렉터리 구조 생성
- Flask 백엔드 기본 구조
- Jinja2 템플릿 기반 프론트엔드
- 문서화 시스템 (README, CODING_RULES, PROJECT_STRUCTURE) 