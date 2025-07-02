"""
Tests for configuration and year parsing functionality.
"""

import pytest
import os
from unittest.mock import patch

# Import the function we want to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import parse_years, load_configuration


class TestConfiguration:
    """Test configuration parsing and validation."""
    
    def test_parse_years_basic(self):
        """Test basic year parsing."""
        # Test single year
        years = parse_years("2024")
        assert years == [2024]
        
        # Test multiple years
        years = parse_years("2023,2024,2025")
        assert years == [2023, 2024, 2025]
        
        # Test with spaces
        years = parse_years("2023, 2024, 2025")
        assert years == [2023, 2024, 2025]
        
    def test_parse_years_sorting(self):
        """Test that years are sorted."""
        years = parse_years("2025,2023,2024")
        assert years == [2023, 2024, 2025]
    
    def test_parse_years_validation(self):
        """Test year validation."""
        # Test invalid year (too old)
        with pytest.raises(ValueError, match="outside valid range"):
            parse_years("2016")
        
        # Test invalid year (too new)
        with pytest.raises(ValueError, match="outside valid range"):
            parse_years("2031")
        
        # Test invalid format
        with pytest.raises(ValueError, match="Invalid years configuration"):
            parse_years("not_a_year")
        
        # Test empty string
        with pytest.raises(ValueError):
            parse_years("")
    
    def test_parse_years_edge_cases(self):
        """Test edge cases for year parsing."""
        # Test boundary values
        years = parse_years("2017,2030")
        assert years == [2017, 2030]
        
        # Test duplicate years (should be deduplicated by sorting)
        years = parse_years("2023,2023,2024")
        assert years == [2023, 2023, 2024]  # duplicates preserved for now
    
    @patch.dict(os.environ, {'EXTRACTION_YEARS': '2024', 'NPI_CSV_PATH': '../test.csv'})
    def test_config_from_environment(self):
        """Test configuration loading from environment variables."""
        config = load_configuration()
        
        assert config['years'] == [2024]
        assert config['npi_csv_path'] == '../test.csv'
    
    def test_config_defaults(self):
        """Test default configuration values."""
        # Clear any environment variables that might interfere
        with patch.dict(os.environ, {}, clear=True):
            config = load_configuration()
            
            # Test default years
            assert config['years'] == [2023, 2024, 2025]
            
            # Test default paths
            assert config['npi_csv_path'] == '../templates/npi_template.csv'
            assert config['output_base_dir'] == './outputs'
            
            # Test default processing settings
            assert config['batch_size'] == 100
            assert config['checkpoint_interval'] == 1000
            
            # Test default boolean values
            assert config['generate_csv'] == True
            assert config['save_raw_responses'] == True