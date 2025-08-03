# tests/test_validators.py
# 입력 데이터 검증 유틸리티 단위 테스트

import pytest
import sys
import os

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.utils.validators import validate_ideal_type_data, sanitize_input


class TestValidators:
    '''입력 데이터 검증 테스트 클래스'''
    
    def test_validate_ideal_type_data_valid(self):
        '''유효한 데이터 검증 테스트'''
        data = {
            'age_range': [25, 35],
            'location': 'seoul',
            'interests': ['travel', 'music']
        }
        
        is_valid, errors = validate_ideal_type_data(data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_ideal_type_data_missing_required_fields(self):
        '''필수 필드 누락 테스트'''
        data = {
            'age_range': [25, 35]
            # location과 interests 누락
        }
        
        is_valid, errors = validate_ideal_type_data(data)
        
        assert is_valid is False
        assert len(errors) == 2
        assert 'location' in errors[0]
        assert 'interests' in errors[1]
    
    def test_validate_ideal_type_data_invalid_age_range(self):
        '''잘못된 나이 범위 테스트'''
        data = {
            'age_range': [35, 25],  # 최소가 최대보다 큼
            'location': 'seoul',
            'interests': ['travel']
        }
        
        is_valid, errors = validate_ideal_type_data(data)
        
        assert is_valid is False
        assert len(errors) == 1
        assert '나이 범위' in errors[0]
    
    def test_validate_ideal_type_data_age_out_of_range(self):
        '''나이 범위 초과 테스트'''
        data = {
            'age_range': [15, 25],  # 18세 미만
            'location': 'seoul',
            'interests': ['travel']
        }
        
        is_valid, errors = validate_ideal_type_data(data)
        
        assert is_valid is False
        assert len(errors) == 1
        assert '18세 이상' in errors[0]
    
    def test_validate_ideal_type_data_too_many_interests(self):
        '''관심사 개수 초과 테스트'''
        data = {
            'age_range': [25, 35],
            'location': 'seoul',
            'interests': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']  # 11개
        }
        
        is_valid, errors = validate_ideal_type_data(data)
        
        assert is_valid is False
        assert len(errors) == 1
        assert '최대 10개' in errors[0]
    
    def test_validate_ideal_type_data_invalid_interests_type(self):
        '''관심사 타입 오류 테스트'''
        data = {
            'age_range': [25, 35],
            'location': 'seoul',
            'interests': 'travel'  # 리스트가 아닌 문자열
        }
        
        is_valid, errors = validate_ideal_type_data(data)
        
        assert is_valid is False
        assert len(errors) == 1
        assert '리스트 형태' in errors[0]
    
    def test_sanitize_input_normal_text(self):
        '''일반 텍스트 정리 테스트'''
        text = "  Hello World  "
        result = sanitize_input(text)
        
        assert result == "Hello World"
    
    def test_sanitize_input_with_html_tags(self):
        '''HTML 태그 제거 테스트'''
        text = "<script>alert('xss')</script>Hello <b>World</b>"
        result = sanitize_input(text)
        
        assert result == "alert('xss')Hello World"
        assert "<script>" not in result
        assert "<b>" not in result
        assert "</b>" not in result
    
    def test_sanitize_input_empty_string(self):
        '''빈 문자열 테스트'''
        result = sanitize_input("")
        
        assert result == ""
    
    def test_sanitize_input_none_value(self):
        '''None 값 테스트'''
        result = sanitize_input(None)
        
        assert result == ""
    
    def test_sanitize_input_complex_html(self):
        '''복잡한 HTML 태그 제거 테스트'''
        text = """
        <div class="container">
            <h1>Title</h1>
            <p>This is a <strong>paragraph</strong> with <a href="#">link</a>.</p>
        </div>
        """
        result = sanitize_input(text)
        
        assert "<div>" not in result
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "<strong>" not in result
        assert "<a href=" not in result
        assert "Title" in result
        assert "This is a" in result
        assert "paragraph" in result
        assert "link" in result


if __name__ == '__main__':
    pytest.main([__file__]) 