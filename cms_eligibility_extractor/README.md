# CMS QPP Eligibility Data Extractor

Extract comprehensive eligibility data from the CMS Quality Payment Program (QPP) API for multiple years with flexible output formats.

## Features

- **Multi-Year Support**: Extract data for 2023, 2024, and 2025
- **Flexible Schema**: Handles optional fields gracefully
- **Multiple Output Formats**: CSV, SQLite, Excel, and raw JSON
- **Rate Limiting**: Automatic handling of API rate limits with exponential backoff
- **Resume Capability**: Continue processing from last checkpoint
- **Data Validation**: Schema validation with detailed error reporting
- **Progress Tracking**: Real-time progress bars and logging

## Quick Start

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Run Extraction**
   ```bash
   python src/main.py
   ```

## Output Formats

### Normalized CSV Files (Recommended)
- `providers_YYYY.csv` - Core provider information
- `organizations_YYYY.csv` - Organization details with provider_npi foreign key
- `individual_scenarios_YYYY.csv` - Individual eligibility scenarios
- `group_scenarios_YYYY.csv` - Group eligibility scenarios
- `apms_YYYY.csv` - Alternative Payment Model data
- `virtual_groups_YYYY.csv` - Virtual group information

### SQLite Database
- Single database file with related tables
- Enables complex queries across years
- Pre-built views for common analyses

### Excel Workbooks
- Multi-sheet workbooks with formatted data
- Includes data dictionary and summary statistics
- Pre-configured pivot tables and charts

## Project Structure

```
cms_eligibility_extractor/
├── src/
│   ├── api/              # CMS API client and rate limiting
│   ├── models/           # Pydantic data models
│   ├── processors/       # Data processing logic
│   ├── exporters/        # Output format generators
│   └── analysis/         # Data analysis utilities
├── tests/                # Comprehensive test suite
├── config/               # Configuration files
└── outputs/              # Generated output files
```

## Configuration

Key configuration files:
- `config/api_config.yaml` - API settings and rate limiting
- `config/field_schema.yaml` - Field definitions and validation rules
- `.env` - Environment-specific settings

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/test_api_client.py
pytest tests/test_schema_validation.py
```

## Data Quality

The system includes comprehensive data quality reporting:
- Field completeness statistics
- Validation error summaries
- Processing success rates
- Data type consistency checks

## Error Handling

- **404 NPIs**: Logged and excluded from final outputs
- **429 Rate Limits**: Automatic exponential backoff
- **Network Errors**: Configurable retry logic
- **Data Validation**: Detailed error reporting without failing entire process