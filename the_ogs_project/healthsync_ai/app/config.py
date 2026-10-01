import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'healthsync-command-center-sec-key-2026-prod')
    
    # Database
    db_path = basedir / 'instance' / 'healthsync.db'
    os.makedirs(db_path.parent, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-12345'
