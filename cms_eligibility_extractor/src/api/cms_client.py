"""
CMS QPP Eligibility API client with rate limiting and error handling.
"""

import requests
import logging
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urljoin
import yaml
import json
from pathlib import Path

from .rate_limiter import RateLimiter, ExponentialBackoff, RateLimitConfig, with_rate_limit_and_retry
from ..models.flexible_schema import EligibilityResponse, ProcessingMetadata


logger = logging.getLogger(__name__)


class CMSAPIError(Exception):
    """Base exception for CMS API errors."""
    pass


class CMSAPINotFoundError(CMSAPIError):
    """NPI not found (404) error."""
    pass


class CMSAPIBadRequestError(CMSAPIError):
    """Bad request (400) error."""
    pass


class CMSAPIRateLimitError(CMSAPIError):
    """Rate limit (429) error."""
    pass


class CMSAPIServerError(CMSAPIError):
    """Server error (5xx) error."""
    pass


class CMSEligibilityClient:
    """
    Client for CMS QPP Eligibility API with rate limiting and retry logic.
    """
    
    def __init__(self, config_path: Optional[str] = None, rate_limit_config: Optional[RateLimitConfig] = None):
        """
        Initialize CMS API client.
        
        Args:
            config_path: Path to API configuration file
            rate_limit_config: Rate limiting configuration (uses defaults if None)
        """
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        
        # Set up rate limiting
        if rate_limit_config is None:
            rate_limit_config = RateLimitConfig(
                requests_per_second=self.config.get('rate_limiting', {}).get('requests_per_second', 2.0),
                burst_requests=self.config.get('rate_limiting', {}).get('burst_requests', 5),
                retry_delay=self.config.get('rate_limiting', {}).get('retry_delay', 1.0),
                max_retry_delay=self.config.get('rate_limiting', {}).get('max_retry_delay', 8.0),
                backoff_factor=self.config.get('rate_limiting', {}).get('backoff_factor', 2.0),
                max_retries=self.config.get('api', {}).get('max_retries', 3)
            )
        
        self.rate_limiter = RateLimiter(rate_limit_config)
        self.backoff_handler = ExponentialBackoff(rate_limit_config)
        
        # Apply rate limiting decorator to request method
        self._make_request = with_rate_limit_and_retry(self.rate_limiter, self.backoff_handler)(self._make_request_impl)
        
        # Set up session headers
        headers = self.config.get('headers', {})
        self.session.headers.update({
            'Accept': headers.get('accept', 'application/vnd.qpp.cms.gov.v6+json'),
            'User-Agent': headers.get('user_agent', 'CMS-Eligibility-Extractor/1.0')
        })
        
        # API configuration
        self.base_url = self.config['api']['base_url']
        self.endpoint_template = self.config['api']['endpoint']
        self.timeout = self.config['api'].get('timeout', 30)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'not_found_requests': 0,
            'bad_request_errors': 0,
            'rate_limit_errors': 0,
            'server_errors': 0,
            'connection_errors': 0,
            'total_processing_time': 0.0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load API configuration from YAML file."""
        if config_path is None:
            # Default to config file in project
            config_path = Path(__file__).parent.parent.parent / 'config' / 'api_config.yaml'
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'api': {
                'base_url': 'https://qpp.cms.gov',
                'endpoint': '/api/eligibility/npi/{npi}',
                'timeout': 30,
                'max_retries': 3
            },
            'rate_limiting': {
                'requests_per_second': 2.0,
                'burst_requests': 5
            },
            'headers': {
                'accept': 'application/vnd.qpp.cms.gov.v6+json',
                'user_agent': 'CMS-Eligibility-Extractor/1.0'
            }
        }
    
    def _make_request_impl(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Actual request implementation (without decorator).
        
        Args:
            url: Request URL
            params: Query parameters
            
        Returns:
            Response object
        """
        start_time = time.time()
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Update statistics
            self.stats['total_requests'] += 1
            self.stats['total_processing_time'] += time.time() - start_time
            
            # Log request details
            logger.debug(f"Request: {response.request.url} -> {response.status_code}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.stats['connection_errors'] += 1
            logger.error(f"Request failed: {e}")
            raise
    
    def get_eligibility(self, npi: str, year: Optional[int] = None, 
                       run_num: Optional[int] = None) -> Tuple[Optional[EligibilityResponse], ProcessingMetadata]:
        """
        Get eligibility data for a specific NPI and year.
        
        Args:
            npi: National Provider Identifier (10 digits)
            year: Performance year (e.g., 2023, 2024, 2025)
            run_num: Data run number (1-4)
            
        Returns:
            Tuple of (eligibility_data, processing_metadata)
            eligibility_data is None if request failed
        """
        # Validate NPI format
        if not npi.isdigit() or len(npi) != 10:
            metadata = ProcessingMetadata(
                npi=npi,
                year=year or 0,
                success=False,
                error_message="Invalid NPI format (must be 10 digits)"
            )
            return None, metadata
        
        # Build URL
        endpoint = self.endpoint_template.format(npi=npi)
        url = urljoin(self.base_url, endpoint)
        
        # Build query parameters
        params = {}
        if year is not None:
            params['year'] = year
        if run_num is not None:
            params['runNum'] = run_num
        
        try:
            # Make request (with rate limiting and retry)
            response = self._make_request(url, params)
            
            # Handle response
            metadata = ProcessingMetadata(
                npi=npi,
                year=year or 0,
                success=False,
                status_code=response.status_code
            )
            
            if response.status_code == 200:
                try:
                    # Parse and validate response
                    response_data = response.json()
                    eligibility_data = EligibilityResponse(**response_data)
                    
                    metadata.success = True
                    self.stats['successful_requests'] += 1
                    
                    logger.debug(f"Successfully retrieved data for NPI {npi}")
                    return eligibility_data, metadata
                    
                except (json.JSONDecodeError, ValueError) as e:
                    metadata.error_message = f"Failed to parse response: {e}"
                    self.stats['failed_requests'] += 1
                    logger.error(f"Failed to parse response for NPI {npi}: {e}")
                    return None, metadata
                    
            elif response.status_code == 404:
                metadata.error_message = "NPI not found"
                self.stats['not_found_requests'] += 1
                logger.info(f"NPI {npi} not found (404)")
                return None, metadata
                
            elif response.status_code == 400:
                metadata.error_message = "Bad request"
                self.stats['bad_request_errors'] += 1
                logger.warning(f"Bad request for NPI {npi} (400)")
                return None, metadata
                
            elif response.status_code == 429:
                metadata.error_message = "Rate limited"
                self.stats['rate_limit_errors'] += 1
                logger.warning(f"Rate limited for NPI {npi} (429)")
                return None, metadata
                
            elif 500 <= response.status_code < 600:
                metadata.error_message = f"Server error ({response.status_code})"
                self.stats['server_errors'] += 1
                logger.error(f"Server error for NPI {npi} ({response.status_code})")
                return None, metadata
                
            else:
                metadata.error_message = f"Unexpected status code: {response.status_code}"
                self.stats['failed_requests'] += 1
                logger.error(f"Unexpected status code for NPI {npi}: {response.status_code}")
                return None, metadata
        
        except Exception as e:
            metadata = ProcessingMetadata(
                npi=npi,
                year=year or 0,
                success=False,
                error_message=str(e)
            )
            self.stats['failed_requests'] += 1
            logger.error(f"Request failed for NPI {npi}: {e}")
            return None, metadata
    
    def get_multiple_eligibility(self, npis: list, year: Optional[int] = None, 
                               run_num: Optional[int] = None, 
                               progress_callback: Optional[callable] = None) -> Dict[str, Tuple[Optional[EligibilityResponse], ProcessingMetadata]]:
        """
        Get eligibility data for multiple NPIs.
        
        Args:
            npis: List of NPIs to process
            year: Performance year
            run_num: Data run number
            progress_callback: Optional callback function called with (current, total, npi)
            
        Returns:
            Dictionary mapping NPI to (eligibility_data, metadata) tuple
        """
        results = {}
        
        for i, npi in enumerate(npis):
            if progress_callback:
                progress_callback(i + 1, len(npis), npi)
                
            eligibility_data, metadata = self.get_eligibility(npi, year, run_num)
            results[npi] = (eligibility_data, metadata)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        stats = self.stats.copy()
        stats.update(self.rate_limiter.get_stats())
        
        # Calculate derived statistics
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
            stats['average_request_time'] = stats['total_processing_time'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
            stats['average_request_time'] = 0.0
            
        return stats
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()