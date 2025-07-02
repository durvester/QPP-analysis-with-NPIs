# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a documentation-only repository containing the CMS Quality Payment Program (QPP) Eligibility API specifications and sample data. It's part of the CMS Quality Payment Program system for tracking healthcare provider eligibility and performance metrics.

## Repository Structure

- **Qpp_API_documentation/**: Contains comprehensive API documentation
  - `eligibility_api_request_sample.md`: Sample API request format and parameters
  - `schema.Md`: Complete API response schema with all fields and data types
  - `sample_response_*.json`: Example API responses for different HTTP status codes (200, 400, 404)
- **NPI.csv**: Sample data file containing National Provider Identifier records with provider information
- **README.md**: Basic repository description (minimal content)

## API Overview

The QPP Eligibility API provides access to healthcare provider eligibility information:

- **Base URL**: `https://qpp.cms.gov`
- **Endpoint**: `GET /api/eligibility/npi/{npi}`
- **Purpose**: Look up public information for healthcare providers by National Provider Identifier (NPI)

### Key API Parameters
- `npi` (required): 10-digit National Provider Identifier
- `year` (optional): Performance year (e.g., 2023)
- `runNum` (optional): Data load sequence number (1-4)
- `Accept` header: API version specification (v4, v5, or v6)

## Data Structure

The API returns comprehensive provider information including:
- Basic provider details (name, NPI, provider type)
- Medicare enrollment information
- MIPS (Merit-based Incentive Payment System) eligibility
- APM (Alternative Payment Model) participation
- Organization affiliations and scenarios
- Quality scores and performance metrics
- Geographic and specialty classifications

## Development Notes

This repository contains no executable code - it's purely documentation and sample data. There are no build scripts, test frameworks, or deployment configurations to run.

For API integration work, reference the schema documentation and sample responses to understand the complete data structure and field definitions.