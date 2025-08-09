# backend/app/blueprints/core/routes.py
# 홈 페이지 및 통계 기반 매칭 확률 계산 API

from flask import render_template, request, jsonify
from app.services.stats_service import calculate_probability, get_statistics_summary
from app.services.image_service import generate_result_card
from . import bp


@bp.route('/')
def index():
    """
    홈 페이지 - 이상형 입력 폼 표시
    
    Returns:
        str: 렌더링된 HTML 페이지
    """
    return render_template('index.html')


@bp.route('/api/calculate', methods=['POST'])
def calculate_rarity():
    """
    이상형 조건에 따른 희귀 확률을 계산하는 API
    
    Returns:
        JSON: 확률 계산 결과
    """
    try:
        # 요청 데이터 검증
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'JSON 형식의 데이터가 필요합니다.',
                'data': None
            }), 400
        
        filters = request.get_json()
        
        # 필수 필드 검증
        if not filters or 'gender' not in filters:
            return jsonify({
                'success': False,
                'message': '성별 정보가 필요합니다.',
                'data': None
            }), 400
        
        # 확률 계산
        result = calculate_probability(filters)
        
        # 오류가 있는 경우
        if 'error' in result:
            return jsonify({
                'success': False,
                'message': f'계산 중 오류가 발생했습니다: {result["error"]}',
                'data': None
            }), 500
        
        return jsonify({
            'success': True,
            'message': '확률 계산이 완료되었습니다.',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'서버 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500


@bp.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    결과 공유용 이미지를 생성하는 API
    
    Returns:
        JSON: 생성된 이미지 데이터
    """
    try:
        # 요청 데이터 검증
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'JSON 형식의 데이터가 필요합니다.',
                'data': None
            }), 400
        
        result_data = request.get_json()
        
        # 필수 필드 검증
        if not result_data or 'probability' not in result_data:
            return jsonify({
                'success': False,
                'message': '결과 데이터가 필요합니다.',
                'data': None
            }), 400
        
        # 이미지 생성
        image_data = generate_result_card(result_data)
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': '이미지 생성에 실패했습니다.',
                'data': None
            }), 500
        
        return jsonify({
            'success': True,
            'message': '이미지가 생성되었습니다.',
            'data': {
                'image_data': image_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'이미지 생성 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500


@bp.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    통계 데이터 요약을 반환하는 API
    
    Returns:
        JSON: 통계 요약 데이터
    """
    try:
        summary = get_statistics_summary()
        
        return jsonify({
            'success': True,
            'message': '통계 데이터를 성공적으로 조회했습니다.',
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'통계 데이터 조회 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500


@bp.route('/api/health', methods=['GET'])
def health_check():
    """
    서비스 상태 확인 API
    
    Returns:
        JSON: 서비스 상태 정보
    """
    return jsonify({
        'success': True,
        'message': '서비스가 정상적으로 작동 중입니다.',
        'data': {
            'status': 'healthy',
            'service': '희귀이상형',
            'version': '1.0.0'
        }
    }) 