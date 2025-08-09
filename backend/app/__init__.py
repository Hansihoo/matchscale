# backend/app/__init__.py
# Flask 앱 생성 및 블루프린트 등록

import os
from flask import Flask
from .config import Config


def create_app(config_class=Config):
    """
    Flask 애플리케이션 팩토리 함수.

    Args:
        config_class: 설정 클래스 (기본값: Config)

    Returns:
        Flask: 설정된 Flask 애플리케이션 인스턴스
    """
    # 템플릿과 정적 파일 경로를 파일 기준으로 안전하게 계산
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    template_dir = os.path.join(project_root, "frontend", "templates")
    static_dir = os.path.join(project_root, "frontend", "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    app.config.from_object(config_class)

    # 블루프린트 등록
    from .blueprints.core import bp as core_bp
    app.register_blueprint(core_bp)

    # TODO: 추가 블루프린트 등록 (stats, image 등)

    return app