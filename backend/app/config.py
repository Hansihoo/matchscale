# backend/app/config.py
# 환경별 설정 클래스 정의

import os


class Config:
    '''
    기본 설정 클래스
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    '''
    개발 환경 설정
    '''
    DEBUG = True


class TestingConfig(Config):
    '''
    테스트 환경 설정
    '''
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    '''
    운영 환경 설정
    '''
    # TODO: 운영 환경에서 SECRET_KEY 환경변수 설정 필요
    pass


# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 