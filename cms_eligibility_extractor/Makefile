# Makefile for CMS QPP Eligibility Data Extractor

.PHONY: help install install-dev clean lint format type-check security test test-unit test-integration test-e2e test-web test-cli test-coverage test-report build check-deps pre-commit setup-dev docker-build docker-run docker-clean

# Default target
help:
	@echo "CMS QPP Eligibility Data Extractor - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  setup-dev        Complete development environment setup"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint             Run all linting checks"
	@echo "  format           Format code with black and isort"
	@echo "  type-check       Run type checking with mypy"
	@echo "  security         Run security checks"
	@echo "  pre-commit       Run pre-commit hooks on all files"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e         Run end-to-end tests only"
	@echo "  test-web         Run web application tests"
	@echo "  test-cli         Run CLI tests"
	@echo "  test-coverage    Run tests with coverage report"
	@echo "  test-report      Generate comprehensive test report"
	@echo ""
	@echo "Build Commands:"
	@echo "  build            Build distribution packages"
	@echo "  clean            Clean build artifacts and cache"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run application in Docker"
	@echo "  docker-clean     Clean Docker images and containers"
	@echo ""
	@echo "Utility Commands:"
	@echo "  check-deps       Check for missing dependencies"

# Installation commands
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test,docs]"

setup-dev: install-dev
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Development environment setup complete!"

# Code quality commands
lint:
	@echo "Running linting checks..."
	ruff check src web tests
	flake8 src web tests
	bandit -r src web -f json -o bandit-report.json || bandit -r src web
	pydocstyle src web

format:
	@echo "Formatting code..."
	black src web tests
	isort src web tests

type-check:
	@echo "Running type checks..."
	mypy src web

security:
	@echo "Running security checks..."
	bandit -r src web
	safety check --json --output safety-report.json || safety check

pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

# Testing commands
test:
	python tests/run_all_tests.py all

test-unit:
	python tests/run_all_tests.py unit

test-integration:
	python tests/run_all_tests.py integration

test-e2e:
	python tests/run_all_tests.py e2e

test-web:
	python tests/run_all_tests.py web

test-cli:
	python tests/run_all_tests.py cli

test-coverage:
	python tests/run_all_tests.py all --coverage

test-report:
	python tests/run_all_tests.py report

# Build commands
build:
	python -m build

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test-results.xml
	rm -rf bandit-report.json
	rm -rf safety-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Clean complete!"

# Docker commands
docker-build:
	docker build -t cms-eligibility-extractor .

docker-run:
	docker run -p 5000:5000 cms-eligibility-extractor

docker-clean:
	docker system prune -f
	docker image prune -f

# Utility commands
check-deps:
	python tests/run_all_tests.py --check-deps

# Development workflow shortcuts
dev-check: format lint type-check security test-unit
	@echo "Development checks complete!"

ci-check: lint type-check security test
	@echo "CI checks complete!"

# Quick development server
dev-server:
	@echo "Starting development server..."
	python web/app.py

# CLI development test
dev-cli:
	@echo "Running CLI with sample data..."
	python src/main.py --npi-csv templates/npi_template.csv --output-dir ./dev_outputs --years 2023 --dry-run

# Database operations (for future use)
db-init:
	@echo "Database initialization not yet implemented"

db-migrate:
	@echo "Database migration not yet implemented"

db-upgrade:
	@echo "Database upgrade not yet implemented"

# Documentation generation
docs:
	@echo "Documentation generation not yet implemented"
	# sphinx-build -b html docs docs/_build/html

docs-serve:
	@echo "Documentation server not yet implemented"
	# python -m http.server 8000 --directory docs/_build/html

# Performance testing
perf-test:
	@echo "Performance testing not yet implemented"

# Load testing
load-test:
	@echo "Load testing not yet implemented"

# Deployment helpers
deploy-staging:
	@echo "Staging deployment not yet implemented"

deploy-prod:
	@echo "Production deployment not yet implemented"

# Monitoring and health checks
health-check:
	@echo "Health check not yet implemented"

# Version management
version:
	python -c "import src; print(getattr(src, '__version__', 'Unknown'))"

# Environment validation
validate-env:
	@echo "Validating environment..."
	python -c "from src.config import load_config; config = load_config(); config.validate(); print('✅ Environment validation passed')"

# Quick project status
status:
	@echo "Project Status:"
	@echo "==============="
	@git status --porcelain | wc -l | xargs echo "Modified files:"
	@git log --oneline -5 | head -1 | xargs echo "Latest commit:"
	@find src web -name "*.py" | wc -l | xargs echo "Python files:"
	@find tests -name "test_*.py" | wc -l | xargs echo "Test files:"
	@echo ""
	@echo "Dependencies:"
	@pip list | grep -E "(flask|requests|pytest|black)" | head -5

# All checks for CI/CD
all-checks: clean install-dev format lint type-check security test-coverage
	@echo "🎉 All checks passed!"