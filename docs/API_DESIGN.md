# API_DESIGN.md

이 문서는 matchscale 프로젝트의 API 설계 명세를 정의합니다.

## API 개요

### 기본 정보
- **Base URL**: `/api`
- **Content-Type**: `application/json`
- **인증**: 현재 미구현 (향후 JWT 토큰 기반 인증 예정)

### 응답 형식
```json
{
    "success": true,
    "message": "처리 완료",
    "data": {},
    "error": null
}
```

## 엔드포인트 목록

### 1. 이상형 조건 제출
- **URL**: `POST /api/submit`
- **설명**: 사용자가 입력한 이상형 조건을 제출하고 확률을 계산
- **요청 본문**:
```json
{
    "age_range": [25, 35],
    "location": "seoul",
    "interests": ["travel", "music", "cooking"],
    "style": "cute",
    "height": "160-170"
}
```
- **응답**:
```json
{
    "success": true,
    "message": "제출 완료",
    "data": {
        "probability": 67.5,
        "rarity_level": "희귀",
        "filters": {...}
    }
}
```

### 2. 확률 계산 (향후 구현)
- **URL**: `POST /api/calculate-probability`
- **설명**: 이상형 조건에 따른 매칭 확률 계산
- **상태**: TODO

### 3. 이미지 생성 (향후 구현)
- **URL**: `POST /api/generate-image`
- **설명**: 이상형 조건에 맞는 프로필 이미지 생성
- **상태**: TODO

### 4. 통계 조회 (향후 구현)
- **URL**: `GET /api/statistics`
- **설명**: 전체 사용자 통계 데이터 조회
- **상태**: TODO

## 데이터 모델

### 이상형 조건 (IdealTypeFilters)
```json
{
    "age_range": [number, number],  // [최소나이, 최대나이]
    "location": string,             // 지역 코드
    "interests": [string],          // 관심사 배열
    "style": string,                // 선호 스타일 (선택)
    "height": string                // 선호 키 (선택)
}
```

### 확률 결과 (ProbabilityResult)
```json
{
    "probability": number,          // 확률 (0-100)
    "rarity_level": string,         // 희귀도 레벨
    "filters": object               // 입력한 필터 조건
}
```

## 에러 처리

### HTTP 상태 코드
- `200`: 성공
- `400`: 잘못된 요청 (입력 데이터 오류)
- `404`: 리소스 없음
- `500`: 서버 내부 오류

### 에러 응답 형식
```json
{
    "success": false,
    "message": "에러 메시지",
    "error": "상세 에러 정보",
    "data": null
}
```

## 향후 확장 계획

1. **인증 시스템**: JWT 토큰 기반 사용자 인증
2. **데이터 저장**: 사용자 입력 데이터 저장 및 분석
3. **실시간 통계**: 실시간 매칭 확률 통계
4. **AI 이미지 생성**: 실제 AI 기반 이미지 생성 API 연동 