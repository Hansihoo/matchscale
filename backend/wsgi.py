# backend/wsgi.py
# WSGI 서버 실행용 진입점

import os
from app import create_app

# 환경 설정
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 