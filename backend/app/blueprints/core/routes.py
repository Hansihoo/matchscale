# backend/app/blueprints/core/routes.py
# 홈 페이지 및 입력 폼 라우팅

from flask import render_template, request, jsonify
from . import bp


@bp.route('/')
def index():
    '''
    홈 페이지 - 이상형 입력 폼 표시
    
    Returns:
        str: 렌더링된 HTML 페이지
    '''
    return render_template('index.html')


@bp.route('/api/submit', methods=['POST'])
def submit_form():
    '''
    이상형 조건 제출 API
    
    Returns:
        dict: 처리 결과 JSON 응답
    '''
    # TODO: 폼 데이터 검증 및 처리 로직 구현
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '데이터가 없습니다'}), 400
    
    # TODO: 서비스 레이어 호출하여 확률 계산
    # result = stats_service.calculate_probability(data)
    
    return jsonify({
        'success': True,
        'message': '제출 완료',
        'data': data
    }) 