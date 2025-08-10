# 조건별 계산 정책과 코드 매핑

본 문서는 각 조건(키, 학력, 연봉, 직업, 지역, 나이, 흡연, 외모)에 대한 확률 계산 정책과 실제 코드 구현 위치를 정리합니다. 핵심 로직은 `backend/app/services/stats_service.py`에 있습니다.

## 전체 흐름 요약
- 입력 필터를 받아 개별 조건 확률을 계산한 뒤 곱셈 원리로 결합
- 상관관계 보정(학력↔연봉, 학력↔직업, 지역↔직업, 나이↔연봉)을 개별 조건 확률 벡터에 적용
- 나이와 미혼률은 분리 적용
  - 나이: 연령 구간 비중 = 선택 연령(단일 나이 합) / 전체 연령(단일 나이 합)
  - 미혼률: 마지막 단계에서 인구가중 미혼률 = Σ(pop[a]×미혼률[band(a)]) / Σ(pop[a])
- 최종 확률을 퍼센트(0–100)로 변환
- 화면 스텝은 간단한 라벨로 표기: “연령 구간 비중 …”, “미혼률 계산 …”

관련 진입점:
- 함수: `calculate_probability(filters: Dict) -> Dict`
- 파일: `backend/app/services/stats_service.py`

---

## 데이터 로딩
- 함수: `_load_statistics_data()`
- 주요 산출
  - `height`: 키 구간→비율
  - `salary`: 연봉 구간→비율
  - `job`: 직업 카테고리→비율
  - `location`: 지역(시·도)→점유율(0~1)
  - `marital_status`: 연령대(5세)→성별 미혼률(0~1)
  - `smoking`: 성별 흡연률(0~1)
  - `population_latest`: 전국/지역 총·남·여 인구
  - `age_population`: 단일 나이→{남성, 여성} 인구
- 소스 CSV(대표)
  - 키: `Height_Distribution__English_Headers_.csv`, `women_Combined_Female_Height_Distribution__20_49.csv`, `men_Percentile_Verification.csv`
  - 연봉: `Income_Distribution_by_Gender__2024_.csv`, (선택) `연봉_구간.csv`
  - 직업: `Occupation_Distribution.csv`
  - 지역 인구: `regional_population_statistics_2025.csv` (우선), 폴백: `Region_population_shares__2025-07__MOIS_.csv`
  - 미혼률: `unmarried_rate_by_age.csv`
  - 흡연률: `smokingRate.csv`
  - 연령 인구: `population_by_age_2025.csv` 또는 `male_population_by_age_korea.csv` + `female_population_by_age_korea.csv`

---

## 조건별 계산 정책

### 키(height)
- 단일 구간: `statistics_data["height"][height_key]`
- 범위(min–max): `_aggregate_height_probability(cm_min, cm_max)`
  - 데이터 구간과 겹치는 비율 합산
  - 상단 꼬리(≥185cm)는 남성 CDF 포인트로 보강: `_estimate_male_cdf_above(cm)`
- 코드: `_aggregate_height_probability`, `_estimate_male_cdf_above`, `_load_male_height_cdf`

### 학력(education)
- 단일: `statistics_data["education"][education]`
- 다중(최소 학력 이상): 선택 레벨들의 비율 합산(상한 1.0)
- 코드: `calculate_probability()` 내 학력 처리 분기

### 연봉(salary)
- 단일: `statistics_data["salary"][salary_key]`
- 범위(min–max): `_aggregate_salary_probability(amount_min, amount_max)`
  - 1억 경계 교차 시 상위 퍼센트 테이블 기반 근사 혼합
  - (선택) 상위 퍼센트 보간: `_estimate_share_above_income(min_manwon)`
- 코드: `_aggregate_salary_probability`, `_estimate_share_above_income`

### 직업(job)
- 단일: `statistics_data["job"][job_key]`
- 다중: 선택 카테고리 비율 합(상한 1.0)
- 코드: `calculate_probability()` 내 직업 처리 분기

### 지역(location/regions)
- 다중 지역: `statistics_data["location"][region]` 점유율 합(상한 1.0)
- 코드: `calculate_probability()` 내 지역 처리, 로딩은 `_load_region_shares_from_population_csv`

### 나이(age/age_range)
- 연령 구간 비중(미혼률 미적용)
  - 분모: `age_population`의 전체 연령(단일 나이) 합(선택 성별)
  - 분자: 선택 구간 단일 나이 합(선택 성별)
  - 결과는 나이 스텝 확률로 포함
- 미혼률(마지막 단계)
  - 인구가중 미혼률 = `Σ(pop[a] × unmarried_rate[band(a)]) / Σ(pop[a])`
  - 5세 구간 키 매핑: `_get_unmarried_band_key(age)`
  - 구현: `_compute_population_weighted_unmarried_rate(gender, age_low, age_high)`
  - 결과는 “미혼률 계산” 스텝으로 마지막 곱에 반영
- 코드: `calculate_probability()` 내 나이 처리, `_compute_population_weighted_unmarried_rate`, `_get_unmarried_band_key`

### 흡연(smoking)
- 체크 시 비흡연만 허용: `non_smoking = 1 - smoking_rate[gender]`
- 코드: `_process_smoking_data`, `calculate_probability()` 내 흡연 처리

### 외모(appearance_top_percent)
- 단일: 상위 X% 이상 → `X / 100`
- 범위(A–B%): `(B - A) / 100`
- 코드: `calculate_probability()` 내 외모 처리 분기

---

## 상관관계 보정
- 함수: `_apply_correlation_adjustment(probabilities, filters)`
- 시점: 개별 조건 확률 수집 후, 미혼률 곱하기 전 벡터에 적용
- 대상 및 방식
  - 학력↔연봉, 학력↔직업, 지역↔직업, 나이↔연봉
  - 보정: `conditional_prob / marginal_prob` 스케일, (0.1 ~ 3.0)로 클램프

---

## 최종 확률 및 단계 표시
- 결합: (보정된 개별 조건 곱) × (연령 구간 비중) × (미혼률)
- 퍼센트 변환: `final_probability *= 100`
- 단계 표시: `_build_explanation_steps()`가 from/to 퍼센트 및 인원 변화 출력
  - 예: “연령 구간 비중 (25–34세): 100.00% → 14.75%”
  - 예: “미혼률 계산: 14.75% → 14.23%”

---

## 모수(대상 인구) 산정
- 함수: `_resolve_target_population(filters)`
- 지역 선택이 있으면 선택 지역 합, 없으면 전국
- 성별 선택 시 해당 성별 인구 사용

---

## 주의 및 한계
- 미혼률 데이터(5세 구간)는 45–49까지만 있을 수 있음 → 상한 외삽(45–49 사용)
- 지역×나이×성별 미혼 “비중” 데이터가 없으므로, 지역 차이는 현재 결과 모수와 다른 조건들로 간접 반영
- 상관관계 보정은 경험적 계수 → 실제 데이터 확보 시 업데이트 권장

---

## 테스트 포인트
- 연령 구간 비중: CSV의 단일 나이 ‘비율’ 합과 일치 (`tests/test_age_population_share.py`)
- 미혼률: 단일 나이 인구×연령대 미혼률 가중 평균이 마지막 단계에 반영되는지 확인
- 상관관계: 보정 전/후 벡터 비교로 특정 항만 스케일되는지 확인
