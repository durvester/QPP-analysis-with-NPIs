# CMS QPP Eligibility API Data Extractor

A comprehensive Python application for extracting healthcare provider eligibility data from the CMS Quality Payment Program (QPP) API across multiple years with flexible output formats and robust error handling.

## 🎯 Overview

This system extracts eligibility data from the CMS QPP API for any list of NPIs and any combination of years (2017-2030). The system processes NPIs through the CMS QPP API and generates clean, analyzable CSV files organized by year. Perfect for healthcare data analysts, researchers, and organizations working with Medicare provider data.

## ✨ Key Features

- **🗓️ Flexible Year Selection**: Extract data for any years from 2017-2030 
- **📊 Any NPI List**: Works with any CSV file containing an "NPI" column
- **🚀 Parallel Processing**: Process multiple years simultaneously for faster extraction
- **📈 Optimized Performance**: 4 requests/second with smart rate limiting
- **🔄 Resume Capability**: Checkpoint system allows resuming interrupted processing
- **📁 Organized Output**: Year-based folder structure (2023/, 2024/, 2025/)
- **🧹 Normalized CSV**: Clean relational tables instead of 133+ column files
- **📝 Complete Audit Trail**: Raw JSON responses saved for debugging
- **⚡ Production Ready**: Comprehensive logging, configuration, and CLI interface

## 📋 Prerequisites

- **Python 3.8+**
- **CSV file with "NPI" column** (case-sensitive)
- **Internet connection** for CMS API access

## 🚀 Quick Start

### 1. **Clone & Setup**

```bash
# Clone the repository
git clone https://github.com/your-username/eligibility-api-qpp.git
cd eligibility-api-qpp/cms_eligibility_extractor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Prepare Your NPI File**

Create a CSV file with your NPIs. **The only requirement is an "NPI" column** (case-sensitive):

```csv
NPI,ProviderName,Specialty
1234567890,Dr. John Smith,Cardiology
9876543210,Dr. Jane Doe,Family Medicine
5555555555,Sample Medical Group,Multi-Specialty
```

📋 **Use the template**: Copy `templates/npi_template.csv` as a starting point.

### 3. **Configure (Optional)**

```bash
# Copy the template
cp templates/.env.example .env

# Edit with your settings
EXTRACTION_YEARS=2023,2024,2025
NPI_CSV_PATH=../your_npis.csv
```

### 4. **Run Extraction**

```bash
# Test setup (no API calls)
python src/main.py --dry-run

# Extract data for default years (2023,2024,2025)
python src/main.py

# Extract specific years
EXTRACTION_YEARS=2024 python src/main.py

# Use custom NPI file
python src/main.py --npi-csv ../your_npis.csv
```

## 📊 Performance & Timing

- **Small lists** (10-100 NPIs): ~1-5 minutes
- **Medium lists** (1,000 NPIs): ~15-30 minutes  
- **Large lists** (10,000+ NPIs): ~2-6 hours
- **Success Rate**: ~65% (404s are normal for inactive providers)

### Running Tests

```bash
# Run all tests
python run_tests.py

# Or with pytest if installed
pytest tests/ -v
```

## 📁 Output Structure

**Year-organized, clean output structure:**

```
outputs/
├── csv/                          # Clean CSV files organized by year
│   ├── 2023/                     # 2023 data files
│   │   ├── providers_2023.csv    # Core provider information
│   │   ├── organizations_2023.csv # Organization details  
│   │   ├── individual_scenarios_2023.csv
│   │   ├── group_scenarios_2023.csv
│   │   └── apms_2023.csv         # Alternative Payment Models
│   ├── 2024/                     # 2024 data files
│   │   └── [...same structure...]
│   ├── 2025/                     # 2025 data files  
│   │   └── [...same structure...]
│   ├── data_dictionary.csv       # Field descriptions (global)
│   └── export_summary.csv        # Processing summary (all years)
├── raw/                          # Raw JSON responses for audit
│   ├── 2023/, 2024/, 2025/       # Raw API responses by year
├── logs/                         # Processing logs and checkpoints
└── reports/                      # Processing statistics
    └── processing_summary.json
```

## 🔧 Configuration Options

Set these environment variables or use command-line arguments:

| Variable | Default | Description |
|----------|---------|-------------|
| `EXTRACTION_YEARS` | `2023,2024,2025` | Comma-separated years to extract |
| `NPI_CSV_PATH` | `../templates/npi_template.csv` | Path to your NPI CSV file |
| `OUTPUT_BASE_DIR` | `./outputs` | Base output directory |
| `BATCH_SIZE` | `100` | NPIs to process in each batch |
| `CHECKPOINT_INTERVAL` | `1000` | Save progress every N NPIs |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

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