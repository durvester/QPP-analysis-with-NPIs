"""
Utility functions for web application file handling and processing.
"""

import os
import uuid
import shutil
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Manages temporary files and cleanup for web application."""
    
    def __init__(self, upload_folder: str, output_folder: str):
        self.upload_folder = Path(upload_folder)
        self.output_folder = Path(output_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, file, job_id: str) -> str:
        """
        Save uploaded file with unique filename.
        
        Args:
            file: Uploaded file object
            job_id: Unique job identifier
            
        Returns:
            Path to saved file
        """
        filename = secure_filename(file.filename)
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Create job-specific directory
        job_dir = self.upload_folder / job_id
        job_dir.mkdir(exist_ok=True)
        
        file_path = job_dir / filename
        file.save(str(file_path))
        
        logger.info(f"Saved uploaded file: {file_path}")
        return str(file_path)
    
    def create_output_directory(self, job_id: str) -> str:
        """
        Create output directory for job.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Path to output directory
        """
        output_dir = self.output_folder / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir)
    
    def create_download_archive(self, job_id: str, csv_files: Dict[str, str]) -> Optional[str]:
        """
        Create ZIP archive of generated CSV files.
        
        Args:
            job_id: Unique job identifier
            csv_files: Dictionary of filename -> filepath
            
        Returns:
            Path to ZIP archive or None if error
        """
        try:
            output_dir = self.output_folder / job_id
            archive_path = output_dir / f'qpp_eligibility_data_{job_id}.zip'
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, filepath in csv_files.items():
                    if os.path.exists(filepath):
                        zipf.write(filepath, filename)
                        logger.info(f"Added {filename} to archive")
            
            logger.info(f"Created download archive: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Failed to create download archive: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old temporary files.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for folder in [self.upload_folder, self.output_folder]:
            try:
                for item in folder.iterdir():
                    if item.is_dir():
                        # Check directory modification time
                        mod_time = datetime.fromtimestamp(item.stat().st_mtime)
                        if mod_time < cutoff_time:
                            shutil.rmtree(item)
                            logger.info(f"Cleaned up old directory: {item}")
            except Exception as e:
                logger.error(f"Error during cleanup of {folder}: {e}")
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file information
        """
        path = Path(filepath)
        if not path.exists():
            return {}
        
        stat = path.stat()
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'name': path.name,
            'extension': path.suffix
        }


def generate_job_id() -> str:
    """Generate unique job identifier."""
    return str(uuid.uuid4())


def validate_npi_format(npi: str) -> bool:
    """
    Validate NPI format (10 digits).
    
    Args:
        npi: NPI string to validate
        
    Returns:
        True if valid NPI format
    """
    return npi.isdigit() and len(npi) == 10


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default