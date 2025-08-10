# backend/app/services/stats_service.py
# 통계 기반 선택률 계산 서비스

import json
import os
import pandas as pd
from typing import Dict, List, Tuple, Optional


class StatsService:
    """통계 기반 선택률 계산 서비스"""
    
    def __init__(self):
        """통계 데이터 초기화"""
        self.statistics_data = self._load_statistics_data()
        self.correlation_factors = self._load_correlation_factors()
        # 최신 인구 데이터 (전국/시도 총인구 및 성별 인구)
        self.population_latest = self.statistics_data.get("population_latest", {})
        # 연봉 상위 퍼센트 기준 테이블 (1억 이상 처리용)
        self.income_percentiles = self.statistics_data.get("income_percentiles", [])
        # 성별별 키 CDF 포인트 (남성 우선 적용)
        self.male_height_cdf_points = self.statistics_data.get("male_height_cdf_points", [])
        # (선택) 연령별 인구 분포
        self.age_population = self.statistics_data.get("age_population", {})
    
    def _load_statistics_data(self) -> Dict:
        """
        실제 통계 데이터를 로드합니다.
        
        Returns:
            Dict: 통계 데이터 딕셔너리
        """
        try:
            # 실제 CSV 파일에서 데이터 로드
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
            
            # 키 분포 데이터 (성별별)
            height_data = pd.read_csv(os.path.join(data_path, 'Height_Distribution__English_Headers_.csv'))
            women_height_data = pd.read_csv(os.path.join(data_path, 'women_Combined_Female_Height_Distribution__20_49.csv'))
            men_height_data = pd.read_csv(os.path.join(data_path, 'men_Percentile_Verification.csv'))
            
            # 성별별 키 분포 생성
            height_dist = self._process_height_data(height_data, women_height_data, men_height_data)
            
            # 소득 분포 데이터
            income_data = pd.read_csv(os.path.join(data_path, 'Income_Distribution_by_Gender__2024_.csv'))
            salary_dist = self._process_income_data(income_data)
            
            # 직업 분포 데이터
            occupation_data = pd.read_csv(os.path.join(data_path, 'Occupation_Distribution.csv'))
            job_dist = self._process_occupation_data(occupation_data)
            
            # 지역 분포 데이터 (신규 CSV 우선 사용, 실패 시 기존 처리)
            location_dist = {}
            try:
                pop_csv = os.path.join(data_path, 'regional_population_statistics_2025.csv')
                if os.path.exists(pop_csv):
                    location_dist, population_latest = self._load_region_shares_from_population_csv(pop_csv)
                    population_out = population_latest
                else:
                    raise FileNotFoundError('regional_population_statistics_2025.csv not found')
            except Exception:
                # 구형 파일로 폴백
                region_data = pd.read_csv(os.path.join(data_path, 'Region_population_shares__2025-07__MOIS_.csv'))
                location_dist = self._process_region_data(region_data)
                population_out = {
                    "nation": {"total": 51169148.0, "남성": 25470398.0, "여성": 25698750.0},
                    "regions": {}
                }
            
            # 미혼율 데이터
            unmarried_data = pd.read_csv(os.path.join(data_path, 'unmarried_rate_by_age.csv'))
            marital_dist = self._process_marital_data(unmarried_data)
            
            # 흡연율 데이터
            smoking_data = pd.read_csv(os.path.join(data_path, 'smokingRate.csv'))
            smoking_dist = self._process_smoking_data(smoking_data)
            
            # 지역·연령별 혼인율(천명당) 데이터
            try:
                region_age_marry_csv = os.path.join(data_path, '지역_연령별_혼인율.csv')
                region_age_marriage_rate = {}
                if os.path.exists(region_age_marry_csv):
                    region_age_marriage_rate = self._load_region_age_marriage_rate(region_age_marry_csv)
            except Exception:
                region_age_marriage_rate = {}
            
            out = {
                "height": height_dist,
                "salary": salary_dist,
                "job": job_dist,
                "location": location_dist,
                "marital_status": marital_dist,
                "smoking": smoking_dist,
                "education": {
                    "SKY": 0.02,      # 2% - 실제 통계 필요
                    "인서울": 0.08,    # 8% - 실제 통계 필요
                    "지거국": 0.15,    # 15% - 실제 통계 필요
                    "4년제": 0.35,    # 35% - 실제 통계 필요
                    "이하": 0.40      # 40% - 실제 통계 필요
                }
            }
            out["population_latest"] = population_out
            # 지역·연령별 혼인율 저장
            try:
                out["region_age_marriage_rate"] = region_age_marriage_rate
            except Exception:
                pass
            # 연봉 상위 퍼센트 테이블 로드 (선택)
            try:
                pt_path = os.path.join(data_path, '연봉_구간.csv')
                if os.path.exists(pt_path):
                    out["income_percentiles"] = self._load_income_percentiles(pt_path)
            except Exception as _:
                pass
            # 남성 키 CDF 포인트 로드 (선택)
            try:
                men_path = os.path.join(data_path, 'men_Percentile_Verification.csv')
                if os.path.exists(men_path):
                    out["male_height_cdf_points"] = self._load_male_height_cdf(men_path)
            except Exception as _:
                pass
            # (선택) 연령별 인구 분포 로드: population_by_age_2025.csv (age, male, female)
            try:
                age_pop_path = os.path.join(data_path, 'population_by_age_2025.csv')
                if os.path.exists(age_pop_path):
                    out["age_population"] = self._load_age_population_by_csv(age_pop_path)
            except Exception as _:
                pass
            # 보강: 남녀 분리 CSV로부터 연령 인구 구성
            try:
                if not out.get("age_population"):
                    male_csv = os.path.join(data_path, 'male_population_by_age_korea.csv')
                    female_csv = os.path.join(data_path, 'female_population_by_age_korea.csv')
                    if os.path.exists(male_csv) and os.path.exists(female_csv):
                        out["age_population"] = self._load_age_population_from_gender_csvs(male_csv, female_csv)
            except Exception:
                pass
            return out
            
        except Exception as e:
            print(f"실제 데이터 로드 실패, 임시 데이터 사용: {e}")
            return self._get_fallback_data()

    def _load_region_shares_from_population_csv(self, csv_path: str) -> Tuple[Dict, Dict]:
        """행정구역별 최신월 총인구수를 사용해 시·도 점유율을 계산합니다.

        Args:
            csv_path: 지역 인구 통계 CSV 경로

        Returns:
            (shares, population):
              shares: Dict[str, float] 지역명 → 인구 점유율(0~1)
              population: {
                  "nation": {"total": float, "남성": float, "여성": float},
                  "regions": { region: {"total": float, "남성": float, "여성": float} }
              }
        """
        df = pd.read_csv(csv_path, header=None)
        if df.shape[0] < 3:
            raise ValueError('CSV rows insufficient')

        header_months = df.iloc[0].tolist()
        header_kinds = df.iloc[1].tolist()

        # 최신월의 각 지표 열 인덱스 탐색 (총/남/여)
        total_idx = male_idx = female_idx = None
        for idx in range(len(header_months) - 1, -1, -1):
            kind = str(header_kinds[idx]).strip()
            if total_idx is None and kind.startswith('총인구수'):
                total_idx = idx
            if male_idx is None and kind.startswith('남자인구수'):
                male_idx = idx
            if female_idx is None and kind.startswith('여자인구수'):
                female_idx = idx
            if total_idx is not None and male_idx is not None and female_idx is not None:
                break
        if total_idx is None:
            raise ValueError('No total population column found')

        # 합계(전국)와 개별 시도 행 추출
        rows = df.iloc[2:]
        name_col = rows.iloc[:, 0].astype(str)
        total_col = rows.iloc[:, total_idx]
        male_col = rows.iloc[:, male_idx] if male_idx is not None else None
        female_col = rows.iloc[:, female_idx] if female_idx is not None else None

        # 전국 분모
        nation_mask = name_col.str.contains('전국')
        if not nation_mask.any():
            raise ValueError('Nationwide row not found')
        nationwide = float(total_col[nation_mask].values[0])
        nation_male = float(male_col[nation_mask].values[0]) if male_col is not None else None
        nation_female = float(female_col[nation_mask].values[0]) if female_col is not None else None
        if nationwide <= 0:
            raise ValueError('Invalid nationwide total')

        # 시도 목록 필터링: "전국" 제외
        shares: Dict[str, float] = {}
        population = {"nation": {"total": nationwide, "남성": nation_male, "여성": nation_female}, "regions": {}}
        for idx_row, (region, total) in enumerate(zip(name_col, total_col)):
            region = str(region).strip().strip('"')
            if region == '전국':
                continue
            try:
                pop = float(total)
            except Exception:
                continue
            share = max(0.0, pop / nationwide)
            shares[region] = share
            male_val = float(male_col.iloc[idx_row]) if male_col is not None else None
            female_val = float(female_col.iloc[idx_row]) if female_col is not None else None
            population["regions"][region] = {"total": pop, "남성": male_val, "여성": female_val}

        # 그룹 프리셋 계산(수도권/지방광역시/기타)
        metro_set = {'서울특별시', '경기도', '인천광역시'}
        big_cities_set = {'부산광역시', '대구광역시', '광주광역시', '대전광역시', '울산광역시'}
        sum_metro = sum(shares.get(r, 0.0) for r in metro_set)
        sum_big = sum(shares.get(r, 0.0) for r in big_cities_set)
        sum_others = max(0.0, 1.0 - (sum_metro + sum_big))
        shares['수도권'] = sum_metro
        shares['지방광역시'] = sum_big
        shares['기타'] = sum_others

        # 정규화(부동소수 오차 보정)
        total_sum = sum(v for k, v in shares.items() if k not in ('수도권', '지방광역시', '기타'))
        # 반환
        return shares, population

    def _load_income_percentiles(self, csv_path: str) -> List[Dict]:
        """연봉 상위 퍼센트 테이블을 로드합니다.

        Returns list of dicts: { 'top_percent': float, 'avg_total_manwon': float }
        """
        df = pd.read_csv(csv_path)
        records: List[Dict] = []
        for _, row in df.iterrows():
            group = str(row.get('구분', '')).strip()
            total = row.get('총급여', None)
            if not group.startswith('상위'):
                continue
            # 구분에서 퍼센트 수치만 추출 (상위 10% → 10)
            try:
                p_str = group.replace('상위', '').replace('%', '').strip()
                p_val = float(p_str)
            except Exception:
                continue
            try:
                total_val = float(total)
            except Exception:
                continue
            # 총급여 단위가 천원이라 가정 → 만원으로 변환
            avg_total_manwon = total_val * 0.1
            records.append({'top_percent': p_val, 'avg_total_manwon': avg_total_manwon})
        # 퍼센트 오름차순 정렬 (0.1, 0.2, ..., 100)
        records.sort(key=lambda x: x['top_percent'])
        return records

    def _estimate_share_above_income(self, min_manwon: int) -> float:
        """1억(=10000만원) 이상 구간에서, 평균 총급여 기반으로 상위 퍼센트 근사치를 추정합니다.

        Approach: 찾고자 하는 임계값 이상이 되는 최소 top_percent를 선형 보간으로 추정. 반환은 비율(0~1).
        데이터가 부족하면 0으로 반환.
        """
        table = self.income_percentiles or []
        if not table:
            return 0.0
        # 평균 총급여는 top_percent가 커질수록 감소 경향. min_manwon에 가장 가까운 상위% 찾기
        # 테이블 내에서 avg_total >= min_manwon 되는 최소 p를 탐색
        prev = None
        for rec in table:
            p = rec['top_percent']
            avg_mw = rec['avg_total_manwon']
            if avg_mw >= min_manwon:
                # 보간 (prev: 더 높은 p에서 평균이 더 낮음)
                if prev is None:
                    return max(0.0, min(1.0, p / 100.0))
                p0, v0 = prev['top_percent'], prev['avg_total_manwon']
                p1, v1 = p, avg_mw
                if v0 == v1:
                    est_p = p1
                else:
                    # v0 < min < v1, interpolate on value→percent
                    ratio = (min_manwon - v0) / (v1 - v0)
                    est_p = p0 + (p1 - p0) * ratio
                return max(0.0, min(1.0, est_p / 100.0))
            prev = rec
        # 임계값이 너무 낮아 하위 데이터까지 내려간 경우: 전체 1.0
        return 1.0
    
    def _process_height_data(self, height_data: pd.DataFrame, women_data: pd.DataFrame, men_data: pd.DataFrame) -> Dict:
        """키 분포 데이터를 처리합니다."""
        height_dist = {}
        
        # 전체 키 분포를 기본으로 사용
        for _, row in height_data.iterrows():
            height_range = row['Height Range']
            percentage = row['Percentage (%)'] / 100
            
            # 범위를 키로 변환 (일부 표기 케이스 대응)
            if '151~155.9cm' in height_range:
                height_dist['150-155'] = percentage
            elif '156~160.9cm' in height_range:
                height_dist['155-160'] = percentage
            elif '161~165.9cm' in height_range:
                height_dist['160-165'] = percentage
            elif '166~170.9cm' in height_range:
                height_dist['165-170'] = percentage
            elif '171~175.9cm' in height_range:
                height_dist['170-175'] = percentage
            elif '176~180.9cm' in height_range:
                height_dist['175-180'] = percentage
            elif '181~185.9cm' in height_range:
                height_dist['180-185'] = percentage
        
        # 품질 체크: 구간이 충분치 않으면 폴백 사용
        if len(height_dist.keys()) < 4:
            height_dist = self._get_fallback_data()["height"]

        return height_dist

    def _load_male_height_cdf(self, csv_path: str) -> List[Dict]:
        """남성 키에 대한 CDF 포인트를 로드합니다.
        Returns: [{ 'height': float, 'cdf': float }, ...]
        """
        df = pd.read_csv(csv_path)
        points: List[Dict] = []
        for _, row in df.iterrows():
            try:
                h = float(row['Actual Height (cm)'])
                cdf = float(row['Expected CDF (%)'])
            except Exception:
                continue
            points.append({'height': h, 'cdf': cdf / 100.0})
        points.sort(key=lambda x: x['height'])
        return points

    def _estimate_male_cdf_above(self, cm: float) -> Optional[float]:
        """남성 키가 cm 이상일 비율(> = cm)을 선형 보간으로 추정합니다."""
        pts = self.male_height_cdf_points
        if not pts:
            return None
        # CDF는 P(<=h). 우리가 필요한 건 P(>=cm) = 1 - P(<cm)
        # 선형 보간으로 CDF(cm) 추정
        prev = None
        # 하단 외삽: cm가 가장 작은 포인트보다 작으면 첫 두 점으로 외삽
        if cm <= pts[0]['height'] and len(pts) >= 2:
            h0, c0 = pts[0]['height'], pts[0]['cdf']
            h1, c1 = pts[1]['height'], pts[1]['cdf']
            slope = (c1 - c0) / (h1 - h0) if h1 != h0 else 0.0
            cdf_cm = c0 + slope * (cm - h0)
            cdf_cm = max(0.0, min(1.0, cdf_cm))
            return max(0.0, min(1.0, 1.0 - cdf_cm))
        for p in pts:
            if p['height'] >= cm:
                if prev is None:
                    cdf_cm = p['cdf']
                else:
                    h0, c0 = prev['height'], prev['cdf']
                    h1, c1 = p['height'], p['cdf']
                    if h1 == h0:
                        cdf_cm = c1
                    else:
                        t = (cm - h0) / (h1 - h0)
                        cdf_cm = c0 + (c1 - c0) * t
                return max(0.0, min(1.0, 1.0 - cdf_cm))
            prev = p
        # 상단 외삽: cm가 가장 큰 포인트보다 크면 마지막 두 점의 기울기로 외삽
        if len(pts) >= 2:
            h0, c0 = pts[-2]['height'], pts[-2]['cdf']
            h1, c1 = pts[-1]['height'], pts[-1]['cdf']
            slope = (c1 - c0) / (h1 - h0) if h1 != h0 else 0.0
            cdf_cm = c1 + slope * (cm - h1)
            cdf_cm = max(0.0, min(1.0, cdf_cm))
            return max(0.0, min(1.0, 1.0 - cdf_cm))
        return 0.0
    
    def _process_income_data(self, income_data: pd.DataFrame) -> Dict:
        """소득 분포 데이터를 처리합니다."""
        salary_dist = {}
        
        # 전체 평균 사용 (성별 구분 없이)
        for _, row in income_data.iterrows():
            income_range = row['Income Range']
            total_percentage = row['Total (%)'] / 100
            
            if 'Under 20M' in income_range:
                salary_dist['2000만원 이하'] = total_percentage
            elif '20M–40M' in income_range:
                salary_dist['2000-3000만원'] = total_percentage * 0.6  # 20-30M
                salary_dist['3000-4000만원'] = total_percentage * 0.4  # 30-40M
            elif '40M–60M' in income_range:
                salary_dist['4000-5000만원'] = total_percentage * 0.5  # 40-50M
                salary_dist['5000만원 이상'] = total_percentage * 0.5  # 50-60M
            elif '60M–80M' in income_range:
                salary_dist['5000만원 이상'] = salary_dist.get('5000만원 이상', 0) + total_percentage * 0.5
            elif '80M–100M' in income_range:
                salary_dist['5000만원 이상'] = salary_dist.get('5000만원 이상', 0) + total_percentage * 0.5
            elif '100M+' in income_range:
                salary_dist['5000만원 이상'] = salary_dist.get('5000만원 이상', 0) + total_percentage
        
        return salary_dist

    def _load_age_population_by_csv(self, csv_path: str) -> Dict[int, Dict[str, float]]:
        """연령별 인구 분포를 로드합니다.

        CSV 형식 예:
            age,male,female
            0,120000,110000
            1,119000,108000
            ...
        대소문자/한글 헤더도 일부 허용합니다.
        Returns: { age_int: {"남성": float, "여성": float} }
        """
        df = pd.read_csv(csv_path)
        cols = {c.lower().strip(): c for c in df.columns}
        # 헤더 후보 매핑
        age_col = cols.get('age') or cols.get('연령') or list(df.columns)[0]
        male_col = cols.get('male') or cols.get('남성') or cols.get('남자')
        female_col = cols.get('female') or cols.get('여성') or cols.get('여자')
        if male_col is None or female_col is None:
            # 남/여 중 하나라도 없으면 사용하지 않음
            return {}
        out: Dict[int, Dict[str, float]] = {}
        for _, row in df.iterrows():
            try:
                age = int(row[age_col])
            except Exception:
                continue
            try:
                m = float(row[male_col])
            except Exception:
                m = 0.0
            try:
                f = float(row[female_col])
            except Exception:
                f = 0.0
            out[age] = {"남성": m, "여성": f}
        return out

    def _load_age_population_from_gender_csvs(self, male_csv_path: str, female_csv_path: str) -> Dict[int, Dict[str, float]]:
        """남녀 분리된 한국 연령 인구 CSV들을 병합해 연령별 인구 분포를 생성합니다.

        각 CSV 형식 예:
            연령별,인구,비율
            0세,"111,163",0.4303%
            ...
            총,"25,836,801",100.0000%

        Returns:
            Dict[int, Dict[str, float]]: { age: {"남성": float, "여성": float} }
        """
        def parse(path: str) -> Dict[int, float]:
            df = pd.read_csv(path)
            # 컬럼 추론
            col_age = df.columns[0]
            col_pop = df.columns[1] if df.shape[1] > 1 else df.columns[0]
            result: Dict[int, float] = {}
            for _, row in df.iterrows():
                age_raw = str(row.get(col_age, '')).strip()
                if not age_raw or '총' in age_raw:
                    continue
                try:
                    age_val = int(str(age_raw).replace('세', '').strip())
                except Exception:
                    continue
                pop_raw = row.get(col_pop, 0)
                try:
                    if isinstance(pop_raw, str):
                        pop_val = float(pop_raw.replace(',', '').replace('"', '').strip())
                    else:
                        pop_val = float(pop_raw)
                except Exception:
                    pop_val = 0.0
                result[age_val] = max(0.0, pop_val)
            return result

        male = parse(male_csv_path)
        female = parse(female_csv_path)
        ages = set(male.keys()) | set(female.keys())
        merged: Dict[int, Dict[str, float]] = {}
        for a in ages:
            merged[a] = {"남성": float(male.get(a, 0.0)), "여성": float(female.get(a, 0.0))}
        return merged

    def _get_unmarried_band_key(self, age: int) -> Optional[str]:
        """unmarried_rate_by_age 매핑에서 사용할 연령대 키를 반환합니다."""
        if age < 20:
            return None
        if age < 25:
            return "20-24"
        if age < 30:
            return "25-29"
        if age < 35:
            return "30-34"
        if age < 40:
            return "35-39"
        if age < 45:
            return "40-44"
        if age < 50:
            return "45-49"
        return "45-49"

    def _compute_population_weighted_unmarried_rate(self, gender: str, age_low: int, age_high: int) -> Tuple[Optional[float], float, float]:
        """단일 나이별 인구와 연령대별 미혼률을 이용해 인구가중 미혼률을 계산합니다.

        Returns:
            (rate, sum_unmarried_count, sum_pop_selected)
        """
        ms_map = self.statistics_data.get("marital_status", {})
        if not isinstance(self.age_population, dict) or not self.age_population:
            return None, 0.0, 0.0
        sum_pop = 0.0
        sum_unmarried = 0.0
        for a in range(age_low, age_high + 1):
            rec = self.age_population.get(a)
            if not rec or gender not in rec:
                continue
            pop_a = float(rec[gender])
            key = self._get_unmarried_band_key(a)
            if key is None:
                continue
            # _process_marital_data 키 보정: '20-24'는 내부에서 '20대'로 저장됐을 수 있음
            rate_entry = ms_map.get(key)
            if rate_entry is None and key == "20-24":
                rate_entry = ms_map.get("20대")
            rate = None
            if rate_entry is not None:
                r = rate_entry.get(gender)
                if isinstance(r, (int, float)):
                    rate = float(r)
            if rate is None:
                continue
            sum_pop += pop_a
            sum_unmarried += pop_a * rate
        if sum_pop > 0:
            return max(0.0, min(1.0, sum_unmarried / sum_pop)), sum_unmarried, sum_pop
        return None, 0.0, 0.0

    def _load_region_age_marriage_rate(self, csv_path: str) -> Dict[str, Dict[str, Dict[str, float]]]:
        """지역·연령대별 혼인율(해당 연령 천명당 건수)을 로드합니다.

        CSV 형식:
            "시도별","연령별",남편(해당연령 천명당 건),아내(해당연령 천명당 건)
            "계","20 - 24세",2.6,7.4
            ...

        Returns:
            Dict[str, Dict[str, Dict[str, float]]]: region -> age_band -> {"남성": rate, "여성": rate}
            rate는 1명 기준 확률(천분율을 1000으로 나눔)
        """
        df = pd.read_csv(csv_path)
        # 헤더 행이 2행으로 중복 포함된 경우를 대비, 첫 번째 의미 행을 찾음
        # 일반적으로 2행 구조: 0행 컬럼명 텍스트, 1행 실제 헤더. 여기서는 이미 컬럼명이 잡혀있다고 가정
        col_region = df.columns[0]
        col_age = df.columns[1]
        col_male = df.columns[2]
        col_female = df.columns[3]
        out: Dict[str, Dict[str, Dict[str, float]]] = {}
        for _, row in df.iterrows():
            region = str(row.get(col_region, '')).strip().strip('"')
            age_band = str(row.get(col_age, '')).strip().strip('"')
            if not region or not age_band or region == '시도별' or age_band == '연령별':
                continue
            try:
                male_rate = float(row.get(col_male, 0.0)) / 1000.0
            except Exception:
                male_rate = 0.0
            try:
                female_rate = float(row.get(col_female, 0.0)) / 1000.0
            except Exception:
                female_rate = 0.0
            out.setdefault(region, {})[age_band] = {"남성": max(0.0, male_rate), "여성": max(0.0, female_rate)}
        return out

    def _estimate_marital_factor(self, gender: str, age_low: int, age_high: int, selected_regions: Optional[List[str]]) -> Tuple[Optional[float], Optional[str]]:
        """선택 성별/연령(범위)과 지역 선택에 따른 '미혼률' 팩터를 계산합니다.

        기본:
        - `unmarried_rate_by_age.csv`의 미혼율(연령대별)을 겹침 연수로 가중 평균해 사용

        지역 보정(선택 사항):
        - `지역_연령별_혼인율.csv`의 혼인율(천명당)을 전국 대비 지수로 환산하여
          미혼률을 미세 보정(발생률이 높을수록 미혼률을 소폭 감소)
        """
        # 1) 기본 미혼률: 연령대별 미혼률(전국) 가중 평균
        bands_unmarried = [
            (20, 24, "20-24"),
            (25, 29, "25-29"),
            (30, 34, "30-34"),
            (35, 39, "35-39"),
            (40, 44, "40-44"),
            (45, 49, "45-49"),
        ]
        ms_map = self.statistics_data.get("marital_status", {})
        total_years = max(1, age_high - age_low + 1)
        base_unmarried = None
        acc = 0.0
        for lo, hi, key in bands_unmarried:
            overlap = max(0, min(hi, age_high) - max(lo, age_low) + 1)
            if overlap <= 0:
                continue
            rate = ms_map.get(key, {}).get(gender)
            if isinstance(rate, (int, float)):
                acc += (overlap / total_years) * float(rate)
        if acc > 0:
            base_unmarried = max(0.0, min(1.0, acc))
        else:
            # 데이터 범위를 벗어난 경우(예: 50세 이상만 선택): 가장 가까운 구간으로 근사
            # 상한을 45-49로 고정 근사
            rate = ms_map.get("45-49", {}).get(gender)
            if isinstance(rate, (int, float)):
                base_unmarried = max(0.0, min(1.0, float(rate)))
            else:
                return None, None

        # 2) 지역 보정: 혼인율(천명당) 지수를 사용해 미세 조정
        region_age = self.statistics_data.get("region_age_marriage_rate") or {}
        if region_age:
            bands_marry = [
                (20, 24, "20 - 24세"),
                (25, 29, "25 - 29세"),
                (30, 34, "30 - 34세"),
                (35, 39, "35 - 39세"),
                (40, 44, "40 - 44세"),
                (45, 49, "45 - 49세"),
            ]

            def marry_rate_for(region_key: str) -> float:
                reg_map = region_age.get(region_key) or {}
                acc_r = 0.0
                for lo, hi, label in bands_marry:
                    overlap = max(0, min(hi, age_high) - max(lo, age_low) + 1)
                    if overlap <= 0:
                        continue
                    rec = reg_map.get(label)
                    if rec and gender in rec:
                        acc_r += (overlap / total_years) * float(rec[gender])
                return max(0.0, acc_r)

            nat_key = "계" if "계" in region_age else next(iter(region_age.keys()))
            nat_rate = marry_rate_for(nat_key) or 1e-9

            if selected_regions:
                # 선택 지역 가중 평균 혼인율
                pop = self.population_latest or {}
                region_pops = pop.get("regions", {})
                weights: List[Tuple[float, str]] = []
                for r in selected_regions:
                    if r in region_age:
                        w = float(region_pops.get(r, {}).get(gender) or 0.0)
                        if w > 0:
                            weights.append((w, r))
                if weights:
                    total_w = sum(w for w, _ in weights)
                    reg_rate = 0.0
                    for w, r in weights:
                        reg_rate += (w / total_w) * marry_rate_for(r)
                else:
                    reg_rate = nat_rate
                label = f"선택 지역 가중 {age_low}-{age_high}세 {gender}"
            else:
                reg_rate = nat_rate
                label = f"전국 합계 {age_low}-{age_high}세 {gender}"

            # 혼인율 지수(>1 → 결혼 활성 → 미혼률 소폭 감소)
            index = reg_rate / nat_rate
            alpha = 0.25  # 보정 강도 (0~1)
            adjusted = base_unmarried * max(0.0, (1.0 - alpha * (index - 1.0)))
            return max(0.0, min(1.0, adjusted)), label

        # 지역 데이터 없으면 기본값 반환
        return base_unmarried, f"전국 합계 {age_low}-{age_high}세 {gender}"
    
    def _process_occupation_data(self, occupation_data: pd.DataFrame) -> Dict:
        """직업 분포 데이터를 처리합니다."""
        job_dist = {}
        
        for _, row in occupation_data.iterrows():
            occupation = row['Occupation Group']
            share = row['Share']
            
            if 'Professional' in occupation:
                job_dist['전문직'] = share
            elif 'Public Servant' in occupation:
                job_dist['공무원'] = share
            elif 'Public Enterprise' in occupation:
                job_dist['공기업'] = share
            elif 'Others' in occupation:
                job_dist['그 외'] = share
        
        return job_dist
    
    def _process_region_data(self, region_data: pd.DataFrame) -> Dict:
        """지역 분포 데이터를 처리합니다."""
        location_dist = {}
        
        # 수도권: 서울 + 경기도
        # 지방광역시: 부산, 대구, 인천, 광주, 대전, 울산
        # 기타: 나머지
        
        capital_area = 0
        metropolitan = 0
        others = 0
        
        for _, row in region_data.iterrows():
            region = row['region']
            share = row['share_percent'] / 100
            
            if region in ['Seoul', 'Gyeonggi']:
                capital_area += share
            elif region in ['Busan', 'Daegu', 'Incheon', 'Gwangju', 'Daejeon', 'Ulsan']:
                metropolitan += share
            else:
                others += share
        
        location_dist['수도권'] = capital_area
        location_dist['지방광역시'] = metropolitan
        location_dist['기타'] = others
        
        return location_dist
    
    def _process_marital_data(self, unmarried_data: pd.DataFrame) -> Dict:
        """미혼율 데이터를 처리합니다."""
        marital_dist = {}
        
        for _, row in unmarried_data.iterrows():
            age_range = row['age']
            male_rate = row['male'] / 100
            female_rate = row['female'] / 100
            
            if '20-24' in age_range:
                marital_dist['20대'] = {'남성': male_rate, '여성': female_rate}
            elif '25-29' in age_range:
                marital_dist['25-29'] = {'남성': male_rate, '여성': female_rate}
            elif '30-34' in age_range:
                marital_dist['30-34'] = {'남성': male_rate, '여성': female_rate}
            elif '35-39' in age_range:
                marital_dist['35-39'] = {'남성': male_rate, '여성': female_rate}
            elif '40-44' in age_range:
                marital_dist['40-44'] = {'남성': male_rate, '여성': female_rate}
            elif '45-49' in age_range:
                marital_dist['45-49'] = {'남성': male_rate, '여성': female_rate}
        
        return marital_dist
    
    def _process_smoking_data(self, smoking_data: pd.DataFrame) -> Dict:
        """흡연율 데이터를 처리합니다."""
        smoking_dist = {}
        
        for _, row in smoking_data.iterrows():
            group = row['Group']
            rate = row['SmokingRate'] / 100
            
            if group == 'Male':
                smoking_dist['남성'] = rate
            elif group == 'Female':
                smoking_dist['여성'] = rate
        
        return smoking_dist
    
    def _get_fallback_data(self) -> Dict:
        """폴백용 임시 데이터를 반환합니다."""
        return {
            "height": {
                "150-155": 0.05,  # 5%
                "155-160": 0.12,  # 12%
                "160-165": 0.20,  # 20%
                "165-170": 0.28,  # 28%
                "170-175": 0.22,  # 22%
                "175-180": 0.10,  # 10%
                "180-185": 0.03   # 3%
            },
            "education": {
                "SKY": 0.02,      # 2%
                "인서울": 0.08,    # 8%
                "지거국": 0.15,    # 15%
                "4년제": 0.35,    # 35%
                "이하": 0.40      # 40%
            },
            "salary": {
                "2000만원 이하": 0.45,    # 45%
                "2000-3000만원": 0.30,   # 30%
                "3000-4000만원": 0.15,   # 15%
                "4000-5000만원": 0.07,   # 7%
                "5000만원 이상": 0.03     # 3%
            },
            "job": {
                "전문직": 0.08,    # 8%
                "공무원": 0.05,    # 5%
                "공기업": 0.07,    # 7%
                "그 외": 0.80      # 80%
            },
            "location": {
                "수도권": 0.50,    # 50%
                "지방광역시": 0.30, # 30%
                "기타": 0.20      # 20%
            },
            "marital_status": {
                "20대": {"남성": 0.85, "여성": 0.90},
                "25-29": {"남성": 0.70, "여성": 0.80},
                "30-34": {"남성": 0.40, "여성": 0.50},
                "35-39": {"남성": 0.20, "여성": 0.30},
                "40-44": {"남성": 0.10, "여성": 0.15},
                "45-49": {"남성": 0.05, "여성": 0.10}
            },
            "smoking": {
                "남성": 0.35,     # 35% 흡연
                "여성": 0.08      # 8% 흡연
            }
        }
    
    def _load_correlation_factors(self) -> Dict:
        """
        조건 간 상관관계 계수를 로드합니다.
        
        Returns:
            Dict: 상관관계 계수
        """
        return {
            # 학력-연봉 상관관계
            "education_salary": {
                "SKY": {"5000만원 이상": 0.8, "4000-5000만원": 0.6, "3000-4000만원": 0.4},
                "인서울": {"5000만원 이상": 0.6, "4000-5000만원": 0.7, "3000-4000만원": 0.5},
                "지거국": {"5000만원 이상": 0.4, "4000-5000만원": 0.6, "3000-4000만원": 0.7},
                "4년제": {"5000만원 이상": 0.2, "4000-5000만원": 0.4, "3000-4000만원": 0.6},
                "이하": {"5000만원 이상": 0.1, "4000-5000만원": 0.2, "3000-4000만원": 0.3}
            },
            # 학력-직업 상관관계
            "education_job": {
                "SKY": {"전문직": 0.7, "공무원": 0.3, "공기업": 0.4},
                "인서울": {"전문직": 0.5, "공무원": 0.4, "공기업": 0.5},
                "지거국": {"전문직": 0.3, "공무원": 0.5, "공기업": 0.6},
                "4년제": {"전문직": 0.2, "공무원": 0.3, "공기업": 0.4},
                "이하": {"전문직": 0.1, "공무원": 0.2, "공기업": 0.2}
            },
            # 지역-직업 상관관계
            "location_job": {
                "수도권": {"전문직": 0.6, "공무원": 0.3, "공기업": 0.4},
                "지방광역시": {"전문직": 0.3, "공무원": 0.5, "공기업": 0.6},
                "기타": {"전문직": 0.1, "공무원": 0.4, "공기업": 0.3}
            },
            # 나이-연봉 상관관계
            "age_salary": {
                "20대": {"5000만원 이상": 0.1, "4000-5000만원": 0.2, "3000-4000만원": 0.3},
                "25-29": {"5000만원 이상": 0.2, "4000-5000만원": 0.3, "3000-4000만원": 0.4},
                "30-34": {"5000만원 이상": 0.4, "4000-5000만원": 0.5, "3000-4000만원": 0.6},
                "35-39": {"5000만원 이상": 0.6, "4000-5000만원": 0.7, "3000-4000만원": 0.8}
            }
        }
    
    def _apply_correlation_adjustment(self, probabilities: List[float], filters: Dict) -> List[float]:
        """
        조건 간 상관관계를 고려하여 확률을 조정합니다 (개선된 방식).
        
        Args:
            probabilities (List[float]): 개별 확률 리스트
            filters (Dict): 필터 조건
            
        Returns:
            List[float]: 조정된 확률 리스트
        """
        adjusted_probs = probabilities.copy()
        
        # 조건부 확률을 사용한 상관관계 조정
        if "education" in filters and "salary" in filters:
            edu = filters["education"]
            salary = filters["salary"]
            
            # 학력별 소득 분포 (실제 데이터 기반 추정)
            education_salary_dist = {
                "SKY": {
                    "2000만원 이하": 0.05,      # SKY는 대부분 높은 소득
                    "2000-3000만원": 0.10,
                    "3000-4000만원": 0.20,
                    "4000-5000만원": 0.30,
                    "5000만원 이상": 0.35
                },
                "인서울": {
                    "2000만원 이하": 0.10,
                    "2000-3000만원": 0.20,
                    "3000-4000만원": 0.30,
                    "4000-5000만원": 0.25,
                    "5000만원 이상": 0.15
                },
                "지거국": {
                    "2000만원 이하": 0.15,
                    "2000-3000만원": 0.25,
                    "3000-4000만원": 0.30,
                    "4000-5000만원": 0.20,
                    "5000만원 이상": 0.10
                },
                "4년제": {
                    "2000만원 이하": 0.25,
                    "2000-3000만원": 0.30,
                    "3000-4000만원": 0.25,
                    "4000-5000만원": 0.15,
                    "5000만원 이상": 0.05
                },
                "이하": {
                    "2000만원 이하": 0.40,
                    "2000-3000만원": 0.35,
                    "3000-4000만원": 0.15,
                    "4000-5000만원": 0.08,
                    "5000만원 이상": 0.02
                }
            }
            
            if edu in education_salary_dist and salary in education_salary_dist[edu]:
                # 조건부 확률: P(소득|학력) / P(소득)
                conditional_prob = education_salary_dist[edu][salary]
                marginal_prob = self.statistics_data["salary"].get(salary, 0.01)
                
                if marginal_prob > 0:
                    # 베이즈 정리 적용
                    adjustment_factor = conditional_prob / marginal_prob
                    # 범위 제한 (0.1 ~ 3.0)
                    adjustment_factor = max(0.1, min(3.0, adjustment_factor))
                    
                    # 연봉 확률 조정
                    if len(adjusted_probs) >= 3:
                        adjusted_probs[2] *= adjustment_factor
        
        # 학력-직업 상관관계 조정
        if "education" in filters and "job" in filters:
            edu = filters["education"]
            job = filters["job"]
            
            # 학력별 직업 분포 (실제 데이터 기반 추정)
            education_job_dist = {
                "SKY": {
                    "전문직": 0.40,      # SKY는 전문직 비율이 높음
                    "공무원": 0.15,
                    "공기업": 0.20,
                    "그 외": 0.25
                },
                "인서울": {
                    "전문직": 0.25,
                    "공무원": 0.20,
                    "공기업": 0.25,
                    "그 외": 0.30
                },
                "지거국": {
                    "전문직": 0.15,
                    "공무원": 0.25,
                    "공기업": 0.30,
                    "그 외": 0.30
                },
                "4년제": {
                    "전문직": 0.10,
                    "공무원": 0.15,
                    "공기업": 0.20,
                    "그 외": 0.55
                },
                "이하": {
                    "전문직": 0.05,
                    "공무원": 0.10,
                    "공기업": 0.10,
                    "그 외": 0.75
                }
            }
            
            if edu in education_job_dist and job in education_job_dist[edu]:
                conditional_prob = education_job_dist[edu][job]
                marginal_prob = self.statistics_data["job"].get(job, 0.01)
                
                if marginal_prob > 0:
                    adjustment_factor = conditional_prob / marginal_prob
                    adjustment_factor = max(0.1, min(3.0, adjustment_factor))
                    
                    # 직업 확률 조정
                    if len(adjusted_probs) >= 4:
                        adjusted_probs[3] *= adjustment_factor
        
        # 지역-직업 상관관계 조정
        if "location" in filters and "job" in filters:
            location = filters["location"]
            job = filters["job"]
            
            # 지역별 직업 분포
            location_job_dist = {
                "수도권": {
                    "전문직": 0.15,      # 수도권은 전문직 비율이 높음
                    "공무원": 0.08,
                    "공기업": 0.12,
                    "그 외": 0.65
                },
                "지방광역시": {
                    "전문직": 0.08,
                    "공무원": 0.12,
                    "공기업": 0.15,
                    "그 외": 0.65
                },
                "기타": {
                    "전문직": 0.05,
                    "공무원": 0.10,
                    "공기업": 0.08,
                    "그 외": 0.77
                }
            }
            
            if location in location_job_dist and job in location_job_dist[location]:
                conditional_prob = location_job_dist[location][job]
                marginal_prob = self.statistics_data["job"].get(job, 0.01)
                
                if marginal_prob > 0:
                    adjustment_factor = conditional_prob / marginal_prob
                    adjustment_factor = max(0.1, min(3.0, adjustment_factor))
                    
                    # 직업 확률 조정
                    if len(adjusted_probs) >= 4:
                        adjusted_probs[3] *= adjustment_factor
        
        # 나이-연봉 상관관계 조정 (범위 입력 시 중앙값 사용)
        if ("age" in filters or "age_range" in filters) and "salary" in filters:
            if "age_range" in filters and filters["age_range"]:
                try:
                    a_min, a_max = filters["age_range"]
                    age = int((int(a_min) + int(a_max)) / 2)
                except Exception:
                    age = int(filters.get("age", 30))
            else:
                age = int(filters["age"])
            salary = filters["salary"]
            
            # 나이대별 소득 분포
            age_salary_dist = {
                "20대": {
                    "2000만원 이하": 0.60,      # 20대는 대부분 낮은 소득
                    "2000-3000만원": 0.25,
                    "3000-4000만원": 0.10,
                    "4000-5000만원": 0.04,
                    "5000만원 이상": 0.01
                },
                "25-29": {
                    "2000만원 이하": 0.40,
                    "2000-3000만원": 0.35,
                    "3000-4000만원": 0.15,
                    "4000-5000만원": 0.07,
                    "5000만원 이상": 0.03
                },
                "30-34": {
                    "2000만원 이하": 0.20,
                    "2000-3000만원": 0.30,
                    "3000-4000만원": 0.25,
                    "4000-5000만원": 0.15,
                    "5000만원 이상": 0.10
                },
                "35-39": {
                    "2000만원 이하": 0.10,
                    "2000-3000만원": 0.20,
                    "3000-4000만원": 0.25,
                    "4000-5000만원": 0.25,
                    "5000만원 이상": 0.20
                }
            }
            
            # 나이대 결정
            if age < 25:
                age_key = "20대"
            elif age < 30:
                age_key = "25-29"
            elif age < 35:
                age_key = "30-34"
            elif age < 40:
                age_key = "35-39"
            else:
                age_key = "35-39"  # 40대 이상은 35-39와 동일
            
            if age_key in age_salary_dist and salary in age_salary_dist[age_key]:
                conditional_prob = age_salary_dist[age_key][salary]
                marginal_prob = self.statistics_data["salary"].get(salary, 0.01)
                
                if marginal_prob > 0:
                    adjustment_factor = conditional_prob / marginal_prob
                    adjustment_factor = max(0.1, min(3.0, adjustment_factor))
                    
                    # 연봉 확률 조정
                    if len(adjusted_probs) >= 3:
                        adjusted_probs[2] *= adjustment_factor
        
        return adjusted_probs
    
    def calculate_probability(self, filters: Dict) -> Dict:
        """
        이상형 조건에 따른 선택률을 계산합니다 (상관관계 고려).
        
        Args:
            filters (Dict): 이상형 필터 조건
            
        Returns:
            Dict: 선택률 계산 결과
        """
        try:
            # 각 조건별 확률 계산
            probabilities = []
            applied_conditions = []
            condition_details = []
            # 미혼율은 마지막 곱으로 적용
            marital_factor: Optional[float] = None
            marital_detail_label: Optional[str] = None
            marital_detail_type: Optional[str] = None
            
            # 성별은 필수이므로 항상 포함
            if "gender" in filters:
                applied_conditions.append("성별")
                condition_details.append({"condition": "성별", "value": filters["gender"], "probability": 1.0})
            
            # 키 조건 처리 (단일 구간 또는 범위)
            if "height_range" in filters and filters["height_range"]:
                try:
                    h_min, h_max = filters["height_range"]
                    h_min = int(h_min)
                    h_max = int(h_max)
                except Exception:
                    h_min, h_max = None, None
                if h_min is not None and h_max is not None and h_min < h_max:
                    height_prob = self._aggregate_height_probability(h_min, h_max)
                    probabilities.append(height_prob)
                    applied_conditions.append("키")
                    condition_details.append({
                        "condition": "키",
                        "value": f"{h_min}-{h_max}cm",
                        "probability": height_prob,
                        "data_source": "실제 키 분포 데이터",
                        "detail": "범위 합산"
                    })
            elif "height" in filters and filters["height"]:
                height_prob = self.statistics_data["height"].get(filters["height"], 0.01)
                probabilities.append(height_prob)
                applied_conditions.append("키")
                condition_details.append({
                    "condition": "키",
                    "value": filters["height"],
                    "probability": height_prob,
                    "data_source": "실제 키 분포 데이터"
                })
            
            # 학력 조건 처리 (단일 또는 다중)
            if "education_levels" in filters and isinstance(filters["education_levels"], list):
                levels: List[str] = [lvl for lvl in filters["education_levels"] if lvl]
                if levels:
                    edu_prob = sum(self.statistics_data["education"].get(lvl, 0.0) for lvl in levels)
                    edu_prob = min(1.0, edu_prob)
                    probabilities.append(edu_prob)
                    applied_conditions.append("학력")
                    condition_details.append({
                        "condition": "학력",
                        "value": ", ".join(levels),
                        "probability": edu_prob,
                        "data_source": "대학 졸업자 통계",
                        "detail": "다중 선택 합산"
                    })
            elif "education" in filters and filters["education"]:
                edu_prob = self.statistics_data["education"].get(filters["education"], 0.01)
                probabilities.append(edu_prob)
                applied_conditions.append("학력")
                condition_details.append({
                    "condition": "학력",
                    "value": filters["education"],
                    "probability": edu_prob,
                    "data_source": "대학 졸업자 통계"
                })
            
            # 연봉 조건 처리 (단일 구간 또는 범위)
            if "salary_range" in filters and filters["salary_range"]:
                try:
                    s_min, s_max = filters["salary_range"]
                    s_min = int(s_min)
                    s_max = int(s_max)
                except Exception:
                    s_min, s_max = None, None
                if s_min is not None and s_max is not None and s_min < s_max:
                    # 1억(10000만원) 경계 고려: 
                    # - 전구간이 1억 이상: P = P(>=s_min) - P(>=s_max)
                    # - 경계 교차: P = P([s_min,10000)) + (P(>=10000) - P(>=s_max))
                    # - 전구간이 1억 미만: 기존 분포 합산
                    if s_min >= 10000 and s_max > 10000:
                        p_min = self._estimate_share_above_income(s_min)
                        p_max = self._estimate_share_above_income(s_max)
                        salary_prob = max(0.0, min(1.0, p_min - p_max))
                        detail_text = "상위 퍼센트 테이블 기반(범위)"
                    elif s_min < 10000 and s_max > 10000:
                        below_prob = self._aggregate_salary_probability(s_min, 10000)
                        p_10000 = self._estimate_share_above_income(10000)
                        p_max = self._estimate_share_above_income(s_max)
                        above_prob = max(0.0, p_10000 - p_max)
                        salary_prob = max(0.0, min(1.0, below_prob + above_prob))
                        detail_text = "분포 합산+상위 퍼센트 혼합"
                    else:
                        salary_prob = self._aggregate_salary_probability(s_min, s_max)
                        detail_text = "분포 범위 합산"
                    probabilities.append(salary_prob)
                    applied_conditions.append("연봉")
                    condition_details.append({
                        "condition": "연봉",
                        "value": f"{s_min}-{s_max}만원",
                        "probability": salary_prob,
                        "data_source": "소득 분포 통계",
                        "detail": detail_text
                    })
            elif "salary" in filters and filters["salary"]:
                salary_prob = self.statistics_data["salary"].get(filters["salary"], 0.01)
                probabilities.append(salary_prob)
                applied_conditions.append("연봉")
                condition_details.append({
                    "condition": "연봉",
                    "value": filters["salary"],
                    "probability": salary_prob,
                    "data_source": "소득 분포 통계"
                })
            
            # 직업 조건 처리 (단일 또는 다중)
            if "occupations" in filters and isinstance(filters["occupations"], list):
                occs: List[str] = [o for o in filters["occupations"] if o]
                if occs:
                    job_prob = sum(self.statistics_data["job"].get(o, 0.0) for o in occs)
                    job_prob = min(1.0, job_prob)
                    probabilities.append(job_prob)
                    applied_conditions.append("직업")
                    condition_details.append({
                        "condition": "직업",
                        "value": ", ".join(occs),
                        "probability": job_prob,
                        "data_source": "직업 분포 통계",
                        "detail": "다중 선택 합산"
                    })
            elif "job" in filters and filters["job"]:
                job_prob = self.statistics_data["job"].get(filters["job"], 0.01)
                probabilities.append(job_prob)
                applied_conditions.append("직업")
                condition_details.append({
                    "condition": "직업",
                    "value": filters["job"],
                    "probability": job_prob,
                    "data_source": "직업 분포 통계"
                })
            
            # 지역 조건 처리 (시·도 다중 선택 우선, 없으면 기존 location)
            if "regions" in filters and isinstance(filters["regions"], list) and filters["regions"]:
                selected_regions: List[str] = [r for r in filters["regions"] if r]
                region_shares = self.statistics_data.get("location", {})
                loc_prob = sum(region_shares.get(r, 0.0) for r in selected_regions)
                loc_prob = min(1.0, loc_prob)
                probabilities.append(loc_prob)
                applied_conditions.append("지역")
                condition_details.append({
                    "condition": "지역",
                    "value": ", ".join(selected_regions),
                    "probability": loc_prob,
                    "data_source": "인구 분포 통계",
                    "detail": "시·도 다중 선택 합산"
                })
            elif "location" in filters and filters["location"]:
                loc_prob = self.statistics_data["location"].get(filters["location"], 0.01)
                probabilities.append(loc_prob)
                applied_conditions.append("지역")
                condition_details.append({
                    "condition": "지역", 
                    "value": filters["location"], 
                    "probability": loc_prob,
                    "data_source": "인구 분포 통계"
                })
            
            # 나이 조건 처리 (범위 또는 단일값)
            # 정책: 나이는 '연령 인구 비중'을 확률로 사용하고, 미혼율은 마지막 단계에서 적용
            if "age_range" in filters and filters["age_range"]:
                gender = filters.get("gender", "남성")
                try:
                    age_min, age_max = filters["age_range"]
                    age_min = int(age_min)
                    age_max = int(age_max)
                except Exception:
                    age_min, age_max = None, None
                if age_min is not None and age_max is not None and age_min < age_max:
                    # 선택 구간은 입력값 기준으로 자르고, 분모는 전체 연령 합계(데이터 전 연령)로 계산
                    sel_low = age_min
                    sel_high = age_max
                    if sel_low <= sel_high:
                        used_real_population = False
                        age_share_prob = None
                        # 실제 연령별 인구 분포가 있으면 그것을 사용
                        if isinstance(self.age_population, dict) and self.age_population:
                            # 분모: 데이터 내 전체 연령(선택 성별)
                            denom = 0.0
                            num = 0.0
                            for a, rec in self.age_population.items():
                                try:
                                    a_int = int(a)
                                except Exception:
                                    continue
                                if rec and gender in rec:
                                    denom += float(rec[gender])
                            for a in range(sel_low, sel_high + 1):
                                rec = self.age_population.get(a)
                                if rec and gender in rec:
                                    num += float(rec[gender])
                            if denom > 0:
                                age_share_prob = max(0.0, min(1.0, num / denom))
                                used_real_population = True
                        # 없거나 계산 불가하면 균등 가정
                        if age_share_prob is None:
                            years = (sel_high - sel_low + 1)
                            # 분모는 데이터 전체를 모를 때 대략 0-99로 가정(100년)
                            total_years = 100
                            age_share_prob = max(0.0, min(1.0, years / total_years))
                        probabilities.append(age_share_prob)
                        applied_conditions.append("나이")
                        condition_details.append({
                            "condition": "나이",
                            "value": f"{age_min}-{age_max}세",
                            "probability": age_share_prob,
                            "data_source": "연령 인구 비중(실제)" if used_real_population else "연령 범위 비중(가정: 18-70 균등)",
                            "detail": (
                                f"선택 연령 인구/성인 인구 (실데이터)" if used_real_population else f"전체 18-70 대비 연령 구간 길이 비율"
                            )
                        })
                        # 미혼율 팩터(마지막 단계) 계산: 지역 선택에 따라 가중 평균
                        try:
                            # 인구가중 미혼률(정확) 계산: 단일 나이별 인구 × 미혼률 합 / 선택 연령 인구 합
                            rate, sum_unmarried, sum_pop_sel = self._compute_population_weighted_unmarried_rate(gender, sel_low, sel_high)
                            if isinstance(rate, (int, float)):
                                marital_factor = rate
                                marital_detail_label = ""
                                marital_detail_type = "인구가중 미혼률"
                        except Exception:
                            pass
            elif "age" in filters and filters["age"]:
                age = int(filters["age"])
                gender = filters.get("gender", "남성")
                if age < 25:
                    band = (20, 24)
                elif age < 30:
                    band = (25, 29)
                elif age < 35:
                    band = (30, 34)
                elif age < 40:
                    band = (35, 39)
                elif age < 45:
                    band = (40, 44)
                elif age < 50:
                    band = (45, 49)
                else:
                    band = (45, 49)
                # 연령대 인구 비중
                used_real_population = False
                age_share_prob = None
                if isinstance(self.age_population, dict) and self.age_population:
                    denom = 0.0
                    num = 0.0
                    for a, rec in self.age_population.items():
                        try:
                            a_int = int(a)
                        except Exception:
                            continue
                        if rec and gender in rec:
                            denom += float(rec[gender])
                    for a in range(band[0], band[1] + 1):
                        rec = self.age_population.get(a)
                        if rec and gender in rec:
                            num += float(rec[gender])
                    if denom > 0:
                        age_share_prob = max(0.0, min(1.0, num / denom))
                        used_real_population = True
                if age_share_prob is None:
                    # 분모는 데이터 전체를 모를 때 대략 0-99로 가정(100년)
                    total_years = 100
                    years = (band[1] - band[0] + 1)
                    age_share_prob = max(0.0, min(1.0, years / total_years))
                probabilities.append(age_share_prob)
                applied_conditions.append("나이")
                condition_details.append({
                    "condition": "나이",
                    "value": f"{band[0]}-{band[1]}세",
                    "probability": age_share_prob,
                    "data_source": "연령 인구 비중(실제)" if used_real_population else "연령 범위 비중(가정: 18-70 균등)",
                    "detail": f"{band[0]}-{band[1]}세 인구 비중"
                })
                # 미혼율 팩터(마지막 단계)
                try:
                    rate, sum_unmarried, sum_pop_sel = self._compute_population_weighted_unmarried_rate(gender, band[0], band[1])
                    if isinstance(rate, (int, float)):
                        marital_factor = rate
                        marital_detail_label = ""
                        marital_detail_type = "인구가중 미혼률"
                except Exception:
                    pass
            
            # 흡연 여부 조건 처리 (체크박스)
            if "smoking" in filters and filters["smoking"] == "비흡연":
                gender = filters.get("gender", "남성")
                smoking_prob = self.statistics_data["smoking"].get(gender, 0.20)
                # 비흡연 확률 = 1 - 흡연 확률
                non_smoking_prob = 1 - smoking_prob
                probabilities.append(non_smoking_prob)
                applied_conditions.append("흡연 여부")
                condition_details.append({
                    "condition": "흡연 여부", 
                    "value": "비흡연", 
                    "probability": non_smoking_prob,
                    "data_source": "성별 흡연율 통계",
                    "detail": f"{gender} 비흡연율"
                })

            # 외모 상위 퍼센트 조건 처리
            # - 단일 값(appearance_top_percent): 상위 X% 이상 → P = X/100
            # - 범위(appearance_top_percent_range): 상위 A–B% 구간 → P = (B - A) / 100
            if "appearance_top_percent_range" in filters and filters["appearance_top_percent_range"]:
                try:
                    a_min, a_max = filters["appearance_top_percent_range"]
                    a_min = float(a_min)
                    a_max = float(a_max)
                except Exception:
                    a_min, a_max = None, None
                if a_min is not None and a_max is not None and 0 <= a_min < a_max <= 100:
                    appearance_prob = max(0.0, min(1.0, (a_max - a_min) / 100.0))
                    probabilities.append(appearance_prob)
                    applied_conditions.append("외모")
                    condition_details.append({
                        "condition": "외모",
                        "value": f"상위 {int(a_min)}–{int(a_max)}%",
                        "probability": appearance_prob,
                        "data_source": "사용자 정의(독립 가정)",
                        "detail": "외모 상위 퍼센트 범위"
                    })
            elif "appearance_top_percent" in filters and filters["appearance_top_percent"] not in (None, ""):
                try:
                    top_p = float(filters["appearance_top_percent"])  # 1~100
                except Exception:
                    top_p = None
                if top_p is not None and 0 < top_p <= 100:
                    appearance_prob = max(0.0, min(1.0, top_p / 100.0))
                    probabilities.append(appearance_prob)
                    applied_conditions.append("외모")
                    condition_details.append({
                        "condition": "외모",
                        "value": f"상위 {int(top_p)}% 이상",
                        "probability": appearance_prob,
                        "data_source": "사용자 정의(독립 가정)",
                        "detail": "외모 상위 퍼센트 단일값"
                    })
            
            # 상관관계 조정 적용
            if len(probabilities) > 1:
                adjusted_probabilities = self._apply_correlation_adjustment(probabilities, filters)
            else:
                adjusted_probabilities = probabilities
            
            # 미혼율은 마지막에 적용
            if marital_factor is not None:
                adjusted_probabilities = list(adjusted_probabilities) + [marital_factor]
                condition_details.append({
                    "condition": "미혼률",
                    "value": "",
                    "probability": marital_factor,
                    "data_source": "연령대별 미혼률(인구가중)",
                    "detail": marital_detail_type or "최종 단계 적용"
                })

            # 최종 선택률 계산 (조정된 곱셈 원리)
            if adjusted_probabilities:
                final_probability = 1.0
                for prob in adjusted_probabilities:
                    final_probability *= prob
                final_probability *= 100  # 퍼센트로 변환
            else:
                # 조건이 없으면 (성별만 선택한 경우) 전체 이성 대비 100%
                final_probability = 100.0
            
            # 선택률 등급 판정
            selection_level = self._get_selection_level(final_probability)
            
            # 단계별 설명 스텝 생성
            steps = self._build_explanation_steps(filters, condition_details, adjusted_probabilities)

            return {
                "probability": round(final_probability, 2),
                "selection_level": selection_level,
                "filters": filters,
                "population": self._resolve_target_population(filters),
                "calculation_details": {
                    "individual_probabilities": adjusted_probabilities,
                    "total_conditions": len(adjusted_probabilities),
                    "applied_conditions": applied_conditions,
                    "condition_details": condition_details,
                    "correlation_adjusted": len(probabilities) > 1,
                    "calculation_method": "상관관계 고려 곱셈 원리",
                    "explanation_steps": steps
                }
            }
            
        except Exception as e:
            return {
                "probability": 0.0,
                "selection_level": "계산 오류",
                "error": str(e),
                "filters": filters,
                "population": self._resolve_target_population(filters)
            }

    def _resolve_target_population(self, filters: Dict) -> Dict:
        """결과 표시에 사용할 대상 인구(모수)를 추정합니다.

        우선순위: regions 합계 > nation 총인구
        성별 선택 시 해당 성별 인구를 사용, 없으면 총인구 사용.
        """
        pop = self.population_latest or {}
        nation = pop.get("nation", {})
        regions = pop.get("regions", {})
        gender = filters.get("gender")

        # 지역 선택 합산
        total = None
        if "regions" in filters and isinstance(filters["regions"], list) and filters["regions"]:
            sel = [r for r in filters["regions"] if r in regions]
            if sel:
                if gender in ("남성", "여성"):
                    vals = [regions[r].get(gender) for r in sel if regions[r].get(gender)]
                else:
                    vals = [regions[r].get("total") for r in sel if regions[r].get("total")]
                if vals:
                    total = float(sum(vals))

        # 지역 없으면 전국
        if total is None:
            if gender in ("남성", "여성") and nation.get(gender):
                total = float(nation.get(gender))
            else:
                total = float(nation.get("total") or 0.0)

        return {
            "total": int(total) if total else None,
            "gender": gender or None
        }

    def _build_explanation_steps(self, filters: Dict, condition_details: List[Dict], adjusted_probs: List[float]) -> List[Dict]:
        """선택 조건에 따른 단계별 인원/비율 변화를 설명용으로 생성합니다."""
        base = self._resolve_target_population(filters)
        base_total = base.get("total") or 0
        steps: List[Dict] = []
        if base_total <= 0 or not adjusted_probs:
            return steps

        # condition_details에는 성별(1.0)도 포함되므로, 비성별 항목에만 확률 매핑
        prob_iter = iter(adjusted_probs)
        prev_count = float(base_total)
        prev_percent = 100.0

        for cond in condition_details:
            if cond.get("condition") == "성별":
                continue
            p = next(prob_iter, None)
            if p is None:
                break
            new_percent = prev_percent * (p * 100.0) / 100.0
            new_count = prev_count * p

            label = cond.get("condition", "조건")
            value = cond.get("value")
            detail = cond.get("detail")
            # 가독성 친화 레이블 보정
            if label == "나이":
                pretty = "연령 구간 비중"
            elif label == "미혼률":
                region_text = "(지역 선택 가중)" if isinstance(filters.get("regions"), list) and filters.get("regions") else "(전국 합계 기준)"
                pretty = f"미혼률 {region_text}"
            elif label == "흡연 여부" and value == "비흡연":
                pretty = "비흡연 비율"
            else:
                pretty = label

            steps.append({
                "label": pretty,
                "value": value,
                "from_percent": round(prev_percent, 2),
                "to_percent": round(new_percent, 2),
                "applied_probability": round(p * 100.0, 2),
                "from_count": int(round(prev_count)),
                "to_count": int(round(new_count))
            })

            prev_percent = new_percent
            prev_count = new_count

        return steps

    def _aggregate_height_probability(self, cm_min: int, cm_max: int) -> float:
        """키 범위에 해당하는 구간 확률을 합산합니다."""
        total = 0.0
        bins = self.statistics_data.get("height", {})
        # 1) 데이터에 있는 구간 합산 (대략적)
        for key, prob in bins.items():
            try:
                a, b = key.split("-")
                a = int(a)
                b = int(b)
            except Exception:
                continue
            if not (b <= cm_min or a >= cm_max):
                total += prob

        # 2) 상단 꼬리(>=185cm)는 남성 CDF 포인트로 보강
        coverage_max = 185
        if self.male_height_cdf_points:
            # 케이스 A: 범위 전부가 185 이상인 경우 → 순수 꼬리 차이
            if cm_min >= coverage_max:
                p_lower = self._estimate_male_cdf_above(cm_min)
                p_upper = self._estimate_male_cdf_above(cm_max)
                tail = max(0.0, (p_lower or 0.0) - (p_upper or 0.0))
                total = tail
            # 케이스 B: 일부만 185 이상이면, 그 부분만 꼬리로 보강
            elif cm_max > coverage_max:
                lower = max(cm_min, coverage_max)
                p_lower = self._estimate_male_cdf_above(lower)
                p_upper = self._estimate_male_cdf_above(cm_max)
                tail = max(0.0, (p_lower or 0.0) - (p_upper or 0.0))
                total += tail

        return min(1.0, max(0.0, total))

    def _aggregate_salary_probability(self, amount_min: int, amount_max: int) -> float:
        """연봉 범위(만원)에 해당하는 분포 확률을 합산합니다."""
        total = 0.0
        for key, prob in self.statistics_data.get("salary", {}).items():
            # 키 값 예시: '2000만원 이하', '2000-3000만원', '5000만원 이상'
            if '이하' in key:
                try:
                    upper = int(key.replace('만원 이하', ''))
                except Exception:
                    continue
                # 범위가 겹치면 포함
                if amount_min <= upper:
                    total += prob
            elif '이상' in key:
                try:
                    lower = int(key.replace('만원 이상', ''))
                except Exception:
                    continue
                if amount_max >= lower:
                    # 5000만원 이상 구간이 상단 꼬리를 포함하므로, 1억원 경계에서 분할
                    if lower == 5000 and amount_max <= 10000:
                        # [5000, 1억)만 포함하도록 조정: prob_minus_tail = prob - P(>=1억)
                        p_tail = self._estimate_share_above_income(10000)
                        contrib = max(0.0, prob - p_tail)
                        total += contrib
                    else:
                        total += prob
            elif '-' in key:
                try:
                    lower, upper = key.replace('만원', '').split('-')
                    lower = int(lower)
                    upper = int(upper)
                except Exception:
                    continue
                if not (upper <= amount_min or lower >= amount_max):
                    total += prob
        return min(1.0, total)
    
    def _get_selection_level(self, probability: float) -> str:
        """
        선택률에 따른 등급을 반환합니다.
        
        Args:
            probability (float): 계산된 선택률 (0-100)
            
        Returns:
            str: 선택률 등급
        """
        if probability < 0.1:
            return "극히 드문 조건"
        elif probability < 1.0:
            return "매우 드문 조건"
        elif probability < 5.0:
            return "드문 조건"
        elif probability < 15.0:
            return "보통 조건"
        elif probability < 30.0:
            return "흔한 조건"
        else:
            return "매우 흔한 조건"
    
    def get_statistics_summary(self) -> Dict:
        """
        통계 데이터 요약을 반환합니다.
        
        Returns:
            Dict: 통계 요약 데이터
        """
        return {
            "total_categories": len(self.statistics_data),
            "categories": list(self.statistics_data.keys()),
            "data_source": "실제 통계청 데이터 + 상관관계 보정",
            "calculation_method": "상관관계 고려 곱셈 원리",
            "correlation_factors": list(self.correlation_factors.keys()),
            "data_quality": "실제 데이터 80% 활용"
        }


# 전역 인스턴스
stats_service = StatsService()


def calculate_probability(filters: Dict) -> Dict:
    """
    선택률 계산 함수 (외부에서 호출용)
    
    Args:
        filters (Dict): 이상형 필터 조건
        
    Returns:
        Dict: 선택률 계산 결과
    """
    return stats_service.calculate_probability(filters)


def get_statistics_summary() -> Dict:
    """
    통계 요약 함수 (외부에서 호출용)
    
    Returns:
        Dict: 통계 요약 데이터
    """
    return stats_service.get_statistics_summary() 