"""
Flexible Pydantic models for CMS QPP Eligibility API responses.
Handles optional fields gracefully and validates data types.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class QpStatusEnum(str, Enum):
    Y = "Y"
    N = "N"
    P = "P"
    Q = "Q"
    R = "R"


class QpScoreTypeEnum(str, Enum):
    MI = "MI"
    ME = "ME"
    AE = "AE"
    AT = "AT"
    AI = "AI"


class ProviderTypeEnum(int, Enum):
    INDIVIDUAL = 1
    ORGANIZATION = 2


class AggregationLevelEnum(int, Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2


class ExtremeHardshipSourceEnum(str, Enum):
    AUTO_FEMA = "auto-fema"
    MANUAL = "manual"
    AUTO_COVID = "auto-covid"


class LowVolumeReasonEnum(str, Enum):
    BENE = "BENE"
    CHRG = "CHRG"
    SRVC = "SRVC"
    BOTH = "BOTH"
    BENE_SRVC = "BENE/SRVC"
    CHRG_SRVC = "CHRG/SRVC"
    ALL = "ALL"
    EMPTY = ""


class ExtremeHardshipReasons(BaseModel):
    """Extreme hardship exemption reasons."""
    quality: Optional[bool] = None
    improvementActivities: Optional[bool] = None
    aci: Optional[bool] = None
    cost: Optional[bool] = None


class IsEligible(BaseModel):
    """Eligibility flags for different scenarios."""
    individual: Optional[bool] = None
    group: Optional[Union[bool, str]] = None
    mipsApm: Optional[bool] = None
    virtualGroup: Optional[bool] = None


class Specialty(BaseModel):
    """Provider specialty information."""
    specialtyDescription: Optional[str] = None
    categoryReference: Optional[str] = None
    typeDescription: Optional[str] = None


class LowVolumeStatusReason(BaseModel):
    """Low volume status reason details."""
    lowVolStusRsnCd: Optional[LowVolumeReasonEnum] = None
    lowVolStusRsnDesc: Optional[str] = None


class QpPatientScores(BaseModel):
    """Quality payment patient scores."""
    ae: Optional[float] = None
    ai: Optional[float] = None
    at: Optional[float] = None
    me: Optional[float] = None
    mi: Optional[float] = None


class QpPaymentScores(BaseModel):
    """Quality payment payment scores."""
    ae: Optional[float] = None
    ai: Optional[float] = None
    at: Optional[float] = None
    me: Optional[float] = None
    mi: Optional[float] = None


class IndividualScenario(BaseModel):
    """Individual provider scenario data."""
    aciHardship: Optional[bool] = None
    aciReweighting: Optional[bool] = None
    aggregationLevel: Optional[AggregationLevelEnum] = None
    ambulatorySurgicalCenter: Optional[bool] = None
    eligibilityScenario: Optional[int] = None
    extremeHardship: Optional[bool] = None
    extremeHardshipEventType: Optional[str] = None
    extremeHardshipReasons: Optional[ExtremeHardshipReasons] = None
    extremeHardshipSources: Optional[List[ExtremeHardshipSourceEnum]] = None
    hasHospitalVbpCCN: Optional[bool] = None
    hasPaymentAdjustmentCCN: Optional[bool] = None
    hospitalBasedClinician: Optional[bool] = None
    hospitalVbpName: Optional[str] = None
    hospitalVbpScore: Optional[float] = None
    hpsaClinician: Optional[bool] = None
    iaStudy: Optional[bool] = None
    isEligible: Optional[IsEligible] = None
    isFacilityBased: Optional[bool] = None
    isOptedIn: Optional[bool] = None
    isOptInEligible: Optional[bool] = None
    lowVolumeServices: Optional[int] = None
    lowVolumeStatusReasons: Optional[List[LowVolumeStatusReason]] = None
    lowVolumeSwitch: Optional[bool] = None
    mipsEligibleSwitch: Optional[bool] = None
    nonPatientFacing: Optional[bool] = None
    optInDecisionDate: Optional[str] = None
    ruralClinician: Optional[bool] = None
    smallGroupPractitioner: Optional[bool] = None
    specialty: Optional[Specialty] = None
    specialtyCode: Optional[str] = None


class GroupScenario(BaseModel):
    """Group provider scenario data."""
    aciHardship: Optional[bool] = None
    aciReweighting: Optional[bool] = None
    aggregationLevel: Optional[AggregationLevelEnum] = None
    ambulatorySurgicalCenter: Optional[bool] = None
    extremeHardship: Optional[bool] = None
    extremeHardshipEventType: Optional[str] = None
    extremeHardshipReasons: Optional[ExtremeHardshipReasons] = None
    extremeHardshipSources: Optional[List[ExtremeHardshipSourceEnum]] = None
    hospitalBasedClinician: Optional[bool] = None
    hpsaClinician: Optional[bool] = None
    iaStudy: Optional[bool] = None
    isEligible: Optional[Dict[str, Union[bool, str]]] = None
    isFacilityBased: Optional[bool] = None
    isOptedIn: Optional[bool] = None
    isOptInEligible: Optional[bool] = None
    lowVolumeServices: Optional[int] = None
    lowVolumeStatusReasons: Optional[List[LowVolumeStatusReason]] = None
    lowVolumeSwitch: Optional[bool] = None
    mipsEligibleSwitch: Optional[bool] = None
    nonPatientFacing: Optional[bool] = None
    optInDecisionDate: Optional[str] = None
    ruralClinician: Optional[bool] = None
    smallGroupPractitioner: Optional[bool] = None


class Apm(BaseModel):
    """Alternative Payment Model data."""
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
    qpPatientScores: Optional[QpPatientScores] = None
    qpPaymentScores: Optional[QpPaymentScores] = None
    complexPatientScore: Optional[float] = None
    finalQpcScore: Optional[float] = None
    extremeHardship: Optional[bool] = None
    extremeHardshipReasons: Optional[ExtremeHardshipReasons] = None
    extremeHardshipEventType: Optional[str] = None
    extremeHardshipSources: Optional[List[ExtremeHardshipSourceEnum]] = None
    isOptedIn: Optional[bool] = None


class SpecialScenario(BaseModel):
    """Special scenario data for virtual groups."""
    aciReweighting: Optional[bool] = None
    nonPatientFacing: Optional[bool] = None
    ruralClinician: Optional[bool] = None
    hpsaClinician: Optional[bool] = None
    hospitalBasedClinician: Optional[bool] = None
    ambulatorySurgicalCenter: Optional[bool] = None
    aciHardship: Optional[bool] = None
    iaStudy: Optional[bool] = None
    smallGroupPractitioner: Optional[bool] = None
    extremeHardship: Optional[bool] = None
    extremeHardshipReasons: Optional[ExtremeHardshipReasons] = None
    extremeHardshipEventType: Optional[str] = None
    extremeHardshipSources: Optional[List[ExtremeHardshipSourceEnum]] = None


class VirtualGroup(BaseModel):
    """Virtual group data."""
    virtualGroupIdentifier: Optional[str] = None
    claimsTypes: Optional[str] = None
    lowVolumeSwitch: Optional[bool] = None
    lowVolumeStatusReasons: Optional[List[LowVolumeStatusReason]] = None
    beneficiaryCount: Optional[int] = None
    allowedCharges: Optional[float] = None
    hospitalVbpName: Optional[str] = None
    isFacilityBased: Optional[bool] = None
    hospitalVbpScore: Optional[float] = None
    specialScenario: Optional[SpecialScenario] = None


class Organization(BaseModel):
    """Organization/practice information."""
    TIN: str = Field(..., description="Taxpayer Identification Number (required)")
    prvdrOrgName: Optional[str] = None
    isFacilityBased: Optional[bool] = None
    addressLineOne: Optional[str] = None
    addressLineTwo: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    state: Optional[str] = None
    hospitalVbpName: Optional[str] = None
    individualScenario: Optional[IndividualScenario] = None
    groupScenario: Optional[GroupScenario] = None
    apms: Optional[List[Apm]] = None
    virtualGroups: Optional[List[VirtualGroup]] = None


class ProviderData(BaseModel):
    """Complete provider eligibility data."""
    # Required fields
    npi: str = Field(..., description="National Provider Identifier (required)")
    firstName: str = Field(..., description="Provider first name (required)")
    lastName: str = Field(..., description="Provider last name (required)")
    
    # Optional core fields
    middleName: Optional[str] = None
    nationalProviderIdentifierType: Optional[ProviderTypeEnum] = None
    firstApprovedDate: Optional[str] = None
    yearsInMedicare: Optional[int] = None
    pecosEnrollmentDate: Optional[int] = None
    newlyEnrolled: Optional[bool] = None
    qpStatus: Optional[QpStatusEnum] = None
    isMaqi: Optional[bool] = None
    qpScoreType: Optional[QpScoreTypeEnum] = None
    amsMipsEligibleClinician: Optional[bool] = None
    
    # Organizations array (optional)
    organizations: Optional[List[Organization]] = None
    
    # Deprecated specialty field (handle gracefully)
    specialty: Optional[Specialty] = None

    @validator('npi')
    def validate_npi(cls, v):
        """Validate NPI format (10 digits)."""
        if not v.isdigit() or len(v) != 10:
            raise ValueError('NPI must be exactly 10 digits')
        return v

    @validator('firstApprovedDate', pre=True)
    def validate_date_format(cls, v):
        """Handle various date formats."""
        if v is None:
            return v
        # Keep as string for now, can parse later if needed
        return str(v)


class EligibilityResponse(BaseModel):
    """Complete CMS API response wrapper."""
    data: ProviderData = Field(..., description="Provider eligibility data")

    class Config:
        # Allow extra fields that we might not have modeled
        extra = "allow"


class ProcessingMetadata(BaseModel):
    """Metadata for tracking processing status."""
    npi: str
    year: int
    success: bool
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.now)
    retry_count: int = 0