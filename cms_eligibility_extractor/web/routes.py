"""
Flask routes for CMS QPP Eligibility Data Extractor web application.
"""

import os
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from werkzeug.exceptions import RequestEntityTooLarge

from .forms import NPIUploadForm, JobStatusForm
from .utils import FileManager, generate_job_id, format_file_size, format_duration
from .error_handlers import (
    FileValidationError, ProcessingError, ApplicationError,
    validate_upload_file, validate_form_data, safe_int
)

logger = logging.getLogger(__name__)

# Blueprint for main routes
main_bp = Blueprint('main', __name__)

# In-memory job storage (in production, use Redis or database)
job_storage = {}
job_lock = threading.Lock()

class JobStatus:
    """Job status tracking."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

def get_job_status(job_id: str) -> dict:
    """Get job status from storage."""
    with job_lock:
        return job_storage.get(job_id, {})

def update_job_status(job_id: str, **kwargs):
    """Update job status in storage."""
    with job_lock:
        if job_id not in job_storage:
            job_storage[job_id] = {}
        job_storage[job_id].update(kwargs)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """Home page with upload form."""
    form = NPIUploadForm()
    
    if form.validate_on_submit():
        # Redirect to upload handler
        return upload()
    
    return render_template('upload.html', form=form)

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle file upload and start processing."""
    form = NPIUploadForm()
    
    if form.validate_on_submit():
        try:
            # Validate uploaded file
            validate_upload_file(form.npi_file.data)
            
            # Validate form data
            form_data = {
                'years': form.years.data,
                'batch_size': form.batch_size.data
            }
            validate_form_data(form_data)
            
            # Generate unique job ID
            job_id = generate_job_id()
            
            # Initialize file manager
            file_manager = FileManager(
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['OUTPUT_FOLDER']
            )
            
            # Save uploaded file
            uploaded_file_path = file_manager.save_uploaded_file(form.npi_file.data, job_id)
            
            # Create output directory
            output_dir = file_manager.create_output_directory(job_id)
            
            # Get form data with safe conversion
            selected_years = [safe_int(year, min_val=2017, max_val=2030) for year in form.years.data]
            batch_size = safe_int(form.batch_size.data, default=100, min_val=1, max_val=1000)
            
            processing_config = {
                'years': selected_years,
                'save_raw_responses': form.save_raw_responses.data,
                'parallel_processing': form.parallel_processing.data,
                'batch_size': batch_size
            }
            
            # Initialize job status
            update_job_status(
                job_id,
                status=JobStatus.PENDING,
                created_at=datetime.now().isoformat(),
                uploaded_file=uploaded_file_path,
                output_dir=output_dir,
                config=processing_config,
                progress={'current': 0, 'total': 0, 'message': 'Initializing...'}
            )
            
            # Start background processing
            thread = threading.Thread(
                target=process_job_background,
                args=(job_id, uploaded_file_path, output_dir, processing_config)
            )
            thread.daemon = True
            thread.start()
            
            flash(f'File uploaded successfully! Job ID: {job_id[:8]}', 'success')
            return redirect(url_for('main.job_status', job_id=job_id))
            
        except (FileValidationError, ApplicationError) as e:
            # These exceptions are handled by the error handlers
            raise
        except Exception as e:
            logger.error(f"Unexpected upload error: {e}", exc_info=True)
            raise ApplicationError(f"Upload failed due to an unexpected error: {str(e)}")
    
    return render_template('upload.html', form=form)

@main_bp.route('/job/<job_id>')
def job_status(job_id):
    """Display job status and progress."""
    if not job_id or len(job_id.strip()) == 0:
        raise ApplicationError("Invalid job ID provided")
    
    job = get_job_status(job_id)
    
    if not job:
        raise ApplicationError(f"Job {job_id[:8]} not found", 'JOB_NOT_FOUND')
    
    form = JobStatusForm()
    return render_template('processing.html', job=job, job_id=job_id, form=form)

@main_bp.route('/api/job/<job_id>/status')
def api_job_status(job_id):
    """API endpoint for job status (for AJAX polling)."""
    if not job_id or len(job_id.strip()) == 0:
        return jsonify({'error': {'code': 'INVALID_JOB_ID', 'message': 'Invalid job ID provided'}}), 400
    
    job = get_job_status(job_id)
    
    if not job:
        return jsonify({'error': {'code': 'JOB_NOT_FOUND', 'message': f'Job {job_id[:8]} not found'}}), 404
    
    return jsonify(job)

