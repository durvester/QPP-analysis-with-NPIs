"""
Main entry point for CMS QPP Eligibility Data Extractor.
"""

import sys
import argparse
import logging
from typing import List
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, get_config
from src.services.extraction_service import ExtractionService, ExtractionConfig


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
    parser.add_argument(
        '--config-file',
        type=str,
        help='Path to configuration file (.env format)'
    )
    
    args = parser.parse_args()
    
    # Prepare configuration overrides from command line arguments
    overrides = {}
    if args.npi_csv:
        overrides['npi_csv_path'] = args.npi_csv
    if args.output_dir:
        overrides['output.base_dir'] = args.output_dir
        overrides['output.csv_dir'] = str(Path(args.output_dir) / 'csv')
    if args.years:
        overrides['years'] = args.years
    if args.log_level:
        overrides['logging.level'] = args.log_level
    if args.skip_csv:
        overrides['output.generate_csv'] = False
    
    # Load configuration
    config = load_config(args.config_file, overrides)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting CMS QPP Eligibility Data Extractor")
    logger.info(f"Configuration loaded from environment and overrides")
    
    try:
        # Create extraction configuration
        extraction_config = ExtractionConfig(
            npi_csv_path=config.npi_csv_path,
            output_base_dir=config.output.base_dir,
            years=config.years,
            save_raw_responses=config.output.save_raw_responses,
            parallel_processing=config.processing.parallel_processing,
            batch_size=config.processing.batch_size,
            checkpoint_interval=config.processing.checkpoint_interval,
            generate_csv=config.output.generate_csv,
            validate_npis=True
        )
        
        # Initialize extraction service
        extraction_service = ExtractionService()
        
        # Handle dry run
        if args.dry_run:
            result = extraction_service.dry_run(extraction_config)
            if result.success:
                return 0
            else:
                logger.error(f"Dry run failed: {result.error_message}")
                return 1
        
        # Run extraction
        result = extraction_service.extract_data(extraction_config)
        
        if result.success:
            return 0
        else:
            logger.error(f"Extraction failed: {result.error_message}")
            return 1
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        # Clean up resources
        if 'extraction_service' in locals():
            extraction_service.close()


if __name__ == '__main__':
    sys.exit(main())