# CMS QPP Eligibility API Data Extractor

A comprehensive Python application for extracting healthcare provider eligibility data from the CMS Quality Payment Program (QPP) API across multiple years with flexible output formats and robust error handling.

## 🎯 Overview

This system extracts eligibility data for **2023, 2024, and 2025** from approximately **45,000 NPIs**, processing them through the CMS QPP API and generating clean, analyzable CSV files. The system handles rate limiting, API errors, and provides comprehensive audit trails.

## ✨ Key Features

- **Multi-Year Support**: Extract data for 2023, 2024, and 2025 simultaneously
- **Flexible Schema**: Handles all possible API response fields gracefully
- **Rate Limiting**: Built-in exponential backoff for API rate limits (429 responses)
- **Error Handling**: Graceful handling of 404s, 400s, and server errors
- **Normalized CSV Output**: Clean, relational CSV files instead of unwieldy 133+ column files
- **Resume Capability**: Checkpoint system allows resuming interrupted processing
- **Raw Response Logging**: Complete audit trail for debugging discrepancies
- **Progress Tracking**: Real-time progress bars and detailed statistics
- **Production Ready**: Comprehensive logging, configuration, and CLI interface

## 📊 Expected Output

- **Processing Time**: 8-12 hours for ~45K NPIs across 3 years
- **Success Rate**: ~85% (some NPIs will return 404s, which is expected)
- **Clean Data**: Only successful 200 responses included in final CSV files
- **File Sizes**: ~30-50MB per CSV file per year

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Internet connection for CMS API access
- NPIs in CSV format (see `NPI.csv` example)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/eligibility-api-qpp.git
cd eligibility-api-qpp/cms_eligibility_extractor

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env with your preferred settings
```

### Basic Usage

```bash
# Test the setup (loads NPIs without making API calls)
python src/main.py --dry-run

# Extract data for all years (2023, 2024, 2025)
python src/main.py

# Extract specific years only
python src/main.py --years 2023 2024

# Use custom NPI file
python src/main.py --npi-csv /path/to/your/npis.csv

# Custom output directory
python src/main.py --output-dir /path/to/output
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Or with pytest if installed
pytest tests/ -v
```

## 📁 Output Structure

The system generates a well-organized output structure:

```
outputs/
├── csv/                          # Clean CSV files for analysis
│   ├── providers_2023.csv         # Core provider information
│   ├── organizations_2023.csv     # Organization details
│   ├── individual_scenarios_2023.csv  # Individual eligibility data
│   ├── group_scenarios_2023.csv   # Group eligibility data
│   ├── apms_2023.csv              # Alternative Payment Model data
│   ├── virtual_groups_2023.csv    # Virtual group information
│   ├── [...same files for 2024, 2025...]
│   ├── data_dictionary.csv        # Field descriptions
│   └── export_summary.csv         # Processing summary
├── raw/                          # Raw JSON responses for audit
│   ├── 2023/
│   ├── 2024/
│   └── 2025/
├── logs/                         # Processing logs and checkpoints
└── reports/                      # Processing statistics
    └── processing_summary.json
```

## 📋 CSV File Structure

Instead of one unwieldy file with 133+ columns, the system generates **6 normalized CSV files per year**:

### 1. `providers_YYYY.csv` (~25 columns)
Core provider information: NPI, name, provider type, years in Medicare, specialty, etc.

### 2. `organizations_YYYY.csv` 
Organization details with `npi` foreign key: TIN, organization name, address, facility info.

### 3. `individual_scenarios_YYYY.csv`
Individual provider eligibility scenarios: MIPS eligibility, hardship exemptions, rural status, etc.

### 4. `group_scenarios_YYYY.csv`
Group practice eligibility data with similar structure to individual scenarios.

### 5. `apms_YYYY.csv`
Alternative Payment Model participation: APM IDs, entity names, scores, performance data.

### 6. `virtual_groups_YYYY.csv`
Virtual group information: identifiers, claims types, special scenarios.

## 🔧 Configuration

### Environment Variables

Key configuration options (see `.env.example`):

```bash
# Input/Output
NPI_CSV_PATH=../NPI.csv
OUTPUT_BASE_DIR=./outputs

# Processing
CHECKPOINT_INTERVAL=1000
SAVE_RAW_RESPONSES=true

# Logging
LOG_LEVEL=INFO
```

### API Configuration

The system uses the CMS QPP API configuration in `config/api_config.yaml`:

- **Base URL**: `https://qpp.cms.gov`
- **Rate Limiting**: 2 requests/second with burst capacity
- **Retry Logic**: Exponential backoff (1s → 2s → 4s → 8s)
- **API Version**: v6 (latest)

## 🛠 Advanced Usage

### Resume Processing

If processing is interrupted, you can resume from the last checkpoint:

```bash
python src/main.py --resume
```

### Processing Specific Years

```bash
# Only process 2024 data
python src/main.py --years 2024

# Process 2023 and 2025 only
python src/main.py --years 2023 2025
```

### Debugging and Analysis

```bash
# Enable debug logging
python src/main.py --log-level DEBUG

# Skip CSV generation (useful for testing API connectivity)
python src/main.py --skip-csv
```

## 📊 Data Quality & Validation

The system includes comprehensive data validation:

- **NPI Format Validation**: Ensures 10-digit numeric NPIs
- **Schema Validation**: Validates API responses against expected structure
- **Deduplication**: Removes duplicate NPIs from input
- **Error Categorization**: Separates 404s, 400s, and other errors
- **Completeness Reporting**: Tracks field population rates

## 🧪 Testing

The test suite validates:

- NPI reading and validation logic
- Schema parsing with real CMS API response structure
- CSV export functionality
- Error handling scenarios

```bash
# Run basic tests
python run_tests.py

# Run with coverage (if pytest-cov installed)
pytest tests/ --cov=src
```

## 📈 Performance & Scalability

- **Memory Efficient**: Processes data in batches to handle large NPI lists
- **Rate Limit Aware**: Automatically handles CMS API rate limits
- **Resumable**: Checkpoint system prevents data loss during interruptions
- **Concurrent Ready**: Architecture supports future multi-threading enhancements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues, questions, or contributions:

1. Check the [Issues](https://github.com/your-username/eligibility-api-qpp/issues) page
2. Review the `CLAUDE.md` file for technical details
3. Run tests to validate your setup: `python run_tests.py`

## 🔍 API Documentation

This extractor works with the CMS Quality Payment Program Eligibility API. See the `Qpp_API_documentation/` directory for:

- API request samples
- Response schema documentation  
- Sample responses (200, 400, 404)

## 🏗 Architecture

```
cms_eligibility_extractor/
├── src/
│   ├── api/              # CMS API client and rate limiting
│   ├── models/           # Pydantic data models  
│   ├── processors/       # Data processing logic
│   ├── exporters/        # CSV export functionality
│   └── main.py          # Application entry point
├── tests/               # Comprehensive test suite
├── config/              # Configuration files
└── outputs/             # Generated data files
```

Built with flexibility and maintainability in mind, this system can easily be extended for additional output formats, new API versions, or enhanced processing capabilities.