@main_bp.route('/download/<job_id>')
def download_results(job_id):
    """Download results as ZIP file."""
    if not job_id or len(job_id.strip()) == 0:
        raise ApplicationError("Invalid job ID provided")
    
    job = get_job_status(job_id)
    
    if not job:
        raise ApplicationError(f"Job {job_id[:8]} not found", 'JOB_NOT_FOUND')
    
    if job.get('status') != JobStatus.COMPLETED:
        raise ApplicationError(
            f"Job {job_id[:8]} is not completed yet (status: {job.get('status', 'unknown')})",
            'JOB_NOT_COMPLETED'
        )
    
    archive_path = job.get('archive_path')
    if not archive_path:
        raise ProcessingError(
            f"No download file available for job {job_id[:8]}",
            job_id=job_id
        )
    
    if not os.path.exists(archive_path):
        raise ProcessingError(
            f"Download file has been removed or is no longer available for job {job_id[:8]}",
            job_id=job_id
        )
    
    try:
        return send_file(
            archive_path,
            as_attachment=True,
            download_name=f'qpp_eligibility_data_{job_id[:8]}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        logger.error(f"Failed to send file {archive_path}: {e}", exc_info=True)
        raise ProcessingError(
            f"Failed to download results for job {job_id[:8]}",
            job_id=job_id,
            details={'archive_path': archive_path, 'error': str(e)}
        )

@main_bp.route('/results/<job_id>')
def results(job_id):
    """Display processing results summary."""
    if not job_id or len(job_id.strip()) == 0:
        raise ApplicationError("Invalid job ID provided")
    
    job = get_job_status(job_id)
    
    if not job:
        raise ApplicationError(f"Job {job_id[:8]} not found", 'JOB_NOT_FOUND')
    
    if job.get('status') != JobStatus.COMPLETED:
        raise ApplicationError(
            f"Job {job_id[:8]} is not completed yet (status: {job.get('status', 'unknown')})",
            'JOB_NOT_COMPLETED'
        )
    
    return render_template('results.html', job=job, job_id=job_id)

@main_bp.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file too large error."""
    flash('File too large. Maximum size is 50MB.', 'error')
    return redirect(url_for('main.index'))

def process_job_background(job_id: str, input_file: str, output_dir: str, config: dict):
    """
    Background function to process the job.
    This integrates with the existing MultiYearOrchestrator.
    """
    try:
        update_job_status(
            job_id,
            status=JobStatus.PROCESSING,
            started_at=datetime.now().isoformat(),
            progress={'current': 0, 'total': 0, 'message': 'Starting processing...'}
        )
        
        # Import here to avoid circular imports
        import sys
        from pathlib import Path
        
        # Add parent directory to path for imports
        parent_dir = Path(__file__).parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        from src.services.extraction_service import ExtractionService, ExtractionConfig
        from src.config import get_config
        
        # Get unified configuration
        app_config = get_config()
        
        # Create extraction configuration
        extraction_config = ExtractionConfig(
            npi_csv_path=input_file,
            output_base_dir=output_dir,
            years=config['years'],
            save_raw_responses=config['save_raw_responses'],
            parallel_processing=config['parallel_processing'],
            batch_size=config['batch_size'],
            generate_csv=True,
            validate_npis=True
        )
        
        # Create progress callback
        def progress_callback(current, total, npi):
            update_job_status(
                job_id,
                progress={
                    'current': current,
                    'total': total,
                    'message': f'Processing NPI {npi} ({current}/{total})'
                }
            )
        
        # Initialize extraction service
        extraction_service = ExtractionService()
        
        # Update status before starting
        update_job_status(job_id, progress={'current': 0, 'total': 0, 'message': 'Loading NPIs...'})
        
        # Run extraction
        result = extraction_service.extract_data(extraction_config, progress_callback)
        
        if result.success:
            # Create download archive
            update_job_status(job_id, progress={'current': 0, 'total': 0, 'message': 'Creating download archive...'})
            
            file_manager = FileManager(
                app_config.web.upload_folder,
                app_config.web.temp_folder
            )
            
            archive_path = file_manager.create_download_archive(job_id, result.output_files)
            
            # Job completed successfully
            update_job_status(
                job_id,
                status=JobStatus.COMPLETED,
                completed_at=datetime.now().isoformat(),
                archive_path=archive_path,
                output_files=list(result.output_files.keys()),
                stats=result.stats,
                progress={'current': result.total_npis, 'total': result.total_npis, 'message': 'Processing completed!'}
            )
            
            logger.info(f"Job {job_id} completed successfully")
        else:
            # Job failed
            update_job_status(
                job_id,
                status=JobStatus.FAILED,
                error_message=result.error_message,
                failed_at=datetime.now().isoformat(),
                progress={'current': 0, 'total': 0, 'message': f'Processing failed: {result.error_message}'}
            )
            logger.error(f"Job {job_id} failed: {result.error_message}")
        
        # Cleanup
        extraction_service.close()
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        
        update_job_status(
            job_id,
            status=JobStatus.FAILED,
            error_message=str(e),
            failed_at=datetime.now().isoformat(),
            progress={'current': 0, 'total': 0, 'message': f'Processing failed: {str(e)}'}
        )
        
        # Cleanup on exception
        if 'extraction_service' in locals():
            extraction_service.close()