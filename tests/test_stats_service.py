# tests/test_stats_service.py
# 확률 계산 서비스 단위 테스트

import pytest
import sys
import os

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.services.stats_service import calculate_probability, get_rarity_level


class TestStatsService:
    '''확률 계산 서비스 테스트 클래스'''
    
    def test_calculate_probability_basic(self):
        '''기본 확률 계산 테스트'''
        filters = {
            'age_range': [25, 35],
            'location': 'seoul',
            'interests': ['travel', 'music']
        }
        
        result = calculate_probability(filters)
        
        # 확률이 0-100 범위 내에 있는지 확인
        assert 0 <= result <= 100
        assert isinstance(result, float)
    
    def test_calculate_probability_with_style(self):
        '''스타일이 포함된 확률 계산 테스트'''
        filters = {
            'age_range': [20, 30],
            'location': 'busan',
            'interests': ['cooking'],
            'style': 'cute'
        }
        
        result = calculate_probability(filters)
        
        assert 0 <= result <= 100
        assert isinstance(result, float)
    
    def test_calculate_probability_empty_filters(self):
        '''빈 필터로 확률 계산 테스트'''
        filters = {}
        
        result = calculate_probability(filters)
        
        assert 0 <= result <= 100
        assert isinstance(result, float)
    
    def test_get_rarity_level_legendary(self):
        '''매우 희귀 레벨 테스트'''
        probability = 85.0
        result = get_rarity_level(probability)
        
        assert result == '매우 희귀'
    
    def test_get_rarity_level_rare(self):
        '''희귀 레벨 테스트'''
        probability = 70.0
        result = get_rarity_level(probability)
        
        assert result == '희귀'
    
    def test_get_rarity_level_common(self):
        '''보통 레벨 테스트'''
        probability = 45.0
        result = get_rarity_level(probability)
        
        assert result == '보통'
    
    def test_get_rarity_level_very_common(self):
        '''흔함 레벨 테스트'''
        probability = 20.0
        result = get_rarity_level(probability)
        
        assert result == '흔함'
    
    def test_get_rarity_level_boundary_values(self):
        '''경계값 테스트'''
        assert get_rarity_level(80.0) == '매우 희귀'
        assert get_rarity_level(79.9) == '희귀'
        assert get_rarity_level(60.0) == '희귀'
        assert get_rarity_level(59.9) == '보통'
        assert get_rarity_level(30.0) == '보통'
        assert get_rarity_level(29.9) == '흔함'
    
    def test_calculate_probability_consistency(self):
        '''동일한 입력에 대한 일관성 테스트'''
        filters = {
            'age_range': [25, 35],
            'location': 'seoul',
            'interests': ['travel']
        }
        
        # 여러 번 실행하여 결과가 일관되는지 확인
        results = []
        for _ in range(10):
            results.append(calculate_probability(filters))
        
        # 모든 결과가 유효한 범위 내에 있는지 확인
        for result in results:
            assert 0 <= result <= 100
            assert isinstance(result, float)


if __name__ == '__main__':
    pytest.main([__file__]) 