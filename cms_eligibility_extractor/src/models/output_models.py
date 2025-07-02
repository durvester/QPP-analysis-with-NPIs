"""
Output models for different export formats.
Defines the structure for CSV, SQLite, and Excel exports.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CSVFieldMapping:
    """Mapping configuration for CSV fields."""
    source_path: str  # Dot notation path in JSON (e.g., "data.firstName")
    csv_column: str   # Column name in CSV
    data_type: str    # Expected data type (str, int, float, bool)
    default_value: Any = None  # Default value if field is missing
    is_array: bool = False     # True if field contains array data


class ProviderCoreRecord(BaseModel):
    """Core provider information for normalized CSV export."""
    npi: str
    year: int
    firstName: str
    lastName: str
    middleName: Optional[str] = None
    nationalProviderIdentifierType: Optional[int] = None
    firstApprovedDate: Optional[str] = None
    yearsInMedicare: Optional[int] = None
    pecosEnrollmentDate: Optional[int] = None
    newlyEnrolled: Optional[bool] = None
    qpStatus: Optional[str] = None
    isMaqi: Optional[bool] = None
    qpScoreType: Optional[str] = None
    amsMipsEligibleClinician: Optional[bool] = None
    
    # Specialty information (from deprecated top-level or from org scenario)
    specialtyDescription: Optional[str] = None
    categoryReference: Optional[str] = None
    typeDescription: Optional[str] = None
    
    # Processing metadata
    processed_at: datetime
    data_source: str = "CMS_QPP_API"


class OrganizationRecord(BaseModel):
    """Organization details for normalized CSV export."""
    npi: str  # Foreign key to provider
    year: int
    org_index: int  # Index within organizations array for this provider
    
    TIN: Optional[str]
    prvdrOrgName: Optional[str] = None
    isFacilityBased: Optional[bool] = None
    addressLineOne: Optional[str] = None
    addressLineTwo: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    state: Optional[str] = None
    hospitalVbpName: Optional[str] = None


class IndividualScenarioRecord(BaseModel):
    """Individual scenario details for normalized CSV export."""
    npi: str  # Foreign key to provider
    year: int
    org_index: int  # Foreign key to organization
    
    aciHardship: Optional[bool] = None
    aciReweighting: Optional[bool] = None
    aggregationLevel: Optional[int] = None
    ambulatorySurgicalCenter: Optional[bool] = None
    eligibilityScenario: Optional[int] = None
    extremeHardship: Optional[bool] = None
    extremeHardshipEventType: Optional[str] = None
    
    # Flattened extreme hardship reasons
    extremeHardship_quality: Optional[bool] = None
    extremeHardship_improvementActivities: Optional[bool] = None
    extremeHardship_aci: Optional[bool] = None
    extremeHardship_cost: Optional[bool] = None
    
    # Flattened extreme hardship sources (as comma-separated string)
    extremeHardshipSources: Optional[str] = None
    
    hasHospitalVbpCCN: Optional[bool] = None
    hasPaymentAdjustmentCCN: Optional[bool] = None
    hospitalBasedClinician: Optional[bool] = None
    hospitalVbpName: Optional[str] = None
    hospitalVbpScore: Optional[float] = None
    hpsaClinician: Optional[bool] = None
    iaStudy: Optional[bool] = None
    
    # Flattened eligibility flags
    isEligible_individual: Optional[bool] = None
    isEligible_group: Optional[bool] = None
    isEligible_mipsApm: Optional[bool] = None
    isEligible_virtualGroup: Optional[bool] = None
    
    isFacilityBased: Optional[bool] = None
    isOptedIn: Optional[bool] = None
    isOptInEligible: Optional[bool] = None
    lowVolumeServices: Optional[int] = None
    lowVolumeSwitch: Optional[bool] = None
    mipsEligibleSwitch: Optional[bool] = None
    nonPatientFacing: Optional[bool] = None
    optInDecisionDate: Optional[str] = None
    ruralClinician: Optional[bool] = None
    smallGroupPractitioner: Optional[bool] = None
    specialtyCode: Optional[str] = None
    
    # Flattened specialty information
    specialty_description: Optional[str] = None
    specialty_categoryReference: Optional[str] = None
    specialty_typeDescription: Optional[str] = None


class GroupScenarioRecord(BaseModel):
    """Group scenario details for normalized CSV export."""
    npi: str  # Foreign key to provider
    year: int
    org_index: int  # Foreign key to organization
    
    aciHardship: Optional[bool] = None
    aciReweighting: Optional[bool] = None
    aggregationLevel: Optional[int] = None
    ambulatorySurgicalCenter: Optional[bool] = None
    extremeHardship: Optional[bool] = None
    extremeHardshipEventType: Optional[str] = None
    
    # Flattened extreme hardship reasons
    extremeHardship_quality: Optional[bool] = None
    extremeHardship_improvementActivities: Optional[bool] = None
    extremeHardship_aci: Optional[bool] = None
    extremeHardship_cost: Optional[bool] = None
    
    # Flattened extreme hardship sources
    extremeHardshipSources: Optional[str] = None
    
    hospitalBasedClinician: Optional[bool] = None
    hpsaClinician: Optional[bool] = None
    iaStudy: Optional[bool] = None
    
    # Group eligibility (can be bool or string)
    isEligible_group: Optional[str] = None  # Using string to handle both types
    
    isFacilityBased: Optional[bool] = None
    isOptedIn: Optional[bool] = None
    isOptInEligible: Optional[bool] = None
    lowVolumeServices: Optional[int] = None
    lowVolumeSwitch: Optional[bool] = None
    mipsEligibleSwitch: Optional[bool] = None
    nonPatientFacing: Optional[bool] = None
    optInDecisionDate: Optional[str] = None
    ruralClinician: Optional[bool] = None
    smallGroupPractitioner: Optional[bool] = None


class ApmRecord(BaseModel):
    """APM details for normalized CSV export."""
    npi: str  # Foreign key to provider
    year: int
    org_index: int  # Foreign key to organization
    apm_index: int  # Index within APMs array for this organization
    
    entityName: Optional[str] = None
    lvtFlag: Optional[bool] = None
    lvtPayments: Optional[float] = None
    lvtPatients: Optional[int] = None
    lvtSmallStatus: Optional[bool] = None
    lvtPerformanceYear: Optional[int] = None
    apmId: Optional[str] = None
    apmName: Optional[str] = None
    subdivisionId: Optional[str] = None
    subdivisionName: Optional[str] = None
    advancedApmFlag: Optional[bool] = None
    mipsApmFlag: Optional[bool] = None
    providerRelationshipCode: Optional[str] = None
    
    # Flattened QP patient scores
    qpPatientScores_ae: Optional[float] = None
    qpPatientScores_ai: Optional[float] = None
    qpPatientScores_at: Optional[float] = None
    qpPatientScores_me: Optional[float] = None
    qpPatientScores_mi: Optional[float] = None
    
    # Flattened QP payment scores
    qpPaymentScores_ae: Optional[float] = None
    qpPaymentScores_ai: Optional[float] = None
    qpPaymentScores_at: Optional[float] = None
    qpPaymentScores_me: Optional[float] = None
    qpPaymentScores_mi: Optional[float] = None
    
    complexPatientScore: Optional[float] = None
    finalQpcScore: Optional[float] = None
    extremeHardship: Optional[bool] = None
    
    # Flattened extreme hardship reasons
    extremeHardship_quality: Optional[bool] = None
    extremeHardship_improvementActivities: Optional[bool] = None
    extremeHardship_aci: Optional[bool] = None
    extremeHardship_cost: Optional[bool] = None
    
    extremeHardshipEventType: Optional[str] = None
    extremeHardshipSources: Optional[str] = None
    isOptedIn: Optional[bool] = None


class VirtualGroupRecord(BaseModel):
    """Virtual group details for normalized CSV export."""
    npi: str  # Foreign key to provider
    year: int
    org_index: int  # Foreign key to organization
    virtual_group_index: int  # Index within virtual groups array
    
    virtualGroupIdentifier: Optional[str] = None
    claimsTypes: Optional[str] = None
    lowVolumeSwitch: Optional[bool] = None
    beneficiaryCount: Optional[int] = None
    allowedCharges: Optional[float] = None
    hospitalVbpName: Optional[str] = None
    isFacilityBased: Optional[bool] = None
    hospitalVbpScore: Optional[float] = None
    
    # Flattened special scenario fields
    specialScenario_aciReweighting: Optional[bool] = None
    specialScenario_nonPatientFacing: Optional[bool] = None
    specialScenario_ruralClinician: Optional[bool] = None
    specialScenario_hpsaClinician: Optional[bool] = None
    specialScenario_hospitalBasedClinician: Optional[bool] = None
    specialScenario_ambulatorySurgicalCenter: Optional[bool] = None
    specialScenario_aciHardship: Optional[bool] = None
    specialScenario_iaStudy: Optional[bool] = None
    specialScenario_smallGroupPractitioner: Optional[bool] = None
    specialScenario_extremeHardship: Optional[bool] = None
    specialScenario_extremeHardshipEventType: Optional[str] = None


class DataQualityReport(BaseModel):
    """Data quality report for analysis."""
    year: int
    total_npis_processed: int
    successful_responses: int
    failed_responses: int
    npis_with_404: int
    npis_with_400: int
    npis_with_other_errors: int
    
    # Field completeness statistics
    field_completeness: Dict[str, float]  # field_name -> percentage_complete
    
    # Validation statistics
    validation_errors: Dict[str, int]  # error_type -> count
    
    # Processing statistics
    average_processing_time: float
    total_processing_time: float
    api_rate_limit_hits: int
    
    generated_at: datetime


class ExportSummary(BaseModel):
    """Summary of export operations."""
    year: int
    export_formats: List[str]  # ['csv', 'sqlite', 'excel']
    
    # Record counts by format
    csv_records: Dict[str, int]  # table_name -> record_count
    sqlite_tables: List[str]
    excel_sheets: List[str]
    
    # File paths
    output_files: Dict[str, str]  # format -> file_path
    
    # Data quality
    data_quality_report: DataQualityReport
    
    export_completed_at: datetime