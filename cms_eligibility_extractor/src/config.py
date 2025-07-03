"""
Unified configuration system for CMS QPP Eligibility Data Extractor.
Supports both CLI and web applications.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration (for future use)."""
    host: str = "localhost"
    port: int = 5432
    name: str = "cms_qpp"
    user: str = "postgres"
    password: str = ""
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables."""
        return cls(
            host=os.getenv('DB_HOST', cls.host),
            port=int(os.getenv('DB_PORT', cls.port)),
            name=os.getenv('DB_NAME', cls.name),
            user=os.getenv('DB_USER', cls.user),
            password=os.getenv('DB_PASSWORD', cls.password)
        )


@dataclass
class APIConfig:
    """API configuration."""
    base_url: str = "https://qpp.cms.gov"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_delay: float = 0.1
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create API config from environment variables."""
        return cls(
            base_url=os.getenv('CMS_API_BASE_URL', cls.base_url),
            timeout=int(os.getenv('API_TIMEOUT', cls.timeout)),
            max_retries=int(os.getenv('API_MAX_RETRIES', cls.max_retries)),
            retry_delay=float(os.getenv('API_RETRY_DELAY', cls.retry_delay)),
            rate_limit_delay=float(os.getenv('API_RATE_LIMIT_DELAY', cls.rate_limit_delay))
        )


@dataclass
class ProcessingConfig:
    """Processing configuration."""
    batch_size: int = 100
    checkpoint_interval: int = 1000
    parallel_processing: bool = True
    max_workers: int = 4
    memory_limit_mb: int = 1024
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        """Create processing config from environment variables."""
        return cls(
            batch_size=int(os.getenv('BATCH_SIZE', cls.batch_size)),
            checkpoint_interval=int(os.getenv('CHECKPOINT_INTERVAL', cls.checkpoint_interval)),
            parallel_processing=os.getenv('PARALLEL_PROCESSING', 'true').lower() == 'true',
            max_workers=int(os.getenv('MAX_WORKERS', cls.max_workers)),
            memory_limit_mb=int(os.getenv('MEMORY_LIMIT_MB', cls.memory_limit_mb))
        )


@dataclass
class OutputConfig:
    """Output configuration."""
    base_dir: str = "./outputs"
    csv_dir: str = "./outputs/csv"
    raw_responses_dir: str = "./outputs/raw"
    archive_dir: str = "./outputs/archives"
    generate_csv: bool = True
    save_raw_responses: bool = True
    cleanup_temp_files: bool = True
    
    @classmethod
    def from_env(cls) -> 'OutputConfig':
        """Create output config from environment variables."""
        base_dir = os.getenv('OUTPUT_BASE_DIR', cls.base_dir)
        return cls(
            base_dir=base_dir,
            csv_dir=os.getenv('CSV_OUTPUT_DIR', f"{base_dir}/csv"),
            raw_responses_dir=os.getenv('RAW_RESPONSES_DIR', f"{base_dir}/raw"),
            archive_dir=os.getenv('ARCHIVE_DIR', f"{base_dir}/archives"),
            generate_csv=os.getenv('GENERATE_CSV', 'true').lower() == 'true',
            save_raw_responses=os.getenv('SAVE_RAW_RESPONSES', 'true').lower() == 'true',
            cleanup_temp_files=os.getenv('CLEANUP_TEMP_FILES', 'true').lower() == 'true'
        )


@dataclass
class WebConfig:
    """Web application configuration."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = "dev-secret-key-change-in-production"
    max_content_length: int = 50 * 1024 * 1024  # 50MB
    upload_folder: str = "./temp_uploads"
    temp_folder: str = "./temp_outputs"
    csrf_time_limit: Optional[int] = None
    
    @classmethod
    def from_env(cls) -> 'WebConfig':
        """Create web config from environment variables."""
        return cls(
            host=os.getenv('WEB_HOST', cls.host),
            port=int(os.getenv('WEB_PORT', cls.port)),
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', cls.secret_key),
            max_content_length=int(os.getenv('MAX_CONTENT_LENGTH', cls.max_content_length)),
            upload_folder=os.getenv('UPLOAD_FOLDER', cls.upload_folder),
            temp_folder=os.getenv('TEMP_FOLDER', cls.temp_folder),
            csrf_time_limit=int(os.getenv('CSRF_TIME_LIMIT')) if os.getenv('CSRF_TIME_LIMIT') else None
        )


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create logging config from environment variables."""
        return cls(
            level=os.getenv('LOG_LEVEL', cls.level),
            file=os.getenv('LOG_FILE', cls.file),
            format=os.getenv('LOG_FORMAT', cls.format),
            max_bytes=int(os.getenv('LOG_MAX_BYTES', cls.max_bytes)),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', cls.backup_count))
        )


@dataclass
class AppConfig:
    """Main application configuration."""
    # Core settings
    years: List[int] = field(default_factory=lambda: [2023, 2024, 2025])
    npi_csv_path: str = "../templates/npi_template.csv"
    
    # Component configurations
    api: APIConfig = field(default_factory=APIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    web: WebConfig = field(default_factory=WebConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Environment
    environment: str = "development"
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'AppConfig':
        """Create application config from environment variables."""
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Parse years
        years_str = os.getenv('EXTRACTION_YEARS', '2023,2024,2025')
        years = [int(year.strip()) for year in years_str.split(',')]
        
        # Validate years
        for year in years:
            if year < 2017 or year > 2030:
                raise ValueError(f"Year {year} is outside valid range (2017-2030)")
        
        return cls(
            years=years,
            npi_csv_path=os.getenv('NPI_CSV_PATH', cls.npi_csv_path),
            api=APIConfig.from_env(),
            processing=ProcessingConfig.from_env(),
            output=OutputConfig.from_env(),
            web=WebConfig.from_env(),
            logging=LoggingConfig.from_env(),
            database=DatabaseConfig.from_env(),
            environment=os.getenv('ENVIRONMENT', cls.environment)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'years': self.years,
            'npi_csv_path': self.npi_csv_path,
            'api': self.api.__dict__,
            'processing': self.processing.__dict__,
            'output': self.output.__dict__,
            'web': self.web.__dict__,
            'logging': self.logging.__dict__,
            'database': self.database.__dict__,
            'environment': self.environment
        }
    
    def setup_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            self.output.base_dir,
            self.output.csv_dir,
            self.output.raw_responses_dir,
            self.output.archive_dir,
            self.web.upload_folder,
            self.web.temp_folder
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        import logging.handlers
        
        # Create formatter
        formatter = logging.Formatter(self.logging.format)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.logging.level.upper()))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if self.logging.file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.logging.file,
                maxBytes=self.logging.max_bytes,
                backupCount=self.logging.backup_count
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Reduce noise from some libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)
    
    def validate(self) -> None:
        """Validate configuration."""
        errors = []
        
        # Validate years
        for year in self.years:
            if not isinstance(year, int) or year < 2017 or year > 2030:
                errors.append(f"Invalid year: {year}")
        
        # Validate NPI CSV path
        if not os.path.exists(self.npi_csv_path):
            errors.append(f"NPI CSV file not found: {self.npi_csv_path}")
        
        # Validate batch size
        if self.processing.batch_size < 1 or self.processing.batch_size > 1000:
            errors.append(f"Batch size must be between 1 and 1000, got: {self.processing.batch_size}")
        
        # Validate API timeout
        if self.api.timeout < 1 or self.api.timeout > 300:
            errors.append(f"API timeout must be between 1 and 300 seconds, got: {self.api.timeout}")
        
        # Validate web configuration
        if self.web.port < 1 or self.web.port > 65535:
            errors.append(f"Web port must be between 1 and 65535, got: {self.web.port}")
        
        if self.web.max_content_length < 1024 or self.web.max_content_length > 1024 * 1024 * 1024:
            errors.append(f"Max content length must be between 1KB and 1GB, got: {self.web.max_content_length}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def override_from_dict(self, overrides: Dict[str, Any]) -> None:
        """Override configuration values from dictionary."""
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                # Handle nested configurations
                if '.' in key:
                    config_section, config_key = key.split('.', 1)
                    if hasattr(self, config_section):
                        config_obj = getattr(self, config_section)
                        if hasattr(config_obj, config_key):
                            setattr(config_obj, config_key, value)
                        else:
                            logger.warning(f"Unknown configuration key: {key}")
                    else:
                        logger.warning(f"Unknown configuration section: {config_section}")
                else:
                    logger.warning(f"Unknown configuration key: {key}")


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def load_config(env_file: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    """Load configuration from environment and optional overrides."""
    config = AppConfig.from_env(env_file)
    
    if overrides:
        config.override_from_dict(overrides)
    
    config.validate()
    config.setup_directories()
    config.setup_logging()
    
    set_config(config)
    return config


def get_flask_config() -> Dict[str, Any]:
    """Get Flask-specific configuration dictionary."""
    config = get_config()
    
    return {
        'SECRET_KEY': config.web.secret_key,
        'MAX_CONTENT_LENGTH': config.web.max_content_length,
        'UPLOAD_FOLDER': config.web.upload_folder,
        'OUTPUT_FOLDER': config.web.temp_folder,
        'WTF_CSRF_TIME_LIMIT': config.web.csrf_time_limit,
        'DEBUG': config.web.debug,
        'ENVIRONMENT': config.environment
    }