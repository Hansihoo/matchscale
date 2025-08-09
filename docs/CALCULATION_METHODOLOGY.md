# 이상형 선택률 계산 방식 및 데이터 요구사항

## 📊 현재 계산 방식 분석

### 🔍 **기존 방식의 문제점**

#### 1. **통계적 독립성 가정의 한계**
```python
# 기존 방식: 단순 곱셈 원리
final_probability = 1.0
for prob in probabilities:
    final_probability *= prob
```

**문제점:**
- 키와 학력, 연봉과 직업 등이 실제로는 상관관계가 있음
- 예: SKY 졸업자는 평균적으로 높은 연봉을 받을 가능성이 높음
- 지역과 직업도 상관관계가 있을 수 있음

#### 2. **데이터 정확성 문제**
- 임시 데이터 사용으로 인한 부정확성
- 실제 통계청 데이터와 차이
- 연령대별 세분화 부족

#### 3. **나이 처리 방식의 문제**
- 단순 나이대별 미혼율 적용
- 성별별 차이 미반영
- 연령대 세분화 부족

## 🚀 개선된 계산 방식

### 1. **실제 데이터 활용**
```python
# 실제 CSV 파일에서 데이터 로드
height_data = pd.read_csv('Height_Distribution__English_Headers_.csv')
unmarried_data = pd.read_csv('unmarried_rate_by_age.csv')
smoking_data = pd.read_csv('smokingRate.csv')
```

### 2. **상관관계 고려**
```python
# 상관관계 조정 함수
def _apply_correlation_adjustment(self, probabilities, filters):
    # 학력-연봉 상관관계
    # 학력-직업 상관관계
    # 지역-직업 상관관계
    # 나이-연봉 상관관계
```

### 3. **성별별 세분화**
```python
# 성별별 미혼율 적용
marital_prob = self.statistics_data["marital_status"][age_key][gender]
```

## 📈 필요한 추가 데이터

### 1. **교육 수준별 분포**
```csv
education_level,percentage
SKY,2.0
인서울,8.0
지거국,15.0
4년제,35.0
이하,40.0
```

**데이터 소스:**
- 통계청 고등교육 통계
- 대학교 졸업자 현황
- 학력별 인구 분포

### 2. **연봉 분포 데이터**
```csv
salary_range,percentage
2000만원 이하,45.0
2000-3000만원,30.0
3000-4000만원,15.0
4000-5000만원,7.0
5000만원 이상,3.0
```

**데이터 소스:**
- 통계청 소득분배지표
- 고용노동부 임금정보시스템
- 연령대별 소득 분포

### 3. **직업 분포 데이터**
```csv
job_category,percentage
전문직,8.0
공무원,5.0
공기업,7.0
그 외,80.0
```

**데이터 소스:**
- 통계청 경제활동인구조사
- 직업별 종사자 현황
- 산업별 고용 현황

### 4. **지역별 인구 분포**
```csv
region,percentage
수도권,50.0
지방광역시,30.0
기타,20.0
```

**데이터 소스:**
- 통계청 주민등록인구현황
- 행정안전부 인구통계
- 지역별 인구 이동 현황

### 5. **상관관계 데이터**
```csv
condition1,condition2,correlation_coefficient
SKY,5000만원 이상,0.8
인서울,전문직,0.5
수도권,전문직,0.6
```

**데이터 소스:**
- 통계청 종합사회조사
- 학력별 소득 분석
- 지역별 직업 분포

## 🧮 계산 공식

### 1. **기본 확률 계산**
```python
# 개별 조건 확률
P(condition_i) = 실제_통계_데이터[condition_i]

# 기본 결합 확률 (독립성 가정)
P(조건1 ∩ 조건2 ∩ ... ∩ 조건n) = ∏ P(조건i)
```

### 2. **상관관계 보정**
```python
# 상관관계가 있는 조건들의 보정
adjusted_prob = original_prob * (1 + correlation_factor * adjustment_weight)

# 예: SKY 졸업자 + 5000만원 이상
# correlation_factor = 0.8, adjustment_weight = 0.3
# adjusted_prob = original_prob * (1 + 0.8 * 0.3) = original_prob * 1.24
```

### 3. **최종 선택률**
```python
final_probability = adjusted_combined_probability * 100
```

## 📊 데이터 품질 기준

### 1. **정확성**
- 통계청 공식 데이터 사용
- 최신 연도 데이터 (2024년 기준)
- 표본 오차 고려

### 2. **일관성**
- 동일한 기준년도 사용
- 동일한 분류 체계 적용
- 단위 통일

### 3. **완전성**
- 모든 조건별 데이터 확보
- 결측치 최소화
- 대체 데이터 준비

## 🔧 구현 개선사항

### 1. **데이터 로딩 최적화**
```python
# 캐싱 적용
@cache.memoize(timeout=3600)
def load_statistics_data():
    # 데이터 로딩 로직
```

### 2. **상관관계 동적 계산**
```python
# 실제 데이터 기반 상관관계 계산
def calculate_correlation_from_data():
    # 실제 데이터셋에서 상관관계 계산
```

### 3. **신뢰구간 제공**
```python
# 계산 결과에 신뢰구간 추가
def calculate_confidence_interval():
    # 표본 오차 고려한 신뢰구간 계산
```

## 📋 우선순위별 데이터 수집 계획

### 🔥 **1순위 (즉시 필요)**
1. **교육 수준별 분포** - 대학 졸업자 통계
2. **연봉 분포** - 소득분배지표
3. **직업 분포** - 경제활동인구조사

### ⚡ **2순위 (1개월 내)**
1. **지역별 인구 분포** - 주민등록인구현황
2. **상관관계 데이터** - 종합사회조사

### 📈 **3순위 (3개월 내)**
1. **신뢰구간 계산** - 표본 오차 분석
2. **동적 상관관계** - 실시간 데이터 연동

## 🎯 예상 효과

### 1. **정확도 향상**
- 실제 데이터 기반으로 20-30% 정확도 향상
- 상관관계 고려로 10-15% 추가 정확도 향상

### 2. **신뢰성 증대**
- 공식 통계 데이터 사용으로 신뢰성 확보
- 계산 과정 투명성 제공

### 3. **사용자 경험 개선**
- 더 현실적인 결과 제공
- 상세한 계산 과정 표시
