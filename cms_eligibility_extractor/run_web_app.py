#!/usr/bin/env python3
"""
Startup script for CMS QPP Eligibility Data Extractor Web Application.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from web.app import create_app

def main():
    """Main entry point for web application."""
    
    # Set default environment variables if not already set
    os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
    os.environ.setdefault('UPLOAD_FOLDER', str(current_dir / 'temp_uploads'))
    os.environ.setdefault('OUTPUT_FOLDER', str(current_dir / 'temp_outputs'))
    
    # Create Flask app
    app = create_app()
    
    # Configuration
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("CMS QPP Eligibility Data Extractor - Web Interface")
    print("=" * 60)
    print(f"Starting web server on http://{host}:{port}")
    print(f"Debug mode: {'ON' if debug else 'OFF'}")
    print()
    print("Available endpoints:")
    print(f"  - Upload: http://{host}:{port}/")
    print(f"  - Status: http://{host}:{port}/job/<job_id>")
    print(f"  - Download: http://{host}:{port}/download/<job_id>")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nShutting down web server...")
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()