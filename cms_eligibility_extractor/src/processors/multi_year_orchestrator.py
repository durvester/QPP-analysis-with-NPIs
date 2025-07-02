"""
Multi-year orchestrator for coordinating CMS API data extraction across years.
"""

import logging
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from tqdm import tqdm

from ..api.cms_client import CMSEligibilityClient
from ..models.flexible_schema import ProcessingMetadata
from ..models.output_models import DataQualityReport, ExportSummary
from .npi_reader import NPIReader
from .data_processor import DataProcessor


logger = logging.getLogger(__name__)


class MultiYearOrchestrator:
    """
    Orchestrates multi-year data extraction, processing, and export.
    """
    
    def __init__(
        self, 
        npi_csv_path: str,
        output_base_dir: str,
        years: List[int],
        cms_client: Optional[CMSEligibilityClient] = None
    ):
        """
        Initialize multi-year orchestrator.
        
        Args:
            npi_csv_path: Path to CSV file containing NPIs
            output_base_dir: Base directory for outputs
            years: List of years to process (e.g., [2023, 2024, 2025])
            cms_client: CMS API client (creates default if None)
        """
        self.npi_csv_path = npi_csv_path
        self.output_base_dir = Path(output_base_dir)
        self.years = years
        
        # Create output directories
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        for subdir in ['csv', 'database', 'excel', 'raw', 'logs', 'reports']:
            (self.output_base_dir / subdir).mkdir(exist_ok=True)
        
        # Initialize components
        self.npi_reader = NPIReader(npi_csv_path)
        self.data_processor = DataProcessor()
        self.cms_client = cms_client or CMSEligibilityClient()
        
        # Processing state
        self.npis = []
        self.processing_results = {}  # year -> {npi -> (response, metadata)}
        self.processed_records = {}   # year -> {table_name -> [records]}
        
        # Statistics
        self.orchestrator_stats = {
            'start_time': None,
            'end_time': None,
            'total_npis': 0,
            'years_processed': [],
            'total_api_calls': 0,
            'total_processing_time': 0.0
        }
    
    def load_npis(self, validate_npis: bool = True) -> List[str]:
        """
        Load NPIs from CSV file.
        
        Args:
            validate_npis: Whether to validate NPI format
            
        Returns:
            List of valid NPIs
        """
        logger.info("Loading NPIs from CSV file...")
        
        try:
            self.npis = self.npi_reader.read_npis(skip_validation=not validate_npis)
            self.orchestrator_stats['total_npis'] = len(self.npis)
            
            logger.info(f"Loaded {len(self.npis)} NPIs for processing")
            
            # Log NPI reader statistics
            npi_stats = self.npi_reader.get_stats()
            logger.info(f"NPI validation results: {npi_stats['success_rate']:.1f}% success rate")
            
            return self.npis
            
        except Exception as e:
            logger.error(f"Failed to load NPIs: {e}")
            raise
    
    def process_year(
        self, 
        year: int, 
        progress_callback: Optional[Callable] = None,
        save_raw_responses: bool = True,
        checkpoint_interval: int = 1000
    ) -> Dict[str, Any]:
        """
        Process all NPIs for a specific year.
        
        Args:
            year: Performance year to process
            progress_callback: Optional progress callback function
            save_raw_responses: Whether to save raw JSON responses
            checkpoint_interval: Save checkpoint every N NPIs
            
        Returns:
            Processing results for the year
        """
        logger.info(f"Starting processing for year {year}")
        start_time = time.time()
        
        if not self.npis:
            raise ValueError("No NPIs loaded. Call load_npis() first.")
        
        year_results = {}
        year_records = {
            'providers': [],
            'organizations': [],
            'individual_scenarios': [],
            'group_scenarios': [],
            'apms': [],
            'virtual_groups': []
        }
        
        # Set up progress tracking
        pbar = None
        if progress_callback is None:
            pbar = tqdm(total=len(self.npis), desc=f"Processing {year}")
            progress_callback = lambda current, total, npi: pbar.update(1)
        
        # Create year-specific output directory
        year_output_dir = self.output_base_dir / 'raw' / str(year)
        year_output_dir.mkdir(exist_ok=True)
        
        successful_count = 0
        failed_count = 0
        
        try:
            for i, npi in enumerate(self.npis):
                try:
                    # Make API request
                    eligibility_response, metadata = self.cms_client.get_eligibility(npi, year)
                    year_results[npi] = (eligibility_response, metadata)
                    
                    # Save raw response if requested and successful
                    if save_raw_responses and eligibility_response:
                        raw_file = year_output_dir / f"{npi}.json"
                        with open(raw_file, 'w') as f:
                            # Convert to dict for JSON serialization
                            response_dict = eligibility_response.dict()
                            json.dump(response_dict, f, indent=2)
                    
                    # Process successful responses
                    if eligibility_response and metadata.success:
                        try:
                            records = self.data_processor.process_eligibility_response(
                                eligibility_response, year, metadata
                            )
                            
                            # Accumulate records
                            for table_name, table_records in records.items():
                                year_records[table_name].extend(table_records)
                            
                            successful_count += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to process response for NPI {npi}: {e}")
                            failed_count += 1
                    else:
                        failed_count += 1
                        logger.debug(f"No valid response for NPI {npi}: {metadata.error_message}")
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(i + 1, len(self.npis), npi)
                    
                    # Checkpoint save
                    if (i + 1) % checkpoint_interval == 0:
                        self._save_checkpoint(year, year_results, year_records, i + 1)
                        logger.info(f"Checkpoint saved at {i + 1} NPIs for year {year}")
                
                except Exception as e:
                    logger.error(f"Unexpected error processing NPI {npi} for year {year}: {e}")
                    failed_count += 1
                    continue
        
        finally:
            if hasattr(pbar, 'close'):
                pbar.close()
        
        # Store results
        self.processing_results[year] = year_results
        self.processed_records[year] = year_records
        
        processing_time = time.time() - start_time
        self.orchestrator_stats['total_processing_time'] += processing_time
        self.orchestrator_stats['years_processed'].append(year)
        
        # Log summary
        logger.info(f"Completed processing for year {year}")
        logger.info(f"  Successful: {successful_count}")
        logger.info(f"  Failed: {failed_count}")
        logger.info(f"  Processing time: {processing_time:.2f} seconds")
        
        # Generate data quality report
        metadata_list = [metadata for _, metadata in year_results.values()]
        quality_report = self.data_processor.generate_data_quality_report(
            year, metadata_list, processing_time
        )
        
        return {
            'year': year,
            'successful_count': successful_count,
            'failed_count': failed_count,
            'processing_time': processing_time,
            'quality_report': quality_report,
            'records': year_records
        }
    
    def process_all_years(
        self, 
        progress_callback: Optional[Callable] = None,
        save_raw_responses: bool = True,
        checkpoint_interval: int = 1000,
        parallel: bool = True
    ) -> Dict[int, Dict[str, Any]]:
        """
        Process all configured years.
        
        Args:
            progress_callback: Optional progress callback function
            save_raw_responses: Whether to save raw JSON responses
            checkpoint_interval: Save checkpoint every N NPIs
            parallel: Whether to process years in parallel (default: True)
            
        Returns:
            Processing results for all years
        """
        self.orchestrator_stats['start_time'] = datetime.now()
        logger.info(f"Starting multi-year processing for years: {self.years} (parallel={parallel})")
        
        all_results = {}
        
        try:
            if parallel and len(self.years) > 1:
                all_results = self._process_years_parallel(
                    progress_callback, save_raw_responses, checkpoint_interval
                )
            else:
                all_results = self._process_years_sequential(
                    progress_callback, save_raw_responses, checkpoint_interval
                )
        
        except Exception as e:
            logger.error(f"Error during multi-year processing: {e}")
            raise
        
        finally:
            self.orchestrator_stats['end_time'] = datetime.now()
            
            # Calculate total API calls
            total_calls = sum(len(self.processing_results.get(year, {})) for year in self.years)
            self.orchestrator_stats['total_api_calls'] = total_calls
        
        # Save final summary
        self._save_processing_summary(all_results)
        
        logger.info("Multi-year processing completed")
        return all_results
    
    def _process_years_sequential(
        self, 
        progress_callback: Optional[Callable],
        save_raw_responses: bool,
        checkpoint_interval: int
    ) -> Dict[int, Dict[str, Any]]:
        """Process years sequentially (original method)."""
        all_results = {}
        
        for year in self.years:
            logger.info(f"Starting processing for year {year}")
            year_results = self.process_year(
                year, 
                progress_callback=progress_callback,
                save_raw_responses=save_raw_responses,
                checkpoint_interval=checkpoint_interval
            )
            all_results[year] = year_results
            logger.info(f"Completed year {year}, moving to next year...")
        
        return all_results
    
    def _process_years_parallel(
        self, 
        progress_callback: Optional[Callable],
        save_raw_responses: bool,
        checkpoint_interval: int
    ) -> Dict[int, Dict[str, Any]]:
        """Process years in parallel using ThreadPoolExecutor."""
        all_results = {}
        
        # Create progress bars for each year
        year_progress_bars = {}
        if progress_callback is None:
            for year in self.years:
                year_progress_bars[year] = tqdm(
                    total=len(self.npis), 
                    desc=f"Year {year}", 
                    position=self.years.index(year)
                )
        
        def year_progress_callback(year: int):
            """Create a progress callback for a specific year."""
            if progress_callback:
                return progress_callback
            else:
                return lambda current, total, npi: year_progress_bars[year].update(1)
        
        try:
            # Process years in parallel with thread pool
            with ThreadPoolExecutor(max_workers=len(self.years)) as executor:
                # Submit all year processing tasks
                future_to_year = {
                    executor.submit(
                        self.process_year,
                        year,
                        progress_callback=year_progress_callback(year),
                        save_raw_responses=save_raw_responses,
                        checkpoint_interval=checkpoint_interval
                    ): year for year in self.years
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_year):
                    year = future_to_year[future]
                    try:
                        year_results = future.result()
                        all_results[year] = year_results
                        logger.info(f"Completed year {year}")
                    except Exception as e:
                        logger.error(f"Error processing year {year}: {e}")
                        raise
        
        finally:
            # Close progress bars
            for pbar in year_progress_bars.values():
                if hasattr(pbar, 'close'):
                    pbar.close()
        
        return all_results
    
    def _save_checkpoint(
        self, 
        year: int, 
        year_results: Dict[str, Any], 
        year_records: Dict[str, List[Any]], 
        npis_processed: int
    ):
        """Save processing checkpoint for resume capability."""
        checkpoint_data = {
            'year': year,
            'npis_processed': npis_processed,
            'total_npis': len(self.npis),
            'timestamp': datetime.now().isoformat(),
            'successful_npis': sum(1 for _, metadata in year_results.values() if metadata.success),
            'failed_npis': sum(1 for _, metadata in year_results.values() if not metadata.success)
        }
        
        checkpoint_file = self.output_base_dir / 'logs' / f'checkpoint_{year}.json'
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def _save_processing_summary(self, all_results: Dict[int, Dict[str, Any]]):
        """Save comprehensive processing summary."""
        summary = {
            'orchestrator_stats': self.orchestrator_stats,
            'year_summaries': {},
            'api_client_stats': self.cms_client.get_stats(),
            'data_processor_stats': self.data_processor.get_stats(),
            'npi_reader_stats': self.npi_reader.get_stats()
        }
        
        # Add per-year summaries
        for year, results in all_results.items():
            summary['year_summaries'][year] = {
                'successful_count': results['successful_count'],
                'failed_count': results['failed_count'],
                'processing_time': results['processing_time'],
                'record_counts': {
                    table: len(records) for table, records in results['records'].items()
                }
            }
        
        # Save to file
        summary_file = self.output_base_dir / 'reports' / 'processing_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)  # default=str for datetime serialization
        
        logger.info(f"Processing summary saved to {summary_file}")
    
    def get_records_for_year(self, year: int) -> Optional[Dict[str, List[Any]]]:
        """Get processed records for a specific year."""
        return self.processed_records.get(year)
    
    def get_all_records(self) -> Dict[int, Dict[str, List[Any]]]:
        """Get all processed records across all years."""
        return self.processed_records
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            'orchestrator_stats': self.orchestrator_stats,
            'api_client_stats': self.cms_client.get_stats(),
            'data_processor_stats': self.data_processor.get_stats(),
            'npi_reader_stats': self.npi_reader.get_stats()
        }
    
    def close(self):
        """Clean up resources."""
        if self.cms_client:
            self.cms_client.close()
    
    def resume_from_checkpoint(self, year: int) -> Optional[Dict[str, Any]]:
        """
        Resume processing from a saved checkpoint.
        
        Args:
            year: Year to resume processing for
            
        Returns:
            Checkpoint data if found, None otherwise
        """
        checkpoint_file = self.output_base_dir / 'logs' / f'checkpoint_{year}.json'
        
        if not checkpoint_file.exists():
            logger.info(f"No checkpoint found for year {year}")
            return None
        
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            logger.info(f"Found checkpoint for year {year}: {checkpoint_data['npis_processed']} NPIs processed")
            return checkpoint_data
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint for year {year}: {e}")
            return None