# backend/app/extensions.py
# Flask 확장 기능 초기화

from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# 데이터베이스
db = SQLAlchemy()

# 캐시 (선택적)
cache = Cache()

# TODO: 필요에 따라 추가 확장 기능 초기화
# from flask_login import LoginManager
# from flask_migrate import Migrate
# from flask_cors import CORS 