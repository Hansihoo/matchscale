# backend/wsgi.py
# WSGI 서버 실행용 진입점

import os
from app import create_app
from app.config import config

# 환경 설정
config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config[config_name])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 