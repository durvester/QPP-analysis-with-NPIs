"""
CSV exporter for generating normalized CSV files from processed records.
"""

import csv
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import asdict, fields

from ..models.output_models import (
    ProviderCoreRecord, OrganizationRecord, IndividualScenarioRecord,
    GroupScenarioRecord, ApmRecord, VirtualGroupRecord, ExportSummary
)


logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Exports processed records to normalized CSV files.
    """
    
    def __init__(self, output_directory: str):
        """
        Initialize CSV exporter.
        
        Args:
            output_directory: Directory to save CSV files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Track export statistics
        self.export_stats = {
            'files_created': [],
            'total_records_exported': 0,
            'export_start_time': None,
            'export_end_time': None,
            'record_counts_by_table': {}
        }
        
    def export_year_data(
        self, 
        year: int, 
        records: Dict[str, List[Any]],
        overwrite: bool = True
    ) -> Dict[str, str]:
        """
        Export all record types for a specific year.
        
        Args:
            year: Performance year
            records: Dictionary mapping table names to record lists
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary mapping table names to output file paths
        """
        self.export_stats['export_start_time'] = datetime.now()
        logger.info(f"Starting CSV export for year {year}")
        
        output_files = {}
        total_records = 0
        
        # Define table configurations
        table_configs = {
            'providers': {
                'model_class': ProviderCoreRecord,
                'filename': f'providers_{year}.csv'
            },
            'organizations': {
                'model_class': OrganizationRecord,
                'filename': f'organizations_{year}.csv'
            },
            'individual_scenarios': {
                'model_class': IndividualScenarioRecord,
                'filename': f'individual_scenarios_{year}.csv'
            },
            'group_scenarios': {
                'model_class': GroupScenarioRecord,
                'filename': f'group_scenarios_{year}.csv'
            },
            'apms': {
                'model_class': ApmRecord,
                'filename': f'apms_{year}.csv'
            },
            'virtual_groups': {
                'model_class': VirtualGroupRecord,
                'filename': f'virtual_groups_{year}.csv'
            }
        }
        
        try:
            for table_name, config in table_configs.items():
                table_records = records.get(table_name, [])
                
                if not table_records:
                    logger.info(f"No records found for table '{table_name}', skipping")
                    continue
                
                output_file = self.output_directory / config['filename']
                
                # Check if file exists and handle overwrite
                if output_file.exists() and not overwrite:
                    logger.warning(f"File {output_file} exists and overwrite=False, skipping")
                    continue
                
                # Export table
                record_count = self._export_table(
                    table_records, 
                    output_file, 
                    config['model_class']
                )
                
                output_files[table_name] = str(output_file)
                total_records += record_count
                self.export_stats['record_counts_by_table'][table_name] = record_count
                self.export_stats['files_created'].append(str(output_file))
                
                logger.info(f"Exported {record_count} records to {output_file}")
            
            self.export_stats['total_records_exported'] += total_records
            
        except Exception as e:
            logger.error(f"Error during CSV export for year {year}: {e}")
            raise
        
        finally:
            self.export_stats['export_end_time'] = datetime.now()
        
        logger.info(f"CSV export completed for year {year}: {total_records} total records")
        return output_files
    
    def _export_table(
        self, 
        records: List[Any], 
        output_file: Path, 
        model_class: type
    ) -> int:
        """
        Export a single table to CSV.
        
        Args:
            records: List of record objects
            output_file: Output CSV file path
            model_class: Pydantic model class for the records
            
        Returns:
            Number of records exported
        """
        if not records:
            return 0
        
        # Get field names from the model class
        field_names = [field.name for field in fields(model_class)]
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                
                for record in records:
                    # Convert record to dictionary
                    if hasattr(record, 'dict'):
                        # Pydantic model
                        record_dict = record.dict()
                    elif hasattr(record, '__dict__'):
                        # Regular class instance
                        record_dict = record.__dict__
                    else:
                        # Assume it's already a dictionary
                        record_dict = record
                    
                    # Ensure all fields are present and handle special types
                    clean_record = {}
                    for field_name in field_names:
                        value = record_dict.get(field_name)
                        clean_record[field_name] = self._clean_csv_value(value)
                    
                    writer.writerow(clean_record)
            
            return len(records)
            
        except Exception as e:
            logger.error(f"Error writing CSV file {output_file}: {e}")
            raise
    
    def _clean_csv_value(self, value: Any) -> str:
        """
        Clean a value for CSV export.
        
        Args:
            value: Value to clean
            
        Returns:
            Cleaned string value
        """
        if value is None:
            return ''
        elif isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, dict)):
            # For complex types, convert to string representation
            return str(value)
        else:
            return str(value)
    
    def export_multiple_years(
        self, 
        multi_year_records: Dict[int, Dict[str, List[Any]]],
        overwrite: bool = True
    ) -> Dict[int, Dict[str, str]]:
        """
        Export data for multiple years.
        
        Args:
            multi_year_records: Dictionary mapping years to record dictionaries
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary mapping years to output file dictionaries
        """
        logger.info(f"Starting multi-year CSV export for years: {list(multi_year_records.keys())}")
        
        all_output_files = {}
        
        for year, year_records in multi_year_records.items():
            year_files = self.export_year_data(year, year_records, overwrite)
            all_output_files[year] = year_files
        
        logger.info("Multi-year CSV export completed")
        return all_output_files
    
    def create_data_dictionary(self, output_file: Optional[str] = None) -> str:
        """
        Create a data dictionary CSV file explaining all fields.
        
        Args:
            output_file: Output file path (uses default if None)
            
        Returns:
            Path to created data dictionary file
        """
        if output_file is None:
            output_file = self.output_directory / 'data_dictionary.csv'
        else:
            output_file = Path(output_file)
        
        # Define field descriptions
        field_descriptions = {
            # Provider core fields
            'npi': 'National Provider Identifier - unique 10-digit ID for healthcare providers',
            'year': 'Performance year for the data (e.g., 2023, 2024, 2025)',
            'firstName': 'Provider first name',
            'lastName': 'Provider last name',
            'middleName': 'Provider middle name or initial',
            'nationalProviderIdentifierType': 'Type of provider: 1=Individual, 2=Organization',
            'firstApprovedDate': 'First date enrollment was approved for this NPI',
            'yearsInMedicare': 'Number of years the provider has been in Medicare',
            'pecosEnrollmentDate': 'Year of enrollment in PECOS system',
            'newlyEnrolled': 'TRUE if provider is newly enrolled in current year',
            'qpStatus': 'Qualifying APM Participant status (Y/N/P/Q/R)',
            'isMaqi': 'TRUE if granted MAQI Demonstration Waiver',
            'qpScoreType': 'Category for QP participant (MI/ME/AE/AT/AI)',
            'amsMipsEligibleClinician': 'TRUE if eligible for MIPS',
            
            # Organization fields
            'org_index': 'Index of organization within provider record (starts at 0)',
            'TIN': 'Taxpayer Identification Number (masked)',
            'prvdrOrgName': 'Organization or practice name',
            'isFacilityBased': 'TRUE if facility-based encounters threshold met',
            'addressLineOne': 'Primary address line',
            'addressLineTwo': 'Secondary address line',
            'city': 'Organization city',
            'zip': 'Nine-digit ZIP code',
            'state': 'State abbreviation',
            'hospitalVbpName': 'Hospital Value-Based Purchasing Program facility name',
            
            # Scenario fields
            'aciHardship': 'TRUE if ACI Hardship Exemption approved',
            'aciReweighting': 'TRUE if meets ACI Reweighting conditions',
            'aggregationLevel': 'Aggregation level (1 or 2)',
            'ambulatorySurgicalCenter': 'TRUE if meets ASC threshold',
            'extremeHardship': 'TRUE if received Extreme Hardship Exemption',
            'extremeHardshipEventType': 'Type of extreme hardship event',
            'lowVolumeSwitch': 'TRUE if fell below low volume threshold',
            'mipsEligibleSwitch': 'TRUE if provider type eligible for MIPS',
            'ruralClinician': 'TRUE if has claims with rural ZIP designation',
            'nonPatientFacing': 'TRUE if patient-facing encounters met threshold',
            
            # APM fields
            'apm_index': 'Index of APM within organization record',
            'entityName': 'Official APM entity name',
            'apmId': 'APM Program identifier',
            'apmName': 'Formal APM Program name',
            'advancedApmFlag': 'TRUE if Advanced APM',
            'mipsApmFlag': 'TRUE if MIPS APM',
            'complexPatientScore': 'Composite Complex-Patient Score (0.00-5.00)',
            'finalQpcScore': 'Final Quality Payment Score',
            
            # Processing metadata
            'processed_at': 'Timestamp when data was processed',
            'data_source': 'Source of the data (CMS_QPP_API)'
        }
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Field Name', 'Description', 'Data Type', 'Example Values'])
                
                for field_name, description in field_descriptions.items():
                    # Determine data type based on common patterns
                    if field_name in ['year', 'org_index', 'apm_index', 'yearsInMedicare', 'aggregationLevel']:
                        data_type = 'Integer'
                        example = '2023' if field_name == 'year' else '1'
                    elif field_name.endswith(('Flag', 'Switch')) or field_name.startswith('is') or 'Hardship' in field_name:
                        data_type = 'Boolean'
                        example = 'TRUE/FALSE'
                    elif 'Score' in field_name or 'Payments' in field_name:
                        data_type = 'Float'
                        example = '123.45'
                    elif field_name in ['processed_at']:
                        data_type = 'DateTime'
                        example = '2024-01-15T10:30:00'
                    else:
                        data_type = 'String'
                        example = 'Sample text'
                    
                    writer.writerow([field_name, description, data_type, example])
            
            logger.info(f"Data dictionary created: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error creating data dictionary: {e}")
            raise
    
    def create_summary_report(
        self, 
        multi_year_records: Dict[int, Dict[str, List[Any]]],
        output_file: Optional[str] = None
    ) -> str:
        """
        Create a summary report of exported data.
        
        Args:
            multi_year_records: Multi-year record data
            output_file: Output file path (uses default if None)
            
        Returns:
            Path to created summary report
        """
        if output_file is None:
            output_file = self.output_directory / 'export_summary.csv'
        else:
            output_file = Path(output_file)
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Year', 'Table', 'Record Count', 'Export Status'])
                
                for year, year_records in multi_year_records.items():
                    for table_name, records in year_records.items():
                        record_count = len(records)
                        status = 'Success' if record_count > 0 else 'No Data'
                        writer.writerow([year, table_name, record_count, status])
                
                # Add totals row
                total_records = sum(
                    len(records) 
                    for year_records in multi_year_records.values() 
                    for records in year_records.values()
                )
                writer.writerow(['TOTAL', 'ALL TABLES', total_records, 'Summary'])
            
            logger.info(f"Export summary created: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error creating summary report: {e}")
            raise
    
    def get_export_stats(self) -> Dict[str, Any]:
        """Get export statistics."""
        stats = self.export_stats.copy()
        
        if stats['export_start_time'] and stats['export_end_time']:
            export_duration = stats['export_end_time'] - stats['export_start_time']
            stats['export_duration_seconds'] = export_duration.total_seconds()
        
        return stats
    
    def validate_csv_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Validate exported CSV files.
        
        Args:
            file_paths: List of CSV file paths to validate
            
        Returns:
            Validation report
        """
        validation_report = {
            'files_validated': len(file_paths),
            'valid_files': 0,
            'invalid_files': 0,
            'file_details': {},
            'errors': []
        }
        
        for file_path in file_paths:
            file_path = Path(file_path)
            file_details = {
                'exists': file_path.exists(),
                'size_bytes': 0,
                'row_count': 0,
                'column_count': 0,
                'has_header': False,
                'errors': []
            }
            
            try:
                if file_path.exists():
                    file_details['size_bytes'] = file_path.stat().st_size
                    
                    with open(file_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile)
                        
                        # Check header
                        try:
                            header = next(reader)
                            file_details['has_header'] = True
                            file_details['column_count'] = len(header)
                        except StopIteration:
                            file_details['errors'].append('Empty file')
                        
                        # Count rows
                        row_count = sum(1 for _ in reader)
                        file_details['row_count'] = row_count
                    
                    if file_details['errors']:
                        validation_report['invalid_files'] += 1
                    else:
                        validation_report['valid_files'] += 1
                else:
                    file_details['errors'].append('File does not exist')
                    validation_report['invalid_files'] += 1
                    
            except Exception as e:
                file_details['errors'].append(f'Validation error: {str(e)}')
                validation_report['invalid_files'] += 1
                validation_report['errors'].append(f'{file_path}: {str(e)}')
            
            validation_report['file_details'][str(file_path)] = file_details
        
        return validation_report