"""
Tests for flexible schema validation using the sample response.
"""

import pytest
import json
from pathlib import Path

from src.models.flexible_schema import EligibilityResponse, ProviderData


class TestSchemaValidation:
    """Test schema validation against sample CMS API response."""
    
    @pytest.fixture
    def sample_response_data(self):
        """Load the sample 200 response for testing."""
        # In a real test, you'd load this from the actual sample file
        # For now, we'll use the data structure from the documentation
        return {
            "data": {
                "firstName": "Buffy",
                "middleName": "A",
                "lastName": "Summers",
                "npi": "1234567890",
                "nationalProviderIdentifierType": 1,
                "firstApprovedDate": "2010-12-31",
                "yearsInMedicare": 7,
                "pecosEnrollmentDate": 2010,
                "newlyEnrolled": False,
                "qpStatus": "Q",
                "isMaqi": True,
                "qpScoreType": "MI",
                "amsMipsEligibleClinician": True,
                "organizations": [
                    {
                        "TIN": "XXXXXXXXXX",
                        "prvdrOrgName": "Scooby Gang Health Partners",
                        "isFacilityBased": True,
                        "addressLineOne": "1630 REVELLO DR SUITE 1",
                        "addressLineTwo": "",
                        "city": "SUNNYDALE",
                        "zip": "000261234",
                        "state": "CA",
                        "hospitalVbpName": "Johnson Medical Center",
                        "individualScenario": {
                            "aciHardship": True,
                            "aggregationLevel": 1,
                            "extremeHardship": True,
                            "extremeHardshipEventType": "Natural Disaster",
                            "extremeHardshipReasons": {
                                "quality": True,
                                "improvementActivities": True,
                                "aci": True,
                                "cost": True
                            },
                            "isEligible": {
                                "individual": False,
                                "group": False,
                                "mipsApm": False,
                                "virtualGroup": False
                            },
                            "specialty": {
                                "specialtyDescription": "Psychiatry",
                                "categoryReference": "Physicians",
                                "typeDescription": "Doctor of Medicine"
                            },
                            "specialtyCode": "72"
                        }
                    }
                ]
            }
        }
    
    def test_valid_response_parsing(self, sample_response_data):
        """Test that a valid response parses correctly."""
        response = EligibilityResponse(**sample_response_data)
        
        assert response.data.npi == "1234567890"
        assert response.data.firstName == "Buffy"
        assert response.data.lastName == "Summers"
        assert response.data.nationalProviderIdentifierType == 1
        assert response.data.qpStatus == "Q"
        assert response.data.qpScoreType == "MI"
    
    def test_required_fields_validation(self):
        """Test validation of required fields."""
        # Missing required fields should raise validation error
        invalid_data = {
            "data": {
                "firstName": "John",
                # Missing lastName and npi (required fields)
                "middleName": "A"
            }
        }
        
        with pytest.raises(ValueError):
            EligibilityResponse(**invalid_data)
    
    def test_optional_fields_handling(self):
        """Test that optional fields are handled correctly."""
        minimal_data = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe"
                # All other fields are optional
            }
        }
        
        response = EligibilityResponse(**minimal_data)
        
        assert response.data.npi == "1234567890"
        assert response.data.firstName == "John"
        assert response.data.lastName == "Doe"
        assert response.data.middleName is None
        assert response.data.organizations is None
    
    def test_npi_validation(self):
        """Test NPI format validation."""
        # Valid NPI
        valid_data = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe"
            }
        }
        
        response = EligibilityResponse(**valid_data)
        assert response.data.npi == "1234567890"
        
        # Invalid NPI (too short)
        invalid_data = {
            "data": {
                "npi": "123456789",
                "firstName": "John",
                "lastName": "Doe"
            }
        }
        
        with pytest.raises(ValueError, match="NPI must be exactly 10 digits"):
            EligibilityResponse(**invalid_data)
        
        # Invalid NPI (contains letters)
        invalid_data_letters = {
            "data": {
                "npi": "123456789a",
                "firstName": "John",
                "lastName": "Doe"
            }
        }
        
        with pytest.raises(ValueError, match="NPI must be exactly 10 digits"):
            EligibilityResponse(**invalid_data_letters)
    
    def test_enum_validation(self):
        """Test enumeration field validation."""
        # Valid qpStatus
        valid_data = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe",
                "qpStatus": "Y"
            }
        }
        
        response = EligibilityResponse(**valid_data)
        assert response.data.qpStatus == "Y"
        
        # Invalid qpStatus
        invalid_data = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe",
                "qpStatus": "INVALID"
            }
        }
        
        with pytest.raises(ValueError):
            EligibilityResponse(**invalid_data)
    
    def test_nested_objects_validation(self, sample_response_data):
        """Test validation of nested objects."""
        response = EligibilityResponse(**sample_response_data)
        
        # Check organization data
        org = response.data.organizations[0]
        assert org.TIN == "XXXXXXXXXX"
        assert org.prvdrOrgName == "Scooby Gang Health Partners"
        
        # Check individual scenario
        scenario = org.individualScenario
        assert scenario.aciHardship == True
        assert scenario.aggregationLevel == 1
        
        # Check extreme hardship reasons
        hardship_reasons = scenario.extremeHardshipReasons
        assert hardship_reasons.quality == True
        assert hardship_reasons.improvementActivities == True
        
        # Check eligibility flags
        eligibility = scenario.isEligible
        assert eligibility.individual == False
        assert eligibility.group == False
        
        # Check specialty
        specialty = scenario.specialty
        assert specialty.specialtyDescription == "Psychiatry"
        assert specialty.categoryReference == "Physicians"
    
    def test_missing_organization_tin(self):
        """Test validation when required TIN is missing from organization."""
        data_missing_tin = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe",
                "organizations": [
                    {
                        # Missing TIN (required for organization)
                        "prvdrOrgName": "Test Organization"
                    }
                ]
            }
        }
        
        with pytest.raises(ValueError):
            EligibilityResponse(**data_missing_tin)
    
    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed (for future API versions)."""
        data_with_extra = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe",
                "futureField": "some new value",  # Extra field
                "organizations": [
                    {
                        "TIN": "123456789",
                        "newOrgField": "new value"  # Extra field in nested object
                    }
                ]
            }
        }
        
        # Should not raise an error due to extra fields
        response = EligibilityResponse(**data_with_extra)
        assert response.data.npi == "1234567890"
    
    def test_array_fields_validation(self):
        """Test validation of array fields."""
        data_with_arrays = {
            "data": {
                "npi": "1234567890",
                "firstName": "John",
                "lastName": "Doe",
                "organizations": [
                    {
                        "TIN": "123456789",
                        "individualScenario": {
                            "extremeHardshipSources": ["auto-fema", "manual"],
                            "lowVolumeStatusReasons": [
                                {
                                    "lowVolStusRsnCd": "BOTH",
                                    "lowVolStusRsnDesc": "Both the unique beneficiaries and Part B"
                                }
                            ]
                        },
                        "apms": [
                            {
                                "entityName": "Test APM",
                                "apmId": "123",
                                "qpPatientScores": {
                                    "ae": 1234.5,
                                    "mi": 5678.9
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        response = EligibilityResponse(**data_with_arrays)
        
        # Check array fields
        scenario = response.data.organizations[0].individualScenario
        assert "auto-fema" in scenario.extremeHardshipSources
        assert "manual" in scenario.extremeHardshipSources
        
        # Check nested arrays
        assert len(scenario.lowVolumeStatusReasons) == 1
        assert scenario.lowVolumeStatusReasons[0].lowVolStusRsnCd == "BOTH"
        
        # Check APM data
        apm = response.data.organizations[0].apms[0]
        assert apm.entityName == "Test APM"
        assert apm.qpPatientScores.ae == 1234.5