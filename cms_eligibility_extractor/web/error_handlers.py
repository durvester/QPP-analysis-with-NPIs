"""
Comprehensive error handling for the web application.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from flask import request, jsonify, render_template, flash, redirect, url_for
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Base exception for application-specific errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or 'APPLICATION_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(ApplicationError):
    """Exception for file validation errors."""
    
    def __init__(self, message: str, filename: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'FILE_VALIDATION_ERROR', details)
        self.filename = filename


class ProcessingError(ApplicationError):
    """Exception for data processing errors."""
    
    def __init__(self, message: str, job_id: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'PROCESSING_ERROR', details)
        self.job_id = job_id


class ConfigurationError(ApplicationError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, config_key: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'CONFIGURATION_ERROR', details)
        self.config_key = config_key


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Log error with context information.
    
    Args:
        error: Exception to log
        context: Additional context information
        
    Returns:
        Error ID for tracking
    """
    import uuid
    error_id = str(uuid.uuid4())[:8]
    
    error_info = {
        'error_id': error_id,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'request_url': request.url if request else None,
        'request_method': request.method if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None,
        'remote_addr': request.remote_addr if request else None,
        'context': context or {}
    }
    
    # Add exception-specific information
    if isinstance(error, ApplicationError):
        error_info['error_code'] = error.error_code
        error_info['details'] = error.details
    
    logger.error(f"Application error {error_id}: {error_info}")
    
    if not isinstance(error, ApplicationError):
        # Log full traceback for unexpected errors
        logger.error(f"Traceback for error {error_id}:", exc_info=True)
    
    return error_id


def handle_application_error(error: ApplicationError) -> tuple:
    """
    Handle application-specific errors.
    
    Args:
        error: Application error to handle
        
    Returns:
        Tuple of (response, status_code)
    """
    error_id = log_error(error)
    
    if request.content_type == 'application/json' or request.is_json:
        # Return JSON error response
        return jsonify({
            'error': {
                'code': error.error_code,
                'message': error.message,
                'error_id': error_id,
                'details': error.details
            }
        }), 400
    else:
        # Handle web form errors
        if isinstance(error, FileValidationError):
            flash(f'File validation error: {error.message}', 'error')
            return redirect(url_for('main.index'))
        elif isinstance(error, ProcessingError):
            flash(f'Processing error: {error.message}', 'error')
            if error.job_id:
                return redirect(url_for('main.job_status', job_id=error.job_id))
            else:
                return redirect(url_for('main.index'))
        else:
            flash(f'Application error: {error.message}', 'error')
            return redirect(url_for('main.index'))


def handle_http_error(error: HTTPException) -> tuple:
    """
    Handle HTTP errors.
    
    Args:
        error: HTTP exception to handle
        
    Returns:
        Tuple of (response, status_code)
    """
    error_id = log_error(error)
    
    if request.content_type == 'application/json' or request.is_json:
        return jsonify({
            'error': {
                'code': 'HTTP_ERROR',
                'message': error.description,
                'error_id': error_id,
                'status_code': error.code
            }
        }), error.code
    else:
        # Render error page for web requests
        error_messages = {
            400: 'Bad Request - The request could not be understood.',
            401: 'Unauthorized - Authentication is required.',
            403: 'Forbidden - Access is denied.',
            404: 'Not Found - The requested resource was not found.',
            405: 'Method Not Allowed - The request method is not supported.',
            413: 'File Too Large - The uploaded file exceeds the maximum size limit.',
            429: 'Too Many Requests - Rate limit exceeded.',
            500: 'Internal Server Error - An unexpected error occurred.',
            502: 'Bad Gateway - Invalid response from upstream server.',
            503: 'Service Unavailable - The service is temporarily unavailable.'
        }
        
        message = error_messages.get(error.code, error.description)
        
        return render_template(
            'error.html',
            error_code=error.code,
            error_message=message,
            error_id=error_id
        ), error.code


