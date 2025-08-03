# backend/app/utils/validators.py
# 입력 데이터 검증 유틸리티

from typing import Dict, List, Any


def validate_ideal_type_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    '''
    이상형 데이터 유효성을 검증합니다.
    
    Args:
        data (Dict[str, Any]): 검증할 데이터
        
    Returns:
        tuple[bool, List[str]]: (유효성 여부, 오류 메시지 리스트)
    '''
    errors = []
    
    # 필수 필드 검증
    required_fields = ['age_range', 'location', 'interests']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} 필드는 필수입니다.')
    
    # 나이 범위 검증
    if 'age_range' in data and data['age_range']:
        age_range = data['age_range']
        if not isinstance(age_range, (list, tuple)) or len(age_range) != 2:
            errors.append('나이 범위는 [최소, 최대] 형태로 입력해주세요.')
        elif age_range[0] < 18 or age_range[1] > 100:
            errors.append('나이 범위는 18세 이상 100세 이하여야 합니다.')
    
    # 관심사 검증
    if 'interests' in data and data['interests']:
        interests = data['interests']
        if not isinstance(interests, list):
            errors.append('관심사는 리스트 형태로 입력해주세요.')
        elif len(interests) > 10:
            errors.append('관심사는 최대 10개까지 입력 가능합니다.')
    
    return len(errors) == 0, errors


def sanitize_input(text: str) -> str:
    '''
    사용자 입력을 정리합니다.
    
    Args:
        text (str): 정리할 텍스트
        
    Returns:
        str: 정리된 텍스트
    '''
    if not text:
        return ''
    
    # HTML 태그 제거
    import re
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # 앞뒤 공백 제거
    clean_text = clean_text.strip()
    
    return clean_text 