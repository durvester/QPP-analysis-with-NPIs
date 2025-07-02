Collapse allobject
dataCollapse allobject
firstNameCollapse allstring
First name

Example"Buffy"
middleNameCollapse allstring
Often is middle initial rather than full middle name

Example"A"
lastNameCollapse allstring
Last name

Example"Summers"
npiCollapse allstring
National Provider Identifier (NPI) is a unique 10-digit identification number issued to health care providers by CMS.

Example"1234567890"
nationalProviderIdentifierTypeCollapse allinteger
This is a numeric code describing the type of provider that is is represented by the National Provider Identifier (NPI). Possible values-

1 Individual
2 Organization
Allowed values12
firstApprovedDateCollapse allstring
The first date an enrollment was approved for this NPI across all enrollments

Example"2010-12-31"
yearsInMedicareCollapse allinteger
Example7
pecosEnrollmentDateCollapse allinteger
Date of enrollment into Provider Enrollment, Chain and Ownership System (PECOS)

Example2010
newlyEnrolledCollapse allboolean
Examplefalse
qpStatusCollapse allstring
Qualifying APM Participant

Allowed values"Y""N""P""Q""R"
Example"Q"
isMaqiCollapse allboolean
True if clinician has been granted a MAQI Demonstration Waiver

qpScoreTypeCollapse allstring
The category in which an APM participant is QP

Allowed values"MI""ME""AE""AT""AI"
Example"MI"
amsMipsEligibleClinicianCollapse allboolean
MIPS Eligible Clinician (EC) Indicator

Exampletrue
organizationsCollapse allarray<object>
ItemsCollapse allobject
TINCollapse allstring
Masked Taxpayer Identification Number (TIN)

Example"XXXXXXXXXX"
prvdrOrgNameCollapse allstring
If provider is a practice, rather than an individual, practice name will be displayed. Will be undefined if no base records are found for the relevant TIN.

Example"Scooby Gang Health Partners"
isFacilityBasedCollapse allboolean
True if the threshold of facility based encounters is met

addressLineOneCollapse allstring
Uppercased street number, street name, and street suffix abbreviation. Can include secondary unit information such as suite. Will be undefined if no base records are found for the relevant TIN.

Example"1630 REVELLO DR SUITE 1"
addressLineTwoCollapse allstring
Second address line. Can be an empty value. Will be undefined if no base records are found for the relevant TIN.

Example""
cityCollapse allstring
Address city. Will be undefined if no base records are found for the relevant TIN.

Example"SUNNYDALE"
zipCollapse allstring
Nine digit zip code. Will be undefined if no base records are found for the relevant TIN.

Example"000261234"
stateCollapse allstring
Uppercased state abbreviation. Will be undefined if no base records are found for the relevant TIN.

Example"CA"
hospitalVbpNameCollapse allstring
Facility name within the Hospital Value-Based Purchasing Program

Example"Johnson Medical Center"
individualScenarioCollapse allobject
aciHardshipCollapse allboolean
True if there is an approved ACI Hardship Exemption application

aciReweightingCollapse allboolean
True if the group meets the conditions necessary for ACI Reweighting

aggregationLevelCollapse allinteger
Allowed values12
Example1
ambulatorySurgicalCenterCollapse allboolean
True if clinician met the threshold for being designated as an Ambulatory Surgical Center (ASC). ASCs provide surgery without an overnight hospital stay.

Examplefalse
eligibilityScenarioCollapse allinteger
Number reflecting the eligibility profile which is used to manage user interface messaging. This value has no impact on eligibility and is simply used to control UI content.

Example2300
extremeHardshipCollapse allboolean
True if Extreme and Uncontrollable Circumstance Exemption credit has been received

extremeHardshipEventTypeCollapse allstring
Type of extreme hardship event

Example"Natural Disaster"
extremeHardshipReasonsCollapse allobject
qualityCollapse allboolean
True if extreme hardship exemption due to quality

improvementActivitiesCollapse allboolean
True if extreme hardship exemption due to improvement activities

aciCollapse allboolean
True if extreme hardship exemption due to aci

costCollapse allboolean
True if extreme hardship exemption due to cost

extremeHardshipSourcesCollapse allarray<string>
ItemsCollapse allstring
Extreme hardship reporting source

Allowed values"auto-fema""manual""auto-covid"
hasHospitalVbpCCNCollapse allboolean
True if TIN-NPI has a Hospital Value-Based CCN

hasPaymentAdjustmentCCNCollapse allboolean
True if TIN-NPI has a Payment Adjustment CCN

hospitalBasedClinicianCollapse allboolean
True if clinician met the threshold of hospital-based expenditures

Examplefalse
hospitalVbpNameCollapse allstring
Facility name within the Hospital Value-Based Purchasing Program

Example"Johnson Medical Center"
hospitalVbpScoreCollapse allnumberfloat
Hospital Value-Based Purchasing Program score

Example145.78
hpsaClinicianCollapse allboolean
True if clinician has at least one claim with an HPSA designation

Exampletrue
iaStudyCollapse allboolean
True if Improvement Activities Study data is present

Examplefalse
isEligibleCollapse allobject
individualCollapse allboolean
Examplefalse
groupCollapse allboolean
Examplefalse
mipsApmCollapse allboolean
Examplefalse
virtualGroupCollapse allboolean
Examplefalse
isFacilityBasedCollapse allboolean
True if the threshold of facility based encounters is met

isOptedInCollapse allboolean
Whether the entity has opted in or opted out. Will be null if no decision has been made.

Exampletrue
isOptInEligibleCollapse allboolean
Whether the entity is eligible to opt in.

Exampletrue
lowVolumeServicesCollapse allinteger
Number of claim lines counted toward low volume service threshold

Example23
lowVolumeStatusReasonsCollapse allarray<object>
ItemsCollapse allobject
lowVolStusRsnCdCollapse allstring
If lowVolumeSwitch is true, this array will contain the reasons for the status. Possible values-

"BENE" Clinician’s number of unique beneficiaries fell below the low volume threshold
"CHRG" Clinician’s Part B expenditures fell below the low volume threshold
"SRVC" Clinician’s low volume services fell below the low volume threshold
"BOTH" Both the clinician’s number of unique beneficiaries and Part B expenditures fell below the low volume threshold
"BENE/SRVC" Both the clinician’s number of unique beneficiaries and low volume services fell below the low volume threshold
"CHRG/SRVC" Both the clinician’s Part B expenditures and low volume services fell below the low volume threshold
"ALL" Clinician’s number of unique beneficiaries, Part B expenditures, and low volume services fell below the low volume threshold
"" lowVolumeSwitch is false
Allowed values"BENE""CHRG""SRVC""BOTH""BENE/SRVC""CHRG/SRVC""ALL"""
Example"BOTH"
lowVolStusRsnDescCollapse allstring
Description of lowVolStusRsnCd

Example"Both the unique beneficiaries and Part B"
lowVolumeSwitchCollapse allboolean
Fell below the low volume threshold

mipsEligibleSwitchCollapse allboolean
Clinician is a provider type that is eligible for Merit-Based Payment Incentive System (MIPS)

Examplefalse
nonPatientFacingCollapse allboolean
True if patient-facing encounters met the encounter threshold

Exampletrue
optInDecisionDateCollapse allstringdate-time
The date of the opt-in decision.

Example"2019-09-13T00:00:00.000Z"
ruralClinicianCollapse allboolean
True if clinician has at least one claim with a zip code designated as rural

Examplefalse
smallGroupPractitionerCollapse allboolean
True if 15 or fewer clinicians bill under the group

Examplefalse
specialtyCollapse allobject
specialtyDescriptionCollapse allstring
Example"Psychiatry"
categoryReferenceCollapse allstring
Example"Physicians"
typeDescriptionCollapse allstring
Example"Doctor of Medicine"
Additional propertiesforbidden
specialtyCodeCollapse allstring
A 2-character specialty code for a clinician's occupation

Example"72"
Additional propertiesforbidden
groupScenarioCollapse allobject
aciHardshipCollapse allboolean
True if there is an approved ACI Hardship Exemption application

aciReweightingCollapse allboolean
True if the group meets the conditions necessary for ACI Reweighting

aggregationLevelCollapse allinteger
Allowed values12
Example1
ambulatorySurgicalCenterCollapse allboolean
True if clinician met the threshold for being designated as an Ambulatory Surgical Center (ASC). ASCs provide surgery without an overnight hospital stay.

Examplefalse
extremeHardshipCollapse allboolean
True if Extreme and Uncontrollable Circumstance Exemption credit has been received

extremeHardshipEventTypeCollapse allstring
Type of extreme hardship event

Example"Natural Disaster"
extremeHardshipReasonsCollapse allobject
qualityCollapse allboolean
True if extreme hardship exemption due to quality

improvementActivitiesCollapse allboolean
True if extreme hardship exemption due to improvement activities

aciCollapse allboolean
True if extreme hardship exemption due to aci

costCollapse allboolean
True if extreme hardship exemption due to cost

extremeHardshipSourcesCollapse allarray<string>
ItemsCollapse allstring
Extreme hardship reporting source

Allowed values"auto-fema""manual""auto-covid"
hospitalBasedClinicianCollapse allboolean
True if clinician met the threshold of hospital-based expenditures

Examplefalse
hpsaClinicianCollapse allboolean
True if clinician has at least one claim with an HPSA designation

Exampletrue
iaStudyCollapse allboolean
True if Improvement Activities Study data is present

Examplefalse
isEligibleCollapse allobject
groupCollapse all(boolean | string)
One ofCollapse all(boolean | string)
#0boolean
#1string
Examplefalse
isFacilityBasedCollapse allboolean
True if the threshold of facility based encounters is met

isOptedInCollapse allboolean
Whether the entity has opted in or opted out. Will be null if no decision has been made.

Exampletrue
isOptInEligibleCollapse allboolean
Whether the entity is eligible to opt in.

Exampletrue
lowVolumeServicesCollapse allinteger
Number of claim lines counted toward low volume service threshold

Example23
lowVolumeStatusReasonsCollapse allarray<object>
ItemsCollapse allobject
lowVolStusRsnCdCollapse allstring
If lowVolumeSwitch is true, this array will contain the reasons for the status. Possible values-

"BENE" Clinician’s number of unique beneficiaries fell below the low volume threshold
"CHRG" Clinician’s Part B expenditures fell below the low volume threshold
"SRVC" Clinician’s low volume services fell below the low volume threshold
"BOTH" Both the clinician’s number of unique beneficiaries and Part B expenditures fell below the low volume threshold
"BENE/SRVC" Both the clinician’s number of unique beneficiaries and low volume services fell below the low volume threshold
"CHRG/SRVC" Both the clinician’s Part B expenditures and low volume services fell below the low volume threshold
"ALL" Clinician’s number of unique beneficiaries, Part B expenditures, and low volume services fell below the low volume threshold
"" lowVolumeSwitch is false
Allowed values"BENE""CHRG""SRVC""BOTH""BENE/SRVC""CHRG/SRVC""ALL"""
Example"BOTH"
lowVolStusRsnDescCollapse allstring
Description of lowVolStusRsnCd

Example"Both the unique beneficiaries and Part B"
lowVolumeSwitchCollapse allboolean
Fell below the low volume threshold

mipsEligibleSwitchCollapse allboolean
Clinician is a provider type that is eligible for Merit-Based Payment Incentive System (MIPS)

Examplefalse
nonPatientFacingCollapse allboolean
True if patient-facing encounters met the encounter threshold

Exampletrue
optInDecisionDateCollapse allstringdate-time
The date of the opt-in decision.

Example"2019-09-13T00:00:00.000Z"
ruralClinicianCollapse allboolean
True if clinician has at least one claim with a zip code designated as rural

Examplefalse
smallGroupPractitionerCollapse allboolean
True if 15 or fewer clinicians bill under the group

Examplefalse
Additional propertiesforbidden
apmsCollapse allarray<object>
ItemsCollapse allobject
entityNameCollapse allstring
Official name of the Organization

Example"Woodlawn Accountable Care Organization, LLC"
lvtFlagCollapse allboolean
Indicates if the APM Entity is below the low volume threshold

Examplefalse
lvtPaymentsCollapse allnumber
Total aggregated expenditures of the APM Entity

Example16384865.97
lvtPatientsCollapse allinteger
Total number of unique patients of the APM Entity

Example147241
lvtSmallStatusCollapse allboolean
Whether the APM Entity has Small Practice status

Exampletrue
lvtPerformanceYearCollapse allinteger
The relevant year for the APM dataset

Example2017
apmIdCollapse allstring
Unique combination of characters, numbers or symbols that are assigned by CMS Model operations to support establishing the identity of an APM Program

Example"08"
apmNameCollapse allstring
Formal label by which the APM Program is identified

Example"Medicare Shared Savings Program Accountable Care\nOrganizations\n"
subdivisionIdCollapse allstring
Identifier for a specific grouping within the APM Program for QPP purposes

Example"01"
subdivisionNameCollapse allstring
Identification label for the QPP Subdivision

Example"MSSP ACO - Track 1"
advancedApmFlagCollapse allboolean
APMs that require MIPS comparable measures, use of CEHRT, and more than nominal downside risk. Eligible clinicians that participate in Advanced APMs are able to become QPs and receive a 5% bonus and be exempt from MIPS.

Examplefalse
mipsApmFlagCollapse allboolean
APMs that already assess participants on cost and quality under the terms of the APM.

Exampletrue
providerRelationshipCodeCollapse allstring
Identifier of the APM Program Provider Relationship Type

Example"P"
qpPatientScoresCollapse allobject
aeCollapse allnumber
Example1234
aiCollapse allnumber
Example1234
atCollapse allnumber
Example1234
meCollapse allnumber
Example1234
miCollapse allnumber
Example1234
Additional propertiesforbidden
qpPaymentScoresCollapse allobject
aeCollapse allnumber
Example1234
aiCollapse allnumber
Example1234
atCollapse allnumber
Example1234
meCollapse allnumber
Example1234
miCollapse allnumber
Example1234
Additional propertiesforbidden
complexPatientScoreCollapse allnumberfloat
Composite Complex-Patient Score calculated by a combination of the dual eligibility ratio and the Hierarchical Conditions Category (HCC) risk score; max 5.00, min 0.00. The value of this field will be null when the requestor is not authorized to view data for the associated practice/TIN.

Example3.29
finalQpcScoreCollapse allnumber
Example999.9
extremeHardshipCollapse allboolean
True if Extreme and Uncontrollable Circumstance Exemption credit has been received

extremeHardshipReasonsCollapse allobject
qualityCollapse allboolean
True if extreme hardship exemption due to quality

improvementActivitiesCollapse allboolean
True if extreme hardship exemption due to improvement activities

aciCollapse allboolean
True if extreme hardship exemption due to aci

costCollapse allboolean
True if extreme hardship exemption due to cost

extremeHardshipEventTypeCollapse allstring
Type of extreme hardship event

Example"Natural Disaster"
extremeHardshipSourcesCollapse allarray<string>
ItemsCollapse allstring
Extreme hardship reporting source

Allowed values"auto-fema""manual""auto-covid"
isOptedInCollapse allboolean
Whether the entity has opted in or opted out. Will be null if no decision has been made.

Exampletrue
Additional propertiesforbidden
virtualGroupsCollapse allarray<object>
ItemsCollapse allobject
virtualGroupIdentifierCollapse allstring
Masked Virtual Group identifier.

Example"XXXXXX"
claimsTypesCollapse allstring
Type of claims made by this Virtual Group.

Example"CAH2"
lowVolumeSwitchCollapse allboolean
Fell below the low volume threshold

lowVolumeStatusReasonsCollapse allarray<object>
ItemsCollapse allobject
lowVolStusRsnCdCollapse allstring
If lowVolumeSwitch is true, this array will contain the reasons for the status. Possible values-

"BENE" Clinician’s number of unique beneficiaries fell below the low volume threshold
"CHRG" Clinician’s Part B expenditures fell below the low volume threshold
"SRVC" Clinician’s low volume services fell below the low volume threshold
"BOTH" Both the clinician’s number of unique beneficiaries and Part B expenditures fell below the low volume threshold
"BENE/SRVC" Both the clinician’s number of unique beneficiaries and low volume services fell below the low volume threshold
"CHRG/SRVC" Both the clinician’s Part B expenditures and low volume services fell below the low volume threshold
"ALL" Clinician’s number of unique beneficiaries, Part B expenditures, and low volume services fell below the low volume threshold
"" lowVolumeSwitch is false
Allowed values"BENE""CHRG""SRVC""BOTH""BENE/SRVC""CHRG/SRVC""ALL"""
Example"BOTH"
lowVolStusRsnDescCollapse allstring
Description of lowVolStusRsnCd

Example"Both the unique beneficiaries and Part B"
beneficiaryCountCollapse allinteger
Number of patients used to determine low volume threshold status

Example5
allowedChargesCollapse allnumberfloat
Billing amount used to determine low volume threshold status

Example91.25
hospitalVbpNameCollapse allstring
Facility name within the Hospital Value-Based Purchasing Program

Example"Johnson Medical Center"
isFacilityBasedCollapse allboolean
True if the threshold of facility based encounters is met

hospitalVbpScoreCollapse allnumberfloat
Hospital Value-Based Purchasing Program score

Example145.78
specialScenarioCollapse allobject
aciReweightingCollapse allboolean
True if the group meets the conditions necessary for ACI Reweighting

nonPatientFacingCollapse allboolean
True if patient-facing encounters met the encounter threshold

Exampletrue
ruralClinicianCollapse allboolean
True if clinician has at least one claim with a zip code designated as rural

Examplefalse
hpsaClinicianCollapse allboolean
True if clinician has at least one claim with an HPSA designation

Exampletrue
hospitalBasedClinicianCollapse allboolean
True if clinician met the threshold of hospital-based expenditures

Examplefalse
ambulatorySurgicalCenterCollapse allboolean
True if clinician met the threshold for being designated as an Ambulatory Surgical Center (ASC). ASCs provide surgery without an overnight hospital stay.

Examplefalse
aciHardshipCollapse allboolean
True if there is an approved ACI Hardship Exemption application

iaStudyCollapse allboolean
True if Improvement Activities Study data is present

Examplefalse
smallGroupPractitionerCollapse allboolean
True if 15 or fewer clinicians bill under the group

Examplefalse
extremeHardshipCollapse allboolean
True if Extreme and Uncontrollable Circumstance Exemption credit has been received

extremeHardshipReasonsCollapse allobject
qualityCollapse allboolean
True if extreme hardship exemption due to quality

improvementActivitiesCollapse allboolean
True if extreme hardship exemption due to improvement activities

aciCollapse allboolean
True if extreme hardship exemption due to aci

costCollapse allboolean
True if extreme hardship exemption due to cost

extremeHardshipEventTypeCollapse allstring
Type of extreme hardship event

Example"Natural Disaster"
extremeHardshipSourcesCollapse allarray<string>
ItemsCollapse allstring
Extreme hardship reporting source

Allowed values"auto-fema""manual""auto-covid"
Additional propertiesforbidden
Additional propertiesforbidden
Additional propertiesforbidden
specialtyCollapse alldeprecatedobject
This field will be deprecated in v7. Use the specialty object in organizations[].individualScenario instead.

specialtyDescriptionCollapse allstring
Example"Psychiatry"
categoryReferenceCollapse allstring
Example"Physicians"
typeDescriptionCollapse allstring
Example"Doctor of Medicine"
Additional propertiesforbidden
Additional propertiesforbidden