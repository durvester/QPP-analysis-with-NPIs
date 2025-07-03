"""
Flask web application for CMS QPP Eligibility Data Extractor.
"""

import os
import sys
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, get_flask_config

def create_app(config_overrides=None):
    """Application factory pattern."""
    # Load unified configuration
    app_config = load_config(overrides=config_overrides)
    
    # Set static and template folders relative to the parent directory
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    template_folder = os.path.join(os.path.dirname(__file__), 'templates')
    
    app = Flask(__name__, 
                static_folder=static_folder,
                template_folder=template_folder)
    
    # Apply Flask configuration from unified config
    flask_config = get_flask_config()
    app.config.update(flask_config)
    
    # Apply any additional overrides
    if config_overrides:
        app.config.update(config_overrides)
    
    # Initialize extensions
    csrf = CSRFProtect(app)
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register error handlers
    from .error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    # Load configuration
    from src.config import get_config
    config = get_config()
    
    app = create_app()
    app.run(
        debug=config.web.debug,
        host=config.web.host,
        port=config.web.port
    )