# backend/app/services/stats_service.py
# 확률 계산 비즈니스 로직

import random


def calculate_probability(filters: dict) -> float:
    '''
    이상형 조건에 맞는 매칭 확률을 계산합니다.
    
    Args:
        filters (dict): 이상형 필터 조건
        
    Returns:
        float: 매칭 확률 (0~100)
    '''
    # TODO: 실제 통계 데이터 기반 확률 계산 로직 구현
    # 현재는 임시로 랜덤 값 반환
    
    base_probability = 50.0  # 기본 확률
    
    # 필터 조건에 따른 확률 조정
    if filters.get('age_range'):
        base_probability += random.uniform(-10, 10)
    
    if filters.get('location'):
        base_probability += random.uniform(-5, 15)
    
    # 확률 범위 제한 (0~100)
    final_probability = max(0.0, min(100.0, base_probability))
    
    return round(final_probability, 2)


def get_rarity_level(probability: float) -> str:
    '''
    확률에 따른 희귀도 레벨을 반환합니다.
    
    Args:
        probability (float): 매칭 확률
        
    Returns:
        str: 희귀도 레벨 ('매우 희귀', '희귀', '보통', '흔함')
    '''
    if probability >= 80:
        return '매우 희귀'
    elif probability >= 60:
        return '희귀'
    elif probability >= 30:
        return '보통'
    else:
        return '흔함' 