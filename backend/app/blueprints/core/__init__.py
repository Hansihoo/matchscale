# backend/app/blueprints/core/__init__.py
# 핵심 기능 블루프린트 초기화

from flask import Blueprint

bp = Blueprint('core', __name__)

from . import routes 