# CMS QPP Eligibility Data Extractor

A comprehensive tool to extract eligibility data from the CMS Quality Payment Program (QPP) API. Features both a command-line interface for automation and a user-friendly web application for interactive use.

## 🌟 Features

- **🖥️ Dual Interface**: Command-line tool and web-based GUI
- **📅 Multi-Year Support**: Extract data for 2023, 2024, and 2025
- **🔄 Real-time Processing**: Live progress tracking in web interface
- **📊 Multiple Output Formats**: CSV, SQLite, Excel, and raw JSON
- **⚡ Rate Limiting**: Automatic API rate limit handling with exponential backoff
- **🔧 Unified Configuration**: Environment-based configuration system
- **✅ Comprehensive Testing**: Unit, integration, and end-to-end tests
- **🐳 Docker Support**: Ready-to-deploy containers
- **🛡️ Production Ready**: Error handling, validation, and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Internet connection for CMS API access

### Option 1: Web Application (Recommended)

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd cms_eligibility_extractor
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install python-dotenv pydantic requests PyYAML flask flask-wtf tqdm pandas
   ```

2. **Start Web Server**
   ```bash
   python web/app.py
   ```

3. **Use Web Interface**
   - Open browser to http://localhost:5000
   - Upload your NPI CSV file (must have 'NPI' column)
   - Select years and configure options
   - Monitor real-time progress
   - Download ZIP archive with results

### Option 2: Command Line Interface

1. **Setup Environment**
   ```bash
   git clone <repository-url>
   cd cms_eligibility_extractor
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install python-dotenv pydantic requests PyYAML tqdm pandas
   ```

2. **Basic Usage**
   ```bash
   # Help and options
   python src/main.py --help
   
   # Test with dry run (no API calls)
   python src/main.py --npi-csv your_file.csv --dry-run
   
   # Full extraction
   python src/main.py --npi-csv your_file.csv --years 2023 2024
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

## Detailed Usage

### Web Application Interface

The web interface provides an intuitive way to process NPI data without command-line knowledge.

**Features:**
- Drag-and-drop file upload
- Real-time progress tracking
- Configurable processing options
- Automatic error handling
- Download results as ZIP archive

**CSV File Requirements:**
- Must contain a column named `npi`, `npis`, or `npi_number`
- NPIs must be 10-digit numbers (e.g., 1234567890)
- UTF-8 encoded CSV format
- Maximum file size: 50MB

**Processing Options:**
- **Years**: Select 2023, 2024, and/or 2025
- **Batch Size**: Number of NPIs to process together (1-1000)
- **Save Raw Responses**: Keep original JSON for debugging
- **Parallel Processing**: Process multiple years simultaneously

### Command Line Interface

The CLI provides advanced options and scripting capabilities.

**Basic Usage:**
```bash
# Process with default settings
python src/main.py

# Specify custom NPI file
python src/main.py --npi-csv /path/to/npis.csv

# Process specific years
python src/main.py --years 2024 2025

# Custom output directory
python src/main.py --output-dir /path/to/outputs

# Dry run (test without API calls)
python src/main.py --dry-run

# Resume from checkpoint
python src/main.py --resume
```

**Advanced Options:**
```bash
# Skip CSV export (useful for testing)
python src/main.py --skip-csv

# Custom log level
python src/main.py --log-level DEBUG

# Environment variable configuration
export NPI_CSV_PATH="/path/to/npis.csv"
export EXTRACTION_YEARS="2024,2025"
export OUTPUT_BASE_DIR="/custom/output"
python src/main.py
```

## 📁 Project Structure

```
cms_eligibility_extractor/
├── src/                  # Core application logic
│   ├── api/              # CMS API client and rate limiting
│   ├── models/           # Data models and schema validation
│   ├── processors/       # Data processing and orchestration
│   ├── services/         # Business logic services
│   ├── exporters/        # Output format generators
│   ├── config.py         # Unified configuration system
│   └── main.py           # CLI entry point
├── web/                  # Web application
│   ├── app.py            # Flask application factory
│   ├── routes.py         # Web routes and background processing
│   ├── forms.py          # Form validation with Flask-WTF
│   ├── error_handlers.py # Comprehensive error handling
│   ├── utils.py          # Web utilities and file management
│   └── templates/        # HTML templates with Bootstrap
├── static/               # CSS and JavaScript assets
├── tests/                # Comprehensive test suite
│   ├── test_*_comprehensive.py  # Unit and integration tests
│   ├── test_e2e_*.py     # End-to-end tests
│   └── run_all_tests.py  # Test runner
├── scripts/              # Development and deployment scripts
├── config/               # Legacy configuration files
├── .env.example          # Configuration template
├── pyproject.toml        # Python project configuration
├── Makefile              # Development commands
└── docker-compose.yml    # Container orchestration
```

## ⚙️ Configuration

The application uses a **unified configuration system** that supports:

- **Environment Variables**: Set via `.env` file or system environment
- **Configuration Files**: YAML and .env file support  
- **Command Line Overrides**: CLI arguments override all other settings
- **Validation**: Automatic validation with helpful error messages

### Key Configuration Options

```bash
# Core settings
EXTRACTION_YEARS=2023,2024,2025
NPI_CSV_PATH=./your_npis.csv

# API settings  
CMS_API_BASE_URL=https://qpp.cms.gov
API_TIMEOUT=30
BATCH_SIZE=100

# Web application
WEB_HOST=0.0.0.0
WEB_PORT=5000
SECRET_KEY=your-secret-key-here

# Output settings
OUTPUT_BASE_DIR=./outputs
GENERATE_CSV=true
SAVE_RAW_RESPONSES=true
```

Copy `.env.example` to `.env` and customize as needed.

## 🧪 Testing

### Running Tests

The project includes a comprehensive test suite with a custom test runner:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python tests/run_all_tests.py all

# Run specific test categories
python tests/run_all_tests.py unit          # Unit tests only
python tests/run_all_tests.py integration   # Integration tests
python tests/run_all_tests.py e2e           # End-to-end tests
python tests/run_all_tests.py web           # Web application tests
python tests/run_all_tests.py cli           # CLI tests

# Run with coverage report
python tests/run_all_tests.py all --coverage

# Generate comprehensive test report
python tests/run_all_tests.py report
```

### Test Coverage

The test suite includes:
- **Unit Tests**: API client, data models, configuration system
- **Integration Tests**: Multi-component workflows and data processing
- **End-to-End Tests**: Complete CLI and web application workflows
- **Web Application Tests**: Form validation, routes, error handling, background processing
- **API Client Tests**: Rate limiting, retry logic, statistics calculation
- **Error Handling Tests**: Custom exceptions, validation, edge cases

### Development Testing

```bash
# Quick development checks
make dev-check    # Format, lint, type-check, and unit tests

# Full CI simulation
make ci-check     # All checks including security and full test suite
```

## Deployment

### Docker Deployment (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access web interface
open http://localhost:5000

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Manual Deployment

```bash
# Setup environment
python -m venv venv
source venv/bin/activate
pip install python-dotenv pydantic requests PyYAML flask flask-wtf tqdm pandas

# Configure application
cp .env.example .env
# Edit .env with your settings

# Start web application
python web/app.py

# Or run CLI
python src/main.py --npi-csv your_data.csv --years 2023
```

### Production Configuration

For production deployment, set these environment variables:

```bash
export SECRET_KEY="your-secure-secret-key"
export FLASK_DEBUG="false"
export WEB_HOST="0.0.0.0"
export WEB_PORT="80"
export UPLOAD_FOLDER="/app/uploads"
export TEMP_FOLDER="/app/outputs"
export ENVIRONMENT="production"
```

## 🛠️ Development

### Setup Development Environment

```bash
# Automated setup
python scripts/setup_dev.py

# Or manual setup
make setup-dev

# Available development commands
make help           # Show all available commands
make format         # Code formatting with black and isort
make lint           # Comprehensive linting
make test           # Run test suite
make dev-server     # Start development web server
make dev-cli        # Test CLI with sample data
```

### Code Quality Tools

The project includes comprehensive code quality tools:

- **Black + isort**: Automatic code formatting
- **Ruff + Flake8**: Fast linting and style checking  
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Pre-commit hooks**: Automated quality checks on commit
- **GitHub Actions**: CI/CD pipeline with multi-Python testing

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Performance Considerations

- **Memory Usage**: Large CSV files (>10MB) may require 2-4GB RAM
- **Processing Time**: ~1-2 seconds per NPI depending on API response time
- **Rate Limiting**: Default 4 requests/second (configurable)
- **Concurrent Processing**: Web interface supports parallel year processing
- **File Storage**: Temporary files auto-cleanup after 24 hours

## Troubleshooting

### Common Issues

**Web Application Won't Start**
```bash
# Check if port is available
lsof -i :5000

# Check dependencies
pip install -r requirements.txt

# Check Python version (requires 3.8+)
python --version
```

**File Upload Fails**
- Verify CSV has NPI column (`npi`, `npis`, or `npi_number`)
- Check file size (<50MB)
- Ensure NPIs are 10-digit numbers
- Verify UTF-8 encoding

**Processing Fails or Slow**
- Check internet connection
- Verify API access to qpp.cms.gov
- Review rate limiting settings in `config/api_config.yaml`
- Check available memory for large files

**API Errors**
- 404 errors are normal (NPIs not in QPP system)
- 429 errors indicate rate limiting (automatic retry)
- 500+ errors suggest CMS API issues

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Web application
export DEBUG="True"
python run_web_app.py

# CLI application
python src/main.py --log-level DEBUG
```

### Getting Help

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Review API documentation in `Qpp_API_documentation/`
3. Enable debug logging for detailed error information
4. Verify configuration against `config/` examples

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