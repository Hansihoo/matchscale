# backend/app/__init__.py
# Flask 앱 생성 및 블루프린트 등록

from flask import Flask
from .config import Config


def create_app(config_class=Config):
    '''
    Flask 애플리케이션 팩토리 함수
    
    Args:
        config_class: 설정 클래스 (기본값: Config)
        
    Returns:
        Flask: 설정된 Flask 애플리케이션 인스턴스
    '''
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 블루프린트 등록
    from .blueprints.core import bp as core_bp
    app.register_blueprint(core_bp)
    
    # TODO: 추가 블루프린트 등록 (stats, image 등)
    
    return app 