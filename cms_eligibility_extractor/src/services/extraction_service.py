"""
Unified extraction service for both CLI and web interfaces.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass

from ..api.cms_client import CMSEligibilityClient
from ..processors.multi_year_orchestrator import MultiYearOrchestrator
from ..exporters.csv_exporter import CSVExporter


logger = logging.getLogger(__name__)


@dataclass
class ExtractionConfig:
    """Configuration for data extraction."""
    npi_csv_path: str
    output_base_dir: str
    years: List[int]
    save_raw_responses: bool = True
    parallel_processing: bool = True
    batch_size: int = 100
    checkpoint_interval: int = 1000
    generate_csv: bool = True
    validate_npis: bool = True


@dataclass
class ExtractionResult:
    """Result of data extraction."""
    success: bool
    total_npis: int
    processing_results: Dict[int, Dict[str, Any]]
    output_files: Dict[str, str]
    stats: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float = 0.0


class ExtractionService:
    """
    Unified service for CMS QPP data extraction.
    
    This service consolidates the extraction logic that was duplicated
    between CLI and web interfaces.
    """
    
    def __init__(self, cms_client: Optional[CMSEligibilityClient] = None):
        """
        Initialize extraction service.
        
        Args:
            cms_client: Optional pre-configured CMS client
        """
        self.cms_client = cms_client or CMSEligibilityClient()
        self.orchestrator = None
        
    def validate_config(self, config: ExtractionConfig) -> Tuple[bool, Optional[str]]:
        """
        Validate extraction configuration.
        
        Args:
            config: Extraction configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate input file exists
        npi_csv_path = Path(config.npi_csv_path)
        if not npi_csv_path.exists():
            return False, f"NPI CSV file not found: {npi_csv_path}"
        
        # Validate years
        if not config.years:
            return False, "At least one year must be specified"
        
        for year in config.years:
            if year < 2017 or year > 2030:
                return False, f"Year {year} is outside valid range (2017-2030)"
        
        # Validate batch size
        if config.batch_size < 1 or config.batch_size > 1000:
            return False, "Batch size must be between 1 and 1000"
        
        return True, None
    
    def extract_data(
        self, 
        config: ExtractionConfig,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> ExtractionResult:
        """
        Extract CMS QPP eligibility data.
        
        Args:
            config: Extraction configuration
            progress_callback: Optional progress callback function
            
        Returns:
            ExtractionResult with processing results
        """
        import time
        start_time = time.time()
        
        try:
            # Validate configuration
            is_valid, error_message = self.validate_config(config)
            if not is_valid:
                return ExtractionResult(
                    success=False,
                    total_npis=0,
                    processing_results={},
                    output_files={},
                    stats={},
                    error_message=error_message
                )
            
            logger.info("Starting CMS QPP data extraction")
            logger.info(f"Configuration: {config}")
            
            # Initialize orchestrator
            self.orchestrator = MultiYearOrchestrator(
                npi_csv_path=config.npi_csv_path,
                output_base_dir=config.output_base_dir,
                years=config.years,
                cms_client=self.cms_client
            )
            
            # Load NPIs
            logger.info("Loading NPIs from CSV...")
            npis = self.orchestrator.load_npis(validate_npis=config.validate_npis)
            logger.info(f"Loaded {len(npis)} valid NPIs")
            
            if len(npis) == 0:
                return ExtractionResult(
                    success=False,
                    total_npis=0,
                    processing_results={},
                    output_files={},
                    stats={},
                    error_message="No valid NPIs found in CSV file"
                )
            
            # Process data
            logger.info("Starting data extraction...")
            
            # Wrapper for progress callback to add logging
            def enhanced_progress_callback(current, total, npi):
                if progress_callback:
                    progress_callback(current, total, npi)
                
                # Log progress at intervals
                if current % 100 == 0 or current == total:
                    logger.info(f"Progress: {current}/{total} NPIs processed ({current/total*100:.1f}%)")
            
            all_results = self.orchestrator.process_all_years(
                progress_callback=enhanced_progress_callback,
                save_raw_responses=config.save_raw_responses,
                checkpoint_interval=config.checkpoint_interval,
                parallel=config.parallel_processing
            )
            
            # Export data to CSV
            output_files = {}
            if config.generate_csv:
                logger.info("Exporting data to CSV...")
                csv_output_dir = os.path.join(config.output_base_dir, 'csv')
                csv_exporter = CSVExporter(csv_output_dir)
                
                # Get all processed records
                all_records = self.orchestrator.get_all_records()
                
                # Export to CSV
                csv_output_files = csv_exporter.export_multiple_years(all_records)
                
                # Create data dictionary and summary
                csv_exporter.create_data_dictionary()
                csv_exporter.create_summary_report(all_records)
                
                # Flatten output files structure
                for year, year_files in csv_output_files.items():
                    for table_name, file_path in year_files.items():
                        filename = f"{table_name}_{year}.csv"
                        output_files[filename] = file_path
                
                # Add data dictionary and summary
                data_dict_path = os.path.join(csv_output_dir, 'data_dictionary.csv')
                summary_path = os.path.join(csv_output_dir, 'export_summary.csv')
                
                if os.path.exists(data_dict_path):
                    output_files['data_dictionary.csv'] = data_dict_path
                if os.path.exists(summary_path):
                    output_files['export_summary.csv'] = summary_path
                
                logger.info("CSV export completed")
                
                # Log output file summary
                for year, year_files in csv_output_files.items():
                    logger.info(f"Year {year} files:")
                    for table_name, file_path in year_files.items():
                        logger.info(f"  {table_name}: {file_path}")
            
            # Get final statistics
            final_stats = self.orchestrator.get_stats()
            processing_time = time.time() - start_time
            
            # Print final statistics
            logger.info("=" * 50)
            logger.info("EXTRACTION COMPLETED")
            logger.info("=" * 50)
            logger.info(f"Total NPIs processed: {final_stats['orchestrator_stats']['total_npis']}")
            logger.info(f"Total API calls made: {final_stats['orchestrator_stats']['total_api_calls']}")
            logger.info(f"Total processing time: {processing_time:.2f} seconds")
            logger.info(f"API success rate: {final_stats['api_client_stats']['success_rate']:.1f}%")
            logger.info("=" * 50)
            
            return ExtractionResult(
                success=True,
                total_npis=len(npis),
                processing_results=all_results,
                output_files=output_files,
                stats=final_stats,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            return ExtractionResult(
                success=False,
                total_npis=0,
                processing_results={},
                output_files={},
                stats={},
                error_message=str(e),
                processing_time=time.time() - start_time
            )
        
        finally:
            # Clean up resources
            if self.orchestrator:
                self.orchestrator.close()
    
    def dry_run(self, config: ExtractionConfig) -> ExtractionResult:
        """
        Perform a dry run without making API calls.
        
        Args:
            config: Extraction configuration
            
        Returns:
            ExtractionResult with validation results
        """
        try:
            # Validate configuration
            is_valid, error_message = self.validate_config(config)
            if not is_valid:
                return ExtractionResult(
                    success=False,
                    total_npis=0,
                    processing_results={},
                    output_files={},
                    stats={},
                    error_message=error_message
                )
            
            # Initialize orchestrator
            self.orchestrator = MultiYearOrchestrator(
                npi_csv_path=config.npi_csv_path,
                output_base_dir=config.output_base_dir,
                years=config.years,
                cms_client=self.cms_client
            )
            
            # Load NPIs
            npis = self.orchestrator.load_npis(validate_npis=config.validate_npis)
            
            logger.info("Dry run completed successfully")
            logger.info(f"Would process {len(npis)} NPIs for years {config.years}")
            
            return ExtractionResult(
                success=True,
                total_npis=len(npis),
                processing_results={},
                output_files={},
                stats={'dry_run': True, 'total_npis': len(npis), 'years': config.years}
            )
            
        except Exception as e:
            logger.error(f"Dry run failed: {e}", exc_info=True)
            return ExtractionResult(
                success=False,
                total_npis=0,
                processing_results={},
                output_files={},
                stats={},
                error_message=str(e)
            )
        
        finally:
            # Clean up resources
            if self.orchestrator:
                self.orchestrator.close()
    
    def close(self):
        """Clean up resources."""
        if self.cms_client:
            self.cms_client.close()
        if self.orchestrator:
            self.orchestrator.close()