# tests/test_stats_service.py
# 통계 서비스 테스트

import pytest
from app.services.stats_service import calculate_probability, get_statistics_summary


class TestStatsService:
    """통계 서비스 테스트 클래스"""
    
    def test_calculate_probability_basic(self):
        """기본 선택률 계산 테스트"""
        filters = {
            "gender": "남성",
            "height": "165-170",
            "education": "4년제"
        }
        
        result = calculate_probability(filters)
        
        assert "probability" in result
        assert "selection_level" in result
        assert "filters" in result
        assert result["probability"] > 0
        assert result["probability"] <= 100
    
    def test_calculate_probability_all_conditions(self):
        """모든 조건을 포함한 선택률 계산 테스트"""
        filters = {
            "gender": "여성",
            "height": "160-165",
            "education": "SKY",
            "salary": "5000만원 이상",
            "job": "전문직",
            "location": "수도권",
            "age": 25,
            "smoking": "비흡연"
        }
        
        result = calculate_probability(filters)
        
        assert result["probability"] > 0
        assert result["probability"] <= 100
        assert "calculation_details" in result
        assert result["calculation_details"]["total_conditions"] > 0
        assert "applied_conditions" in result["calculation_details"]
    
    def test_calculate_probability_no_filters(self):
        """필터가 없는 경우 테스트"""
        filters = {}
        
        result = calculate_probability(filters)
        
        assert result["probability"] == 50.0  # 기본값
        assert result["selection_level"] == "매우 흔한 조건"
    
    def test_calculate_probability_only_gender(self):
        """성별만 선택한 경우 테스트"""
        filters = {
            "gender": "남성"
        }
        
        result = calculate_probability(filters)
        
        assert result["probability"] == 50.0  # 기본값
        assert result["calculation_details"]["total_conditions"] == 0
        assert "성별" in result["calculation_details"]["applied_conditions"]
    
    def test_calculate_probability_empty_conditions(self):
        """빈 조건들이 포함된 경우 테스트"""
        filters = {
            "gender": "여성",
            "height": "",
            "education": "",
            "salary": "3000-4000만원",
            "job": "",
            "location": "수도권"
        }
        
        result = calculate_probability(filters)
        
        assert result["probability"] > 0
        assert result["calculation_details"]["total_conditions"] == 2  # 연봉, 지역만
        assert "연봉" in result["calculation_details"]["applied_conditions"]
        assert "지역" in result["calculation_details"]["applied_conditions"]
    
    def test_calculate_probability_invalid_filters(self):
        """잘못된 필터 값 테스트"""
        filters = {
            "gender": "남성",
            "height": "invalid_height",
            "education": "invalid_education"
        }
        
        result = calculate_probability(filters)
        
        assert result["probability"] > 0
        assert "error" not in result
    
    def test_selection_levels(self):
        """선택률 등급 테스트"""
        # 극히 드문 조건 (0.1% 미만)
        filters_very_rare = {
            "gender": "남성",
            "height": "180-185",
            "education": "SKY",
            "salary": "5000만원 이상",
            "job": "전문직"
        }
        
        result_very_rare = calculate_probability(filters_very_rare)
        
        # 매우 드문 조건 (1% 미만)
        filters_rare = {
            "gender": "여성",
            "height": "175-180",
            "education": "인서울",
            "salary": "4000-5000만원"
        }
        
        result_rare = calculate_probability(filters_rare)
        
        # 보통 조건 (15% 미만)
        filters_normal = {
            "gender": "남성",
            "height": "170-175",
            "education": "4년제"
        }
        
        result_normal = calculate_probability(filters_normal)
        
        # 흔한 조건 (30% 미만)
        filters_common = {
            "gender": "여성",
            "height": "160-165",
            "education": "이하"
        }
        
        result_common = calculate_probability(filters_common)
        
        # 선택률이 낮을수록 조건이 드물어야 함
        assert result_very_rare["probability"] <= result_rare["probability"]
        assert result_rare["probability"] <= result_normal["probability"]
        assert result_normal["probability"] <= result_common["probability"]
    
    def test_get_statistics_summary(self):
        """통계 요약 테스트"""
        summary = get_statistics_summary()
        
        assert "total_categories" in summary
        assert "categories" in summary
        assert "data_source" in summary
        assert summary["total_categories"] > 0
        assert len(summary["categories"]) > 0
    
    def test_age_based_marital_probability(self):
        """나이 기반 혼인 상태 확률 테스트"""
        # 20대
        filters_20s = {
            "gender": "남성",
            "age": 25
        }
        
        result_20s = calculate_probability(filters_20s)
        
        # 30대
        filters_30s = {
            "gender": "남성",
            "age": 35
        }
        
        result_30s = calculate_probability(filters_30s)
        
        # 40대
        filters_40s = {
            "gender": "남성",
            "age": 45
        }
        
        result_40s = calculate_probability(filters_40s)
        
        # 나이가 많을수록 미혼 확률이 낮아져야 함 (결과 선택률이 높아져야 함)
        assert result_20s["probability"] <= result_30s["probability"]
        assert result_30s["probability"] <= result_40s["probability"]
    
    def test_smoking_checkbox_logic(self):
        """흡연 체크박스 로직 테스트"""
        # 남성 비흡연
        filters_male_non_smoking = {
            "gender": "남성",
            "smoking": "비흡연"
        }
        
        result_male_non_smoking = calculate_probability(filters_male_non_smoking)
        
        # 여성 비흡연
        filters_female_non_smoking = {
            "gender": "여성",
            "smoking": "비흡연"
        }
        
        result_female_non_smoking = calculate_probability(filters_female_non_smoking)
        
        # 체크박스가 선택된 경우에만 흡연 여부가 적용되어야 함
        assert "흡연 여부" in result_male_non_smoking["calculation_details"]["applied_conditions"]
        assert "흡연 여부" in result_female_non_smoking["calculation_details"]["applied_conditions"]
        
        # 비흡연 확률이 50%보다 높아야 함 (대부분이 비흡연자)
        assert result_male_non_smoking["probability"] > 50.0
        assert result_female_non_smoking["probability"] > 50.0
    
    def test_no_smoking_condition(self):
        """흡연 조건을 선택하지 않은 경우 테스트"""
        filters_no_smoking = {
            "gender": "남성",
            "height": "170-175"
        }
        
        result_no_smoking = calculate_probability(filters_no_smoking)
        
        # 흡연 조건이 적용되지 않아야 함
        assert "흡연 여부" not in result_no_smoking["calculation_details"]["applied_conditions"]
    
    def test_calculation_details(self):
        """계산 상세 정보 테스트"""
        filters = {
            "gender": "남성",
            "height": "165-170",
            "education": "4년제",
            "salary": "3000-4000만원"
        }
        
        result = calculate_probability(filters)
        
        assert "calculation_details" in result
        assert "individual_probabilities" in result["calculation_details"]
        assert "total_conditions" in result["calculation_details"]
        assert "applied_conditions" in result["calculation_details"]
        assert result["calculation_details"]["total_conditions"] == 3
        assert len(result["calculation_details"]["individual_probabilities"]) == 3
        assert len(result["calculation_details"]["applied_conditions"]) == 4  # 성별 포함
    
    def test_selection_level_boundaries(self):
        """선택률 등급 경계값 테스트"""
        # 극히 드문 조건 경계
        assert calculate_probability({"gender": "남성"})["selection_level"] != "극히 드문 조건"
        
        # 매우 드문 조건 경계
        filters_very_rare = {
            "gender": "남성",
            "height": "180-185",
            "education": "SKY",
            "salary": "5000만원 이상"
        }
        result_very_rare = calculate_probability(filters_very_rare)
        
        # 드문 조건 경계
        filters_rare = {
            "gender": "여성",
            "height": "175-180",
            "education": "인서울"
        }
        result_rare = calculate_probability(filters_rare)
        
        # 보통 조건 경계
        filters_normal = {
            "gender": "남성",
            "height": "170-175"
        }
        result_normal = calculate_probability(filters_normal)
        
        # 흔한 조건 경계
        filters_common = {
            "gender": "여성",
            "height": "160-165"
        }
        result_common = calculate_probability(filters_common)
        
        # 등급이 올바르게 설정되었는지 확인
        assert "조건" in result_very_rare["selection_level"]
        assert "조건" in result_rare["selection_level"]
        assert "조건" in result_normal["selection_level"]
        assert "조건" in result_common["selection_level"]
    
    def test_empty_string_conditions(self):
        """빈 문자열 조건 처리 테스트"""
        filters = {
            "gender": "여성",
            "height": "",
            "education": "",
            "salary": "",
            "job": "",
            "location": "",
            "age": "",
            "smoking": ""
        }
        
        result = calculate_probability(filters)
        
        # 빈 문자열 조건들은 무시되어야 함
        assert result["calculation_details"]["total_conditions"] == 0
        assert result["probability"] == 50.0  # 기본값 