"""
Main entry point for CMS QPP Eligibility Data Extractor.
"""

import os
import sys
import argparse
import logging
from typing import List
from pathlib import Path
from dotenv import load_dotenv
import yaml

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.cms_client import CMSEligibilityClient
from src.processors.multi_year_orchestrator import MultiYearOrchestrator
from src.exporters.csv_exporter import CSVExporter


def parse_years(years_str: str) -> List[int]:
    """Parse comma-separated years string into list of integers."""
    try:
        years = [int(year.strip()) for year in years_str.split(',')]
        # Validate years are reasonable (2017-2030)
        for year in years:
            if year < 2017 or year > 2030:
                raise ValueError(f"Year {year} is outside valid range (2017-2030)")
        return sorted(years)
    except ValueError as e:
        raise ValueError(f"Invalid years configuration '{years_str}': {e}")


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    
    # Reduce noise from some libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def load_configuration():
    """Load configuration from environment and config files."""
    # Load environment variables
    load_dotenv()
    
    config = {
        # Input configuration
        'npi_csv_path': os.getenv('NPI_CSV_PATH', '../templates/npi_template.csv'),
        
        # Output configuration
        'output_base_dir': os.getenv('OUTPUT_BASE_DIR', './outputs'),
        'csv_output_dir': os.getenv('CSV_OUTPUT_DIR', './outputs/csv'),
        'generate_csv': os.getenv('GENERATE_CSV', 'true').lower() == 'true',
        'save_raw_responses': os.getenv('SAVE_RAW_RESPONSES', 'true').lower() == 'true',
        
        # Processing configuration
        'years': parse_years(os.getenv('EXTRACTION_YEARS', '2023,2024,2025')),
        'batch_size': int(os.getenv('BATCH_SIZE', '100')),
        'checkpoint_interval': int(os.getenv('CHECKPOINT_INTERVAL', '1000')),
        
        # Logging configuration
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'log_file': os.getenv('LOG_FILE', None),
    }
    
    return config


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='CMS QPP Eligibility Data Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                                    # Run with default settings
  python src/main.py --years 2023 2024                 # Extract only 2023 and 2024
  python src/main.py --npi-csv ../NPI.csv             # Specify custom NPI CSV file
  python src/main.py --output-dir ./my_outputs         # Specify custom output directory
  python src/main.py --dry-run                         # Test NPI loading without API calls
        """
    )
    
    parser.add_argument(
        '--npi-csv', 
        type=str, 
        help='Path to CSV file containing NPIs'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--years', 
        type=int, 
        nargs='+', 
        help='Years to process (e.g., --years 2023 2024 2025)'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        help='Logging level'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Load NPIs and validate setup without making API calls'
    )
    parser.add_argument(
        '--resume', 
        action='store_true', 
        help='Resume from last checkpoint if available'
    )
    parser.add_argument(
        '--skip-csv', 
        action='store_true', 
        help='Skip CSV export'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_configuration()
    
    # Override config with command line arguments
    if args.npi_csv:
        config['npi_csv_path'] = args.npi_csv
    if args.output_dir:
        config['output_base_dir'] = args.output_dir
        config['csv_output_dir'] = str(Path(args.output_dir) / 'csv')
    if args.years:
        config['years'] = args.years
    if args.log_level:
        config['log_level'] = args.log_level
    if args.skip_csv:
        config['generate_csv'] = False
    
    # Setup logging
    setup_logging(config['log_level'], config['log_file'])
    logger = logging.getLogger(__name__)
    
    logger.info("Starting CMS QPP Eligibility Data Extractor")
    logger.info(f"Configuration: {config}")
    
    try:
        # Validate input file
        npi_csv_path = Path(config['npi_csv_path'])
        if not npi_csv_path.exists():
            logger.error(f"NPI CSV file not found: {npi_csv_path}")
            return 1
        
        # Initialize components
        logger.info("Initializing components...")
        
        # Create CMS API client
        cms_client = CMSEligibilityClient()
        
        # Create orchestrator
        orchestrator = MultiYearOrchestrator(
            npi_csv_path=str(npi_csv_path),
            output_base_dir=config['output_base_dir'],
            years=config['years'],
            cms_client=cms_client
        )
        
        # Load NPIs
        logger.info("Loading NPIs from CSV...")
        npis = orchestrator.load_npis(validate_npis=True)
        logger.info(f"Loaded {len(npis)} valid NPIs")
        
        if args.dry_run:
            logger.info("Dry run completed successfully")
            logger.info(f"Would process {len(npis)} NPIs for years {config['years']}")
            return 0
        
        # Process data
        logger.info("Starting data extraction...")
        
        def progress_callback(current, total, npi):
            if current % 100 == 0 or current == total:
                logger.info(f"Progress: {current}/{total} NPIs processed ({current/total*100:.1f}%)")
        
        all_results = orchestrator.process_all_years(
            progress_callback=progress_callback,
            save_raw_responses=config['save_raw_responses'],
            checkpoint_interval=config['checkpoint_interval'],
            parallel=True
        )
        
        # Export data
        if config['generate_csv']:
            logger.info("Exporting data to CSV...")
            csv_exporter = CSVExporter(config['csv_output_dir'])
            
            # Get all processed records
            all_records = orchestrator.get_all_records()
            
            # Export to CSV
            output_files = csv_exporter.export_multiple_years(all_records)
            
            # Create data dictionary and summary
            csv_exporter.create_data_dictionary()
            csv_exporter.create_summary_report(all_records)
            
            logger.info("CSV export completed")
            
            # Log output file summary
            for year, year_files in output_files.items():
                logger.info(f"Year {year} files:")
                for table_name, file_path in year_files.items():
                    logger.info(f"  {table_name}: {file_path}")
        
        # Print final statistics
        final_stats = orchestrator.get_stats()
        logger.info("=" * 50)
        logger.info("EXTRACTION COMPLETED")
        logger.info("=" * 50)
        logger.info(f"Total NPIs processed: {final_stats['orchestrator_stats']['total_npis']}")
        logger.info(f"Total API calls made: {final_stats['orchestrator_stats']['total_api_calls']}")
        logger.info(f"Total processing time: {final_stats['orchestrator_stats']['total_processing_time']:.2f} seconds")
        logger.info(f"API success rate: {final_stats['api_client_stats']['success_rate']:.1f}%")
        logger.info("=" * 50)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        # Clean up resources
        if 'orchestrator' in locals():
            orchestrator.close()


if __name__ == '__main__':
    sys.exit(main())