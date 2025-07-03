"""
Configuration settings for the CMS QPP Eligibility Data Extractor Web Application.
"""

import os
from pathlib import Path

class Config:
    """Base configuration class."""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './temp_uploads'
    OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER') or './temp_outputs'
    
    # Security configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    
    # Application configuration
    ALLOWED_EXTENSIONS = {'csv'}
    CLEANUP_INTERVAL_HOURS = int(os.environ.get('CLEANUP_INTERVAL_HOURS', '24'))
    
    # Processing configuration
    DEFAULT_YEARS = [2024, 2025]
    DEFAULT_BATCH_SIZE = 100
    MAX_BATCH_SIZE = 1000
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create required directories
        Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
        Path(app.config['OUTPUT_FOLDER']).mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Security headers and settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Use temporary directories for testing
    UPLOAD_FOLDER = './test_uploads'
    OUTPUT_FOLDER = './test_outputs'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}