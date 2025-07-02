"""
NPI reader for extracting NPIs from CSV file.
"""

import csv
import logging
from typing import List, Set, Iterator, Optional, Dict, Any
from pathlib import Path
import re


logger = logging.getLogger(__name__)


class NPIReader:
    """
    Reads NPIs from CSV file with validation and deduplication.
    """
    
    def __init__(self, csv_path: str, npi_column: str = "NPI"):
        """
        Initialize NPI reader.
        
        Args:
            csv_path: Path to CSV file containing NPIs
            npi_column: Name of column containing NPIs
        """
        self.csv_path = Path(csv_path)
        self.npi_column = npi_column
        
        # Validation statistics
        self.stats = {
            'total_rows': 0,
            'valid_npis': 0,
            'invalid_npis': 0,
            'duplicate_npis': 0,
            'blank_npis': 0
        }
        
        # Track invalid NPIs for reporting
        self.invalid_npis = []
        self.duplicate_npis = []
        
    def validate_npi(self, npi: str) -> bool:
        """
        Validate NPI format.
        
        Args:
            npi: NPI string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not npi or not isinstance(npi, str):
            return False
            
        # Clean up the NPI (remove whitespace, etc.)
        npi = npi.strip()
        
        # Must be exactly 10 digits
        if not re.match(r'^\d{10}$', npi):
            return False
            
        return True
    
    def read_npis(self, skip_validation: bool = False) -> List[str]:
        """
        Read and validate NPIs from CSV file.
        
        Args:
            skip_validation: If True, skip NPI format validation
            
        Returns:
            List of unique valid NPIs
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        npis = []
        seen_npis = set()
        
        logger.info(f"Reading NPIs from {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except csv.Error:
                    # Default to comma if sniffer fails
                    delimiter = ','
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Validate that NPI column exists
                if reader.fieldnames is None or self.npi_column not in reader.fieldnames:
                    available_columns = ', '.join(reader.fieldnames or [])
                    raise ValueError(
                        f"NPI column '{self.npi_column}' not found. "
                        f"Available columns: {available_columns}"
                    )
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    self.stats['total_rows'] += 1
                    
                    npi = row.get(self.npi_column, '').strip()
                    
                    # Handle blank NPIs
                    if not npi:
                        self.stats['blank_npis'] += 1
                        logger.debug(f"Blank NPI found at row {row_num}")
                        continue
                    
                    # Validate NPI format
                    if not skip_validation and not self.validate_npi(npi):
                        self.stats['invalid_npis'] += 1
                        self.invalid_npis.append((row_num, npi))
                        logger.warning(f"Invalid NPI '{npi}' at row {row_num}")
                        continue
                    
                    # Check for duplicates
                    if npi in seen_npis:
                        self.stats['duplicate_npis'] += 1
                        self.duplicate_npis.append((row_num, npi))
                        logger.debug(f"Duplicate NPI '{npi}' at row {row_num}")
                        continue
                    
                    # Valid, unique NPI
                    npis.append(npi)
                    seen_npis.add(npi)
                    self.stats['valid_npis'] += 1
        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
        
        logger.info(f"Successfully read {len(npis)} unique valid NPIs")
        self._log_statistics()
        
        return npis
    
    def read_npis_batch(self, batch_size: int = 1000, skip_validation: bool = False) -> Iterator[List[str]]:
        """
        Read NPIs in batches for memory-efficient processing.
        
        Args:
            batch_size: Number of NPIs per batch
            skip_validation: If True, skip NPI format validation
            
        Yields:
            Batches of NPIs
        """
        all_npis = self.read_npis(skip_validation=skip_validation)
        
        for i in range(0, len(all_npis), batch_size):
            batch = all_npis[i:i + batch_size]
            logger.debug(f"Yielding batch {i // batch_size + 1}: {len(batch)} NPIs")
            yield batch
    
    def read_with_metadata(self, additional_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Read NPIs with additional metadata from CSV.
        
        Args:
            additional_columns: Additional columns to include in output
            
        Returns:
            List of dictionaries with NPI and metadata
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        results = []
        seen_npis = set()
        additional_columns = additional_columns or []
        
        logger.info(f"Reading NPIs with metadata from {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Validate columns exist
                missing_columns = []
                if self.npi_column not in reader.fieldnames:
                    missing_columns.append(self.npi_column)
                
                for col in additional_columns:
                    if col not in reader.fieldnames:
                        missing_columns.append(col)
                
                if missing_columns:
                    available_columns = ', '.join(reader.fieldnames or [])
                    raise ValueError(
                        f"Columns not found: {missing_columns}. "
                        f"Available columns: {available_columns}"
                    )
                
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total_rows'] += 1
                    
                    npi = row.get(self.npi_column, '').strip()
                    
                    if not npi:
                        self.stats['blank_npis'] += 1
                        continue
                    
                    if not self.validate_npi(npi):
                        self.stats['invalid_npis'] += 1
                        self.invalid_npis.append((row_num, npi))
                        continue
                    
                    if npi in seen_npis:
                        self.stats['duplicate_npis'] += 1
                        self.duplicate_npis.append((row_num, npi))
                        continue
                    
                    # Build result record
                    record = {'npi': npi, 'row_number': row_num}
                    
                    # Add additional columns
                    for col in additional_columns:
                        record[col] = row.get(col, '')
                    
                    results.append(record)
                    seen_npis.add(npi)
                    self.stats['valid_npis'] += 1
        
        except Exception as e:
            logger.error(f"Error reading CSV file with metadata: {e}")
            raise
        
        logger.info(f"Successfully read {len(results)} records with metadata")
        self._log_statistics()
        
        return results
    
    def get_column_info(self) -> Dict[str, Any]:
        """
        Get information about CSV columns.
        
        Returns:
            Dictionary with column information
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                columns = reader.fieldnames or []
                
                # Count total rows
                row_count = sum(1 for _ in reader)
                
        except Exception as e:
            logger.error(f"Error analyzing CSV file: {e}")
            raise
        
        return {
            'file_path': str(self.csv_path),
            'file_size_mb': self.csv_path.stat().st_size / (1024 * 1024),
            'delimiter': delimiter,
            'total_columns': len(columns),
            'column_names': columns,
            'total_rows': row_count,
            'has_npi_column': self.npi_column in columns
        }
    
    def _log_statistics(self):
        """Log processing statistics."""
        logger.info("NPI Processing Statistics:")
        logger.info(f"  Total rows processed: {self.stats['total_rows']}")
        logger.info(f"  Valid NPIs: {self.stats['valid_npis']}")
        logger.info(f"  Invalid NPIs: {self.stats['invalid_npis']}")
        logger.info(f"  Duplicate NPIs: {self.stats['duplicate_npis']}")
        logger.info(f"  Blank NPIs: {self.stats['blank_npis']}")
        
        if self.stats['total_rows'] > 0:
            success_rate = (self.stats['valid_npis'] / self.stats['total_rows']) * 100
            logger.info(f"  Success rate: {success_rate:.1f}%")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        
        # Add additional information
        stats['invalid_npi_examples'] = self.invalid_npis[:10]  # First 10 examples
        stats['duplicate_npi_examples'] = self.duplicate_npis[:10]  # First 10 examples
        
        if stats['total_rows'] > 0:
            stats['success_rate'] = (stats['valid_npis'] / stats['total_rows'])
        else:
            stats['success_rate'] = 0.0
            
        return stats
    
    def export_invalid_npis(self, output_path: str):
        """
        Export invalid NPIs to a CSV file for review.
        
        Args:
            output_path: Path to output CSV file
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['row_number', 'invalid_npi', 'issue'])
            
            # Write invalid NPIs
            for row_num, npi in self.invalid_npis:
                writer.writerow([row_num, npi, 'invalid_format'])
            
            # Write duplicates
            for row_num, npi in self.duplicate_npis:
                writer.writerow([row_num, npi, 'duplicate'])
        
        logger.info(f"Exported {len(self.invalid_npis) + len(self.duplicate_npis)} invalid NPIs to {output_path}")