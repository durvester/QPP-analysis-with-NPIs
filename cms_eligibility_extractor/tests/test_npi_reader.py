"""
Tests for NPI reader functionality.
"""

import pytest
import csv
import tempfile
from pathlib import Path

from src.processors.npi_reader import NPIReader


class TestNPIReader:
    """Test cases for NPIReader class."""
    
    def create_test_csv(self, data, filename="test_npis.csv"):
        """Helper to create test CSV files."""
        temp_file = Path(tempfile.gettempdir()) / filename
        
        with open(temp_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        return str(temp_file)
    
    def test_validate_npi_valid(self):
        """Test NPI validation with valid NPIs."""
        reader = NPIReader("dummy.csv")
        
        valid_npis = [
            "1234567890",
            "0000000001",
            "9999999999"
        ]
        
        for npi in valid_npis:
            assert reader.validate_npi(npi), f"NPI {npi} should be valid"
    
    def test_validate_npi_invalid(self):
        """Test NPI validation with invalid NPIs."""
        reader = NPIReader("dummy.csv")
        
        invalid_npis = [
            "123456789",    # Too short
            "12345678901",  # Too long
            "123456789a",   # Contains letter
            "123-456-7890", # Contains hyphens
            "",             # Empty
            None,           # None
            "   ",          # Whitespace only
            "12345 67890"   # Contains space
        ]
        
        for npi in invalid_npis:
            assert not reader.validate_npi(npi), f"NPI {npi} should be invalid"
    
    def test_read_npis_basic(self):
        """Test basic NPI reading functionality."""
        test_data = [
            ["NPI", "NAME", "EMAIL"],
            ["1234567890", "John Doe", "john@example.com"],
            ["0987654321", "Jane Smith", "jane@example.com"],
            ["5555555555", "Bob Johnson", "bob@example.com"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file)
        
        npis = reader.read_npis()
        
        assert len(npis) == 3
        assert "1234567890" in npis
        assert "0987654321" in npis
        assert "5555555555" in npis
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_read_npis_with_invalid(self):
        """Test NPI reading with invalid NPIs."""
        test_data = [
            ["NPI", "NAME"],
            ["1234567890", "Valid NPI"],
            ["123456789", "Invalid - too short"],
            ["", "Empty NPI"],
            ["abcdefghij", "Invalid - letters"],
            ["0987654321", "Valid NPI"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file)
        
        npis = reader.read_npis()
        
        assert len(npis) == 2
        assert "1234567890" in npis
        assert "0987654321" in npis
        
        # Check statistics
        stats = reader.get_stats()
        assert stats['valid_npis'] == 2
        assert stats['invalid_npis'] == 2
        assert stats['blank_npis'] == 1
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_read_npis_with_duplicates(self):
        """Test NPI reading with duplicate NPIs."""
        test_data = [
            ["NPI", "NAME"],
            ["1234567890", "First occurrence"],
            ["0987654321", "Unique NPI"],
            ["1234567890", "Duplicate NPI"],
            ["5555555555", "Another unique"],
            ["0987654321", "Another duplicate"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file)
        
        npis = reader.read_npis()
        
        # Should only get unique NPIs
        assert len(npis) == 3
        assert "1234567890" in npis
        assert "0987654321" in npis
        assert "5555555555" in npis
        
        # Check statistics
        stats = reader.get_stats()
        assert stats['valid_npis'] == 3
        assert stats['duplicate_npis'] == 2
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_read_with_metadata(self):
        """Test reading NPIs with additional metadata."""
        test_data = [
            ["NPI", "PROVIDER_NAME", "STATE", "SPECIALTY"],
            ["1234567890", "Dr. Smith", "CA", "Internal Medicine"],
            ["0987654321", "Dr. Jones", "NY", "Cardiology"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file)
        
        records = reader.read_with_metadata(['PROVIDER_NAME', 'STATE'])
        
        assert len(records) == 2
        
        record1 = records[0]
        assert record1['npi'] == "1234567890"
        assert record1['PROVIDER_NAME'] == "Dr. Smith"
        assert record1['STATE'] == "CA"
        assert 'row_number' in record1
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_get_column_info(self):
        """Test getting CSV column information."""
        test_data = [
            ["NPI", "NAME", "EMAIL", "STATE"],
            ["1234567890", "John Doe", "john@example.com", "CA"],
            ["0987654321", "Jane Smith", "jane@example.com", "NY"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file)
        
        info = reader.get_column_info()
        
        assert info['total_columns'] == 4
        assert 'NPI' in info['column_names']
        assert 'NAME' in info['column_names']
        assert info['has_npi_column'] == True
        assert info['total_rows'] == 2  # Data rows, not including header
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_missing_npi_column(self):
        """Test handling of missing NPI column."""
        test_data = [
            ["PROVIDER_ID", "NAME"],
            ["123", "John Doe"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file, npi_column="NPI")
        
        with pytest.raises(ValueError, match="NPI column 'NPI' not found"):
            reader.read_npis()
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_custom_npi_column(self):
        """Test reading from custom NPI column name."""
        test_data = [
            ["PROVIDER_ID", "NAME"],
            ["1234567890", "John Doe"],
            ["0987654321", "Jane Smith"]
        ]
        
        csv_file = self.create_test_csv(test_data)
        reader = NPIReader(csv_file, npi_column="PROVIDER_ID")
        
        npis = reader.read_npis()
        
        assert len(npis) == 2
        assert "1234567890" in npis
        assert "0987654321" in npis
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_empty_csv(self):
        """Test handling of empty CSV file."""
        csv_file = self.create_test_csv([])
        reader = NPIReader(csv_file)
        
        # Should raise error for empty file (no headers/columns)
        with pytest.raises(ValueError, match="NPI column 'NPI' not found"):
            npis = reader.read_npis()
        
        # Cleanup
        Path(csv_file).unlink()
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        reader = NPIReader("nonexistent_file.csv")
        
        with pytest.raises(FileNotFoundError):
            reader.read_npis()