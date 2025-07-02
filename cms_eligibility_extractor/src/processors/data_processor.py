"""
Data processor for converting CMS API responses to output models.
Handles flexible parsing and data flattening.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import asdict

from ..models.flexible_schema import EligibilityResponse, ProcessingMetadata
from ..models.output_models import (
    ProviderCoreRecord, OrganizationRecord, IndividualScenarioRecord,
    GroupScenarioRecord, ApmRecord, VirtualGroupRecord, DataQualityReport
)


logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes CMS API responses and converts them to normalized output records.
    """
    
    def __init__(self):
        self.stats = {
            'total_responses_processed': 0,
            'successful_conversions': 0,
            'conversion_errors': 0,
            'field_missing_counts': {},
            'validation_errors': {}
        }
    
    def process_eligibility_response(
        self, 
        response: EligibilityResponse, 
        year: int, 
        metadata: ProcessingMetadata
    ) -> Dict[str, List[Any]]:
        """
        Process an eligibility response into normalized records.
        
        Args:
            response: Validated eligibility response
            year: Performance year
            metadata: Processing metadata
            
        Returns:
            Dictionary containing lists of different record types
        """
        self.stats['total_responses_processed'] += 1
        
        try:
            records = {
                'providers': [],
                'organizations': [],
                'individual_scenarios': [],
                'group_scenarios': [],
                'apms': [],
                'virtual_groups': []
            }
            
            # Extract core provider data
            provider_record = self._extract_provider_core(response.data, year, metadata)
            records['providers'].append(provider_record)
            
            # Process organizations
            if response.data.organizations:
                for org_index, org in enumerate(response.data.organizations):
                    # Organization record
                    org_record = self._extract_organization(org, response.data.npi, year, org_index)
                    records['organizations'].append(org_record)
                    
                    # Individual scenario
                    if org.individualScenario:
                        ind_scenario = self._extract_individual_scenario(
                            org.individualScenario, response.data.npi, year, org_index
                        )
                        records['individual_scenarios'].append(ind_scenario)
                    
                    # Group scenario
                    if org.groupScenario:
                        group_scenario = self._extract_group_scenario(
                            org.groupScenario, response.data.npi, year, org_index
                        )
                        records['group_scenarios'].append(group_scenario)
                    
                    # APMs
                    if org.apms:
                        for apm_index, apm in enumerate(org.apms):
                            apm_record = self._extract_apm(
                                apm, response.data.npi, year, org_index, apm_index
                            )
                            records['apms'].append(apm_record)
                    
                    # Virtual Groups
                    if org.virtualGroups:
                        for vg_index, vg in enumerate(org.virtualGroups):
                            vg_record = self._extract_virtual_group(
                                vg, response.data.npi, year, org_index, vg_index
                            )
                            records['virtual_groups'].append(vg_record)
            
            self.stats['successful_conversions'] += 1
            return records
            
        except Exception as e:
            self.stats['conversion_errors'] += 1
            logger.error(f"Error processing response for NPI {metadata.npi}: {e}")
            raise
    
    def _extract_provider_core(self, data, year: int, metadata: ProcessingMetadata) -> ProviderCoreRecord:
        """Extract core provider information."""
        # Get specialty from deprecated field or from first organization
        specialty_desc = None
        category_ref = None
        type_desc = None
        
        if data.specialty:
            specialty_desc = data.specialty.specialtyDescription
            category_ref = data.specialty.categoryReference
            type_desc = data.specialty.typeDescription
        elif data.organizations and data.organizations[0].individualScenario and data.organizations[0].individualScenario.specialty:
            spec = data.organizations[0].individualScenario.specialty
            specialty_desc = spec.specialtyDescription
            category_ref = spec.categoryReference
            type_desc = spec.typeDescription
        
        return ProviderCoreRecord(
            npi=data.npi,
            year=year,
            firstName=data.firstName,
            lastName=data.lastName,
            middleName=data.middleName,
            nationalProviderIdentifierType=data.nationalProviderIdentifierType,
            firstApprovedDate=data.firstApprovedDate,
            yearsInMedicare=data.yearsInMedicare,
            pecosEnrollmentDate=data.pecosEnrollmentDate,
            newlyEnrolled=data.newlyEnrolled,
            qpStatus=data.qpStatus,
            isMaqi=data.isMaqi,
            qpScoreType=data.qpScoreType,
            amsMipsEligibleClinician=data.amsMipsEligibleClinician,
            specialtyDescription=specialty_desc,
            categoryReference=category_ref,
            typeDescription=type_desc,
            processed_at=metadata.processed_at
        )
    
    def _extract_organization(self, org, npi: str, year: int, org_index: int) -> OrganizationRecord:
        """Extract organization information."""
        return OrganizationRecord(
            npi=npi,
            year=year,
            org_index=org_index,
            TIN=org.TIN,
            prvdrOrgName=org.prvdrOrgName,
            isFacilityBased=org.isFacilityBased,
            addressLineOne=org.addressLineOne,
            addressLineTwo=org.addressLineTwo,
            city=org.city,
            zip=org.zip,
            state=org.state,
            hospitalVbpName=org.hospitalVbpName
        )
    
    def _extract_individual_scenario(self, scenario, npi: str, year: int, org_index: int) -> IndividualScenarioRecord:
        """Extract individual scenario information."""
        # Flatten extreme hardship reasons
        extreme_hardship_quality = None
        extreme_hardship_improvement = None
        extreme_hardship_aci = None
        extreme_hardship_cost = None
        
        if scenario.extremeHardshipReasons:
            extreme_hardship_quality = scenario.extremeHardshipReasons.quality
            extreme_hardship_improvement = scenario.extremeHardshipReasons.improvementActivities
            extreme_hardship_aci = scenario.extremeHardshipReasons.aci
            extreme_hardship_cost = scenario.extremeHardshipReasons.cost
        
        # Flatten extreme hardship sources (array to comma-separated string)
        extreme_hardship_sources = None
        if scenario.extremeHardshipSources:
            extreme_hardship_sources = ', '.join(scenario.extremeHardshipSources)
        
        # Flatten eligibility flags
        is_eligible_individual = None
        is_eligible_group = None
        is_eligible_mips_apm = None
        is_eligible_virtual_group = None
        
        if scenario.isEligible:
            is_eligible_individual = scenario.isEligible.individual
            is_eligible_group = scenario.isEligible.group
            is_eligible_mips_apm = scenario.isEligible.mipsApm
            is_eligible_virtual_group = scenario.isEligible.virtualGroup
        
        # Flatten specialty information
        specialty_description = None
        specialty_category = None
        specialty_type = None
        
        if scenario.specialty:
            specialty_description = scenario.specialty.specialtyDescription
            specialty_category = scenario.specialty.categoryReference
            specialty_type = scenario.specialty.typeDescription
        
        return IndividualScenarioRecord(
            npi=npi,
            year=year,
            org_index=org_index,
            aciHardship=scenario.aciHardship,
            aciReweighting=scenario.aciReweighting,
            aggregationLevel=scenario.aggregationLevel,
            ambulatorySurgicalCenter=scenario.ambulatorySurgicalCenter,
            eligibilityScenario=scenario.eligibilityScenario,
            extremeHardship=scenario.extremeHardship,
            extremeHardshipEventType=scenario.extremeHardshipEventType,
            extremeHardship_quality=extreme_hardship_quality,
            extremeHardship_improvementActivities=extreme_hardship_improvement,
            extremeHardship_aci=extreme_hardship_aci,
            extremeHardship_cost=extreme_hardship_cost,
            extremeHardshipSources=extreme_hardship_sources,
            hasHospitalVbpCCN=scenario.hasHospitalVbpCCN,
            hasPaymentAdjustmentCCN=scenario.hasPaymentAdjustmentCCN,
            hospitalBasedClinician=scenario.hospitalBasedClinician,
            hospitalVbpName=scenario.hospitalVbpName,
            hospitalVbpScore=scenario.hospitalVbpScore,
            hpsaClinician=scenario.hpsaClinician,
            iaStudy=scenario.iaStudy,
            isEligible_individual=is_eligible_individual,
            isEligible_group=is_eligible_group,
            isEligible_mipsApm=is_eligible_mips_apm,
            isEligible_virtualGroup=is_eligible_virtual_group,
            isFacilityBased=scenario.isFacilityBased,
            isOptedIn=scenario.isOptedIn,
            isOptInEligible=scenario.isOptInEligible,
            lowVolumeServices=scenario.lowVolumeServices,
            lowVolumeSwitch=scenario.lowVolumeSwitch,
            mipsEligibleSwitch=scenario.mipsEligibleSwitch,
            nonPatientFacing=scenario.nonPatientFacing,
            optInDecisionDate=scenario.optInDecisionDate,
            ruralClinician=scenario.ruralClinician,
            smallGroupPractitioner=scenario.smallGroupPractitioner,
            specialtyCode=scenario.specialtyCode,
            specialty_description=specialty_description,
            specialty_categoryReference=specialty_category,
            specialty_typeDescription=specialty_type
        )
    
    def _extract_group_scenario(self, scenario, npi: str, year: int, org_index: int) -> GroupScenarioRecord:
        """Extract group scenario information."""
        # Flatten extreme hardship reasons
        extreme_hardship_quality = None
        extreme_hardship_improvement = None
        extreme_hardship_aci = None
        extreme_hardship_cost = None
        
        if scenario.extremeHardshipReasons:
            extreme_hardship_quality = scenario.extremeHardshipReasons.quality
            extreme_hardship_improvement = scenario.extremeHardshipReasons.improvementActivities
            extreme_hardship_aci = scenario.extremeHardshipReasons.aci
            extreme_hardship_cost = scenario.extremeHardshipReasons.cost
        
        # Flatten extreme hardship sources
        extreme_hardship_sources = None
        if scenario.extremeHardshipSources:
            extreme_hardship_sources = ', '.join(scenario.extremeHardshipSources)
        
        # Handle group eligibility (can be bool or string)
        is_eligible_group = None
        if scenario.isEligible and 'group' in scenario.isEligible:
            value = scenario.isEligible['group']
            is_eligible_group = str(value) if value is not None else None
        
        return GroupScenarioRecord(
            npi=npi,
            year=year,
            org_index=org_index,
            aciHardship=scenario.aciHardship,
            aciReweighting=scenario.aciReweighting,
            aggregationLevel=scenario.aggregationLevel,
            ambulatorySurgicalCenter=scenario.ambulatorySurgicalCenter,
            extremeHardship=scenario.extremeHardship,
            extremeHardshipEventType=scenario.extremeHardshipEventType,
            extremeHardship_quality=extreme_hardship_quality,
            extremeHardship_improvementActivities=extreme_hardship_improvement,
            extremeHardship_aci=extreme_hardship_aci,
            extremeHardship_cost=extreme_hardship_cost,
            extremeHardshipSources=extreme_hardship_sources,
            hospitalBasedClinician=scenario.hospitalBasedClinician,
            hpsaClinician=scenario.hpsaClinician,
            iaStudy=scenario.iaStudy,
            isEligible_group=is_eligible_group,
            isFacilityBased=scenario.isFacilityBased,
            isOptedIn=scenario.isOptedIn,
            isOptInEligible=scenario.isOptInEligible,
            lowVolumeServices=scenario.lowVolumeServices,
            lowVolumeSwitch=scenario.lowVolumeSwitch,
            mipsEligibleSwitch=scenario.mipsEligibleSwitch,
            nonPatientFacing=scenario.nonPatientFacing,
            optInDecisionDate=scenario.optInDecisionDate,
            ruralClinician=scenario.ruralClinician,
            smallGroupPractitioner=scenario.smallGroupPractitioner
        )
    
    def _extract_apm(self, apm, npi: str, year: int, org_index: int, apm_index: int) -> ApmRecord:
        """Extract APM information."""
        # Flatten QP patient scores
        qp_patient_ae = qp_patient_ai = qp_patient_at = qp_patient_me = qp_patient_mi = None
        if apm.qpPatientScores:
            qp_patient_ae = apm.qpPatientScores.ae
            qp_patient_ai = apm.qpPatientScores.ai
            qp_patient_at = apm.qpPatientScores.at
            qp_patient_me = apm.qpPatientScores.me
            qp_patient_mi = apm.qpPatientScores.mi
        
        # Flatten QP payment scores
        qp_payment_ae = qp_payment_ai = qp_payment_at = qp_payment_me = qp_payment_mi = None
        if apm.qpPaymentScores:
            qp_payment_ae = apm.qpPaymentScores.ae
            qp_payment_ai = apm.qpPaymentScores.ai
            qp_payment_at = apm.qpPaymentScores.at
            qp_payment_me = apm.qpPaymentScores.me
            qp_payment_mi = apm.qpPaymentScores.mi
        
        # Flatten extreme hardship reasons
        extreme_hardship_quality = None
        extreme_hardship_improvement = None
        extreme_hardship_aci = None
        extreme_hardship_cost = None
        
        if apm.extremeHardshipReasons:
            extreme_hardship_quality = apm.extremeHardshipReasons.quality
            extreme_hardship_improvement = apm.extremeHardshipReasons.improvementActivities
            extreme_hardship_aci = apm.extremeHardshipReasons.aci
            extreme_hardship_cost = apm.extremeHardshipReasons.cost
        
        # Flatten extreme hardship sources
        extreme_hardship_sources = None
        if apm.extremeHardshipSources:
            extreme_hardship_sources = ', '.join(apm.extremeHardshipSources)
        
        return ApmRecord(
            npi=npi,
            year=year,
            org_index=org_index,
            apm_index=apm_index,
            entityName=apm.entityName,
            lvtFlag=apm.lvtFlag,
            lvtPayments=apm.lvtPayments,
            lvtPatients=apm.lvtPatients,
            lvtSmallStatus=apm.lvtSmallStatus,
            lvtPerformanceYear=apm.lvtPerformanceYear,
            apmId=apm.apmId,
            apmName=apm.apmName,
            subdivisionId=apm.subdivisionId,
            subdivisionName=apm.subdivisionName,
            advancedApmFlag=apm.advancedApmFlag,
            mipsApmFlag=apm.mipsApmFlag,
            providerRelationshipCode=apm.providerRelationshipCode,
            qpPatientScores_ae=qp_patient_ae,
            qpPatientScores_ai=qp_patient_ai,
            qpPatientScores_at=qp_patient_at,
            qpPatientScores_me=qp_patient_me,
            qpPatientScores_mi=qp_patient_mi,
            qpPaymentScores_ae=qp_payment_ae,
            qpPaymentScores_ai=qp_payment_ai,
            qpPaymentScores_at=qp_payment_at,
            qpPaymentScores_me=qp_payment_me,
            qpPaymentScores_mi=qp_payment_mi,
            complexPatientScore=apm.complexPatientScore,
            finalQpcScore=apm.finalQpcScore,
            extremeHardship=apm.extremeHardship,
            extremeHardship_quality=extreme_hardship_quality,
            extremeHardship_improvementActivities=extreme_hardship_improvement,
            extremeHardship_aci=extreme_hardship_aci,
            extremeHardship_cost=extreme_hardship_cost,
            extremeHardshipEventType=apm.extremeHardshipEventType,
            extremeHardshipSources=extreme_hardship_sources,
            isOptedIn=apm.isOptedIn
        )
    
    def _extract_virtual_group(self, vg, npi: str, year: int, org_index: int, vg_index: int) -> VirtualGroupRecord:
        """Extract virtual group information."""
        # Flatten special scenario fields
        ss_aci_reweighting = None
        ss_non_patient_facing = None
        ss_rural_clinician = None
        ss_hpsa_clinician = None
        ss_hospital_based = None
        ss_ambulatory_surgical = None
        ss_aci_hardship = None
        ss_ia_study = None
        ss_small_group = None
        ss_extreme_hardship = None
        ss_extreme_hardship_event = None
        
        if vg.specialScenario:
            ss = vg.specialScenario
            ss_aci_reweighting = ss.aciReweighting
            ss_non_patient_facing = ss.nonPatientFacing
            ss_rural_clinician = ss.ruralClinician
            ss_hpsa_clinician = ss.hpsaClinician
            ss_hospital_based = ss.hospitalBasedClinician
            ss_ambulatory_surgical = ss.ambulatorySurgicalCenter
            ss_aci_hardship = ss.aciHardship
            ss_ia_study = ss.iaStudy
            ss_small_group = ss.smallGroupPractitioner
            ss_extreme_hardship = ss.extremeHardship
            ss_extreme_hardship_event = ss.extremeHardshipEventType
        
        return VirtualGroupRecord(
            npi=npi,
            year=year,
            org_index=org_index,
            virtual_group_index=vg_index,
            virtualGroupIdentifier=vg.virtualGroupIdentifier,
            claimsTypes=vg.claimsTypes,
            lowVolumeSwitch=vg.lowVolumeSwitch,
            beneficiaryCount=vg.beneficiaryCount,
            allowedCharges=vg.allowedCharges,
            hospitalVbpName=vg.hospitalVbpName,
            isFacilityBased=vg.isFacilityBased,
            hospitalVbpScore=vg.hospitalVbpScore,
            specialScenario_aciReweighting=ss_aci_reweighting,
            specialScenario_nonPatientFacing=ss_non_patient_facing,
            specialScenario_ruralClinician=ss_rural_clinician,
            specialScenario_hpsaClinician=ss_hpsa_clinician,
            specialScenario_hospitalBasedClinician=ss_hospital_based,
            specialScenario_ambulatorySurgicalCenter=ss_ambulatory_surgical,
            specialScenario_aciHardship=ss_aci_hardship,
            specialScenario_iaStudy=ss_ia_study,
            specialScenario_smallGroupPractitioner=ss_small_group,
            specialScenario_extremeHardship=ss_extreme_hardship,
            specialScenario_extremeHardshipEventType=ss_extreme_hardship_event
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()
    
    def generate_data_quality_report(
        self, 
        year: int, 
        processing_metadata: List[ProcessingMetadata],
        processing_time: float
    ) -> DataQualityReport:
        """
        Generate a data quality report for the processed data.
        
        Args:
            year: Performance year
            processing_metadata: List of processing metadata for all NPIs
            processing_time: Total processing time in seconds
            
        Returns:
            Data quality report
        """
        total_npis = len(processing_metadata)
        successful = sum(1 for m in processing_metadata if m.success)
        failed = total_npis - successful
        
        # Count error types
        npis_404 = sum(1 for m in processing_metadata if m.status_code == 404)
        npis_400 = sum(1 for m in processing_metadata if m.status_code == 400)
        npis_other_errors = failed - npis_404 - npis_400
        
        # Calculate field completeness (would need actual data analysis)
        field_completeness = {}  # TODO: Implement field completeness analysis
        
        # Validation statistics
        validation_errors = self.stats.get('validation_errors', {})
        
        # Calculate average processing time
        avg_processing_time = processing_time / total_npis if total_npis > 0 else 0.0
        
        return DataQualityReport(
            year=year,
            total_npis_processed=total_npis,
            successful_responses=successful,
            failed_responses=failed,
            npis_with_404=npis_404,
            npis_with_400=npis_400,
            npis_with_other_errors=npis_other_errors,
            field_completeness=field_completeness,
            validation_errors=validation_errors,
            average_processing_time=avg_processing_time,
            total_processing_time=processing_time,
            api_rate_limit_hits=0,  # TODO: Get from API client
            generated_at=datetime.now()
        )