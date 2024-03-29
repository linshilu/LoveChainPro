#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import timedelta


class Config:
    def __init__(self):
        pass

    SECRET_KEY = os.environ.get('SECRET_KEY') or '!@#$%^&*12345678'
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=25)
    APP_ID = os.environ.get('APP_ID')
    APP_SECRET = os.environ.get('APP_SECRET')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DEV_DATABASE_URL') or
                               'mysql+pymysql://root:123456@localhost/lovechain')


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()

    SQLALCHEMY_DATABASE_URI = (os.environ.get('PRO_DATABASE_URL'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
