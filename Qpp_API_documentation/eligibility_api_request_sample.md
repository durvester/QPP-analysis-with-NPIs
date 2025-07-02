Unauthenticated

baseUrl: https://qpp.cms.gov


GET
{{baseUrl}}/api/eligibility/npi/{npi}

Look up public information for a single provider by NPI.

Parameters
Name	Description
npi *
string
(path)
National Provider Identifier (NPI) is a unique 10-digit identification number issued to health care providers by CMS.

npi
year
string
(query)
Request content by performance year, i.e. year=2023. If not specified, the current default year will be used.

The default year is viewable under key defaultYear in the version endpoint.

Example : 2023

2023
runNum
string
(query)
To request content by the load sequence of the year. Data is loaded into the database multiple times a year. To request the 2nd load of data, set 'runNum' to 2, i.e. runNum=2. If not requested, the default will be the latest run for the given year.

The latest run for each year is viewable under keys special_scenario_latest_run_{YEAR} in the environment endpoint.

Available values : 1, 2, 3, 4

Example : 2


2
Accept
string
(header)
Request a content type and a specific API version. For example, to request application/json and version 6 of the API, the header value should be application/vnd.qpp.cms.gov.v6+json. The API will return the default version if the Accept header is not included or if the requested version is not supported.

Available values : application/vnd.qpp.cms.gov.v4+json, application/vnd.qpp.cms.gov.v5+json, application/vnd.qpp.cms.gov.v6+json

Default value : application/vnd.qpp.cms.gov.v6+json


application/vnd.qpp.cms.gov.v6+json