def handle_file_too_large(error: RequestEntityTooLarge) -> tuple:
    """
    Handle file too large errors.
    
    Args:
        error: File too large exception
        
    Returns:
        Tuple of (response, status_code)
    """
    error_id = log_error(error)
    
    if request.content_type == 'application/json' or request.is_json:
        return jsonify({
            'error': {
                'code': 'FILE_TOO_LARGE',
                'message': 'The uploaded file is too large. Maximum size is 50MB.',
                'error_id': error_id,
                'max_size': '50MB'
            }
        }), 413
    else:
        flash('File too large. Maximum size is 50MB.', 'error')
        return redirect(url_for('main.index'))


def handle_unexpected_error(error: Exception) -> tuple:
    """
    Handle unexpected errors.
    
    Args:
        error: Unexpected exception
        
    Returns:
        Tuple of (response, status_code)
    """
    error_id = log_error(error)
    
    if request.content_type == 'application/json' or request.is_json:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred. Please try again later.',
                'error_id': error_id
            }
        }), 500
    else:
        flash(f'An unexpected error occurred. Error ID: {error_id}', 'error')
        return redirect(url_for('main.index'))


def register_error_handlers(app):
    """
    Register error handlers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(ApplicationError)
    def handle_app_error(error):
        return handle_application_error(error)
    
    @app.errorhandler(FileValidationError)
    def handle_file_error(error):
        return handle_application_error(error)
    
    @app.errorhandler(ProcessingError)
    def handle_proc_error(error):
        return handle_application_error(error)
    
    @app.errorhandler(ConfigurationError)
    def handle_config_error(error):
        return handle_application_error(error)
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(error):
        return handle_file_too_large(error)
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return handle_http_error(error)
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        return handle_unexpected_error(error)


def validate_upload_file(file) -> None:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file object
        
    Raises:
        FileValidationError: If file validation fails
    """
    if not file:
        raise FileValidationError("No file was uploaded")
    
    if file.filename == '':
        raise FileValidationError("No file was selected")
    
    if not file.filename.lower().endswith('.csv'):
        raise FileValidationError(
            "Invalid file type. Only CSV files are allowed.",
            filename=file.filename
        )
    
    # Check file size (this is also handled by Flask's MAX_CONTENT_LENGTH)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 50 * 1024 * 1024  # 50MB
    if file_size > max_size:
        raise FileValidationError(
            f"File too large. Maximum size is 50MB, but file is {file_size / (1024*1024):.1f}MB.",
            filename=file.filename,
            details={'file_size': file_size, 'max_size': max_size}
        )


def validate_form_data(form_data: Dict[str, Any]) -> None:
    """
    Validate form data.
    
    Args:
        form_data: Form data to validate
        
    Raises:
        ApplicationError: If validation fails
    """
    # Validate years
    years = form_data.get('years', [])
    if not years:
        raise ApplicationError("At least one year must be selected")
    
    for year in years:
        try:
            year_int = int(year)
            if year_int < 2017 or year_int > 2030:
                raise ApplicationError(f"Year {year_int} is outside valid range (2017-2030)")
        except (ValueError, TypeError):
            raise ApplicationError(f"Invalid year value: {year}")
    
    # Validate batch size
    batch_size = form_data.get('batch_size')
    if batch_size is not None:
        try:
            batch_size_int = int(batch_size)
            if batch_size_int < 1 or batch_size_int > 1000:
                raise ApplicationError("Batch size must be between 1 and 1000")
        except (ValueError, TypeError):
            raise ApplicationError(f"Invalid batch size: {batch_size}")


def safe_int(value: Any, default: int = 0, min_val: int = None, max_val: int = None) -> int:
    """
    Safely convert value to integer with bounds checking.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Integer value within bounds
        
    Raises:
        ApplicationError: If value is outside bounds
    """
    try:
        result = int(value)
        
        if min_val is not None and result < min_val:
            raise ApplicationError(f"Value {result} is below minimum {min_val}")
        
        if max_val is not None and result > max_val:
            raise ApplicationError(f"Value {result} is above maximum {max_val}")
        
        return result
        
    except (ValueError, TypeError):
        if min_val is not None and default < min_val:
            raise ApplicationError(f"Default value {default} is below minimum {min_val}")
        if max_val is not None and default > max_val:
            raise ApplicationError(f"Default value {default} is above maximum {max_val}")
        
        return default