#!/usr/bin/env python3
"""
EPA Drinking Water Compliance Analysis
Springfield Municipal Water District - January 15, 2025
Coordinated by EPA Compliance Orchestrator Agent
"""

import pandas as pd
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

class EPAComplianceAnalyzer:
    def __init__(self):
        # EPA Regulatory Standards (CFR Title 40)
        self.mcls = {
            'E.coli': 0,  # Zero tolerance
            'Lead': 15,   # Action Level (ppb)
            'Copper': 1300,  # Action Level (ppb)
            'PFOA': 4     # Maximum Contaminant Level (ng/L)
        }
        
        self.violation_tiers = {
            'E.coli': 'Tier 1',
            'Lead': 'Tier 2', 
            'Copper': 'Tier 2',
            'PFOA': 'Tier 2'
        }
        
        self.notification_requirements = {
            'Tier 1': {'timeframe': '24 hours', 'media': ['Public Notice', 'Direct Contact', 'Media Alert']},
            'Tier 2': {'timeframe': '30 days', 'media': ['Public Notice', 'Newspaper']},
            'Tier 3': {'timeframe': '1 year', 'media': ['Annual Report']}
        }
        
        # EPA API configuration
        self.epa_api_base = 'https://data.epa.gov/efservice'
        self.api_timeout = 15

    def fetch_water_system_info(self, pwsid: str) -> Optional[Dict[str, Any]]:
        """Fetch real water system information from EPA ECHO API."""
        print(f"🔍 Fetching water system information for PWSID: {pwsid}")
        
        # EPA API endpoint for water system data
        url = f"{self.epa_api_base}/sdwis.water_system/pwsid/equals/{pwsid}/json"
        
        try:
            response = requests.get(url, timeout=self.api_timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and isinstance(data, list) and len(data) > 0:
                    raw_system_data = data[0]
                    
                    # Debug: Show available fields in EPA response
                    print(f"EPA API returned {len(data)} record(s)")
                    print(f"Available fields: {list(raw_system_data.keys())[:15]}")
                    
                    # Parse EPA response fields using exact field names from debug output
                    system_info = {
                        'pwsid': raw_system_data.get('pwsid', raw_system_data.get('PWSID', pwsid)),
                        'system_name': raw_system_data.get('pws_name', raw_system_data.get('PWS_NAME', 'Unknown')),
                        'population_served': raw_system_data.get('population_served_count', raw_system_data.get('POPULATION_SERVED_COUNT', 0)),
                        'system_type': raw_system_data.get('pws_type_code', raw_system_data.get('PWS_TYPE_CODE', 'Unknown')),
                        'activity_status': raw_system_data.get('pws_activity_code', raw_system_data.get('PWS_ACTIVITY_CODE', 'Unknown')),
                        'state_code': raw_system_data.get('state_code', raw_system_data.get('STATE_CODE', 'Unknown')),
                        'city_name': raw_system_data.get('city_name', raw_system_data.get('CITY_NAME', 'Unknown')),
                        'county_name': raw_system_data.get('county_name', raw_system_data.get('COUNTY_NAME', 'Unknown')),
                        'owner_type': raw_system_data.get('owner_type_code', raw_system_data.get('OWNER_TYPE_CODE', 'Unknown')),
                        'data_source': 'EPA_API',
                        'api_response_time': response.elapsed.total_seconds()
                    }
                    
                    # Convert population to integer if possible
                    try:
                        if system_info['population_served']:
                            system_info['population_served'] = int(system_info['population_served'])
                    except (ValueError, TypeError):
                        system_info['population_served'] = 0
                    
                    print(f"✓ Found system: {system_info['system_name']}")
                    print(f"  Population: {system_info['population_served']:,}")
                    print(f"  System Type: {system_info['system_type']}")
                    print(f"  Location: {system_info['city_name']}, {system_info['county_name']} County")
                    print(f"  Status: {system_info['activity_status']}")
                    
                    # Debug: Show key field extraction
                    print(f"Debug - Field extraction:")
                    print(f"  Raw pws_name: {raw_system_data.get('pws_name', 'NOT_FOUND')}")
                    print(f"  Raw PWS_NAME: {raw_system_data.get('PWS_NAME', 'NOT_FOUND')}")
                    print(f"  Raw population_served_count: {raw_system_data.get('population_served_count', 'NOT_FOUND')}")
                    print(f"  Final system_name: {system_info['system_name']}")
                    
                    return system_info
                
                else:
                    print(f"⚪ No data found in EPA database for PWSID {pwsid}")
                    
            else:
                print(f"⚠ EPA API returned status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠ EPA API request timed out after {self.api_timeout}s")
        except Exception as e:
            print(f"⚠ EPA API error: {e}")
        
        # Return fallback data for Clinton Machine PWS if API fails
        print("Using fallback data for compliance analysis")
        return {
            'pwsid': pwsid,
            'system_name': 'Clinton Machine PWS',
            'population_served': 250,  # Typical small system
            'system_type': 'NCWS',     # Non-Community Water System
            'activity_status': 'A',    # Active
            'state_code': 'OH',
            'city_name': 'Unknown',
            'county_name': 'Unknown',
            'owner_type': 'P',         # Private
            'data_source': 'FALLBACK',
            'api_response_time': 0
        }

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load laboratory results data with validation."""
        try:
            df = pd.read_csv(file_path)
            print(f"✓ Data loaded successfully: {len(df)} records")
            return df
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return pd.DataFrame()

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data against EPA quality standards."""
        validation_results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'quality_score': 100
        }
        
        # Required columns check
        required_cols = ['PWSID', 'Sample_Date', 'Parameter', 'Result', 'Units', 'MCL', 'Lab_Cert_Number']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            validation_results['issues'].append(f"Missing required columns: {missing_cols}")
            validation_results['valid'] = False
        
        # PWSID format validation
        pwsid_pattern = r'^[A-Z]{2}\d{7}$'
        invalid_pwsids = df[~df['PWSID'].str.match(pwsid_pattern, na=False)]
        if not invalid_pwsids.empty:
            validation_results['issues'].append(f"Invalid PWSID format: {invalid_pwsids['PWSID'].unique()}")
        
        # Lab certification check
        if df['Lab_Cert_Number'].isna().any():
            validation_results['warnings'].append("Missing laboratory certification numbers")
            validation_results['quality_score'] -= 10
        
        # Sample collection time validation
        if df['Collection_Time'].isna().any():
            validation_results['warnings'].append("Missing collection times")
            validation_results['quality_score'] -= 5
        
        print(f"✓ Data Quality Validation Complete - Score: {validation_results['quality_score']}/100")
        return validation_results

    def detect_violations(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Detect violations against EPA standards."""
        violations = {}
        
        for parameter in df['Parameter'].unique():
            param_data = df[df['Parameter'] == parameter]
            mcl = self.mcls.get(parameter)
            
            if mcl is None:
                continue
                
            param_violations = []
            
            for _, row in param_data.iterrows():
                if parameter == 'E.coli':
                    if row['Result'] == 'Present':
                        param_violations.append({
                            'sample_location': row['Sample_Location'],
                            'result': row['Result'],
                            'mcl': mcl,
                            'exceedance_factor': 'ACUTE',
                            'collection_time': row['Collection_Time'],
                            'tier': self.violation_tiers[parameter]
                        })
                else:
                    try:
                        result_value = float(row['Result'])
                        if result_value > mcl:
                            param_violations.append({
                                'sample_location': row['Sample_Location'],
                                'result': result_value,
                                'mcl': mcl,
                                'exceedance_factor': round(result_value / mcl, 2),
                                'collection_time': row['Collection_Time'],
                                'tier': self.violation_tiers[parameter]
                            })
                    except ValueError:
                        continue
            
            if param_violations:
                violations[parameter] = param_violations
        
        return violations

    def assess_severity(self, violations: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Assess severity of violations for response prioritization."""
        severity_assessment = {}
        
        for parameter, violation_list in violations.items():
            if parameter == 'E.coli':
                severity_assessment[parameter] = "CRITICAL - Immediate public health risk"
            elif parameter == 'Lead':
                max_exceedance = max([v['exceedance_factor'] for v in violation_list])
                if max_exceedance > 2.0:
                    severity_assessment[parameter] = "HIGH - Significant health risk"
                else:
                    severity_assessment[parameter] = "MODERATE - Health concern"
            elif parameter == 'Copper':
                max_exceedance = max([v['exceedance_factor'] for v in violation_list])
                if max_exceedance > 1.5:
                    severity_assessment[parameter] = "HIGH - Corrosion control failure"
                else:
                    severity_assessment[parameter] = "MODERATE - Corrosion monitoring required"
            elif parameter == 'PFOA':
                max_exceedance = max([v['exceedance_factor'] for v in violation_list])
                if max_exceedance > 2.0:
                    severity_assessment[parameter] = "HIGH - Persistent contamination"
                else:
                    severity_assessment[parameter] = "MODERATE - Monitoring required"
        
        return severity_assessment

    def generate_public_notifications(self, violations: Dict[str, List[Dict]], severity: Dict[str, str], water_system_info: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate required public notifications based on violation tiers."""
        notifications = {}
        
        # Use real water system information if available
        if water_system_info:
            system_header = f"{water_system_info['system_name']} (PWSID: {water_system_info['pwsid']})"
        else:
            system_header = "{system_header}"
        
        for parameter, violation_list in violations.items():
            tier = violation_list[0]['tier']
            notification_req = self.notification_requirements[tier]
            
            if parameter == 'E.coli':
                notifications[parameter] = f"""
IMMEDIATE PUBLIC NOTICE - TIER 1 VIOLATION
{system_header}

URGENT: DO NOT DRINK THE WATER WITHOUT BOILING IT FIRST

E.coli bacteria have been found in your drinking water. This is an acute violation requiring immediate action.

IMMEDIATE ACTIONS REQUIRED:
- Boil all water for drinking, cooking, and brushing teeth for at least 1 minute
- Use bottled water if available
- Seek medical attention if you experience illness

The water system is taking corrective action and will notify you when the water is safe to drink.

Notification Requirements: {notification_req['timeframe']} via {', '.join(notification_req['media'])}
Severity: {severity[parameter]}
Date of Violation: January 15, 2025
                """
            
            elif parameter == 'Lead':
                max_result = max([v['result'] for v in violation_list])
                notifications[parameter] = f"""
PUBLIC NOTICE - TIER 2 VIOLATION
{system_header}

Lead levels in your drinking water exceed the EPA action level.

VIOLATION DETAILS:
- Maximum Lead Level: {max_result} ppb
- EPA Action Level: 15 ppb
- Number of Exceedances: {len(violation_list)}

HEALTH EFFECTS:
Lead can cause serious health problems, especially for pregnant women and young children. Lead in drinking water is primarily from materials and components associated with service lines and home plumbing.

ACTIONS BEING TAKEN:
- Corrosion control treatment optimization
- Additional monitoring and testing
- Public education campaign

Notification Requirements: {notification_req['timeframe']} via {', '.join(notification_req['media'])}
Severity: {severity[parameter]}
                """
            
            elif parameter == 'Copper':
                max_result = max([v['result'] for v in violation_list])
                notifications[parameter] = f"""
PUBLIC NOTICE - TIER 2 VIOLATION
{system_header}

Copper levels in your drinking water exceed the EPA action level.

VIOLATION DETAILS:
- Maximum Copper Level: {max_result} ppb
- EPA Action Level: 1300 ppb
- Number of Exceedances: {len(violation_list)}

HEALTH EFFECTS:
Copper is an essential nutrient, but some people who drink water containing copper in excess of the action level over a relatively short period could experience gastrointestinal distress.

ACTIONS BEING TAKEN:
- Corrosion control treatment adjustment
- pH optimization
- Additional monitoring

Notification Requirements: {notification_req['timeframe']} via {', '.join(notification_req['media'])}
Severity: {severity[parameter]}
                """
            
            elif parameter == 'PFOA':
                max_result = max([v['result'] for v in violation_list])
                notifications[parameter] = f"""
PUBLIC NOTICE - TIER 2 VIOLATION
{system_header}

PFOA levels in your drinking water exceed the EPA maximum contaminant level.

VIOLATION DETAILS:
- PFOA Level: {max_result} ng/L
- EPA MCL: 4 ng/L
- Exceedance Factor: {max_result/4:.1f}x

HEALTH EFFECTS:
PFOA is a synthetic chemical that has been used in industry and consumer products. Some people who drink water containing PFOA in excess of the MCL over many years may experience certain health effects.

ACTIONS BEING TAKEN:
- Enhanced treatment system implementation
- Source water investigation
- Alternative water supply evaluation

Notification Requirements: {notification_req['timeframe']} via {', '.join(notification_req['media'])}
Severity: {severity[parameter]}
                """
        
        return notifications

    def generate_federal_reporting(self, violations: Dict[str, List[Dict]], severity: Dict[str, str], water_system_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate required federal reporting documents."""
        
        # Use real water system information if available
        if water_system_info:
            system_name = water_system_info['system_name']
            pwsid = water_system_info['pwsid']
            population_served = water_system_info['population_served']
            system_type = water_system_info['system_type']
            location = f"{water_system_info['city_name']}, {water_system_info['county_name']} County, {water_system_info['state_code']}"
        else:
            system_name = 'Clinton Machine PWS'
            pwsid = 'OH7700001'
            population_served = 250
            system_type = 'NCWS'
            location = 'Unknown'
        
        federal_report = {
            'report_type': 'Drinking Water Violation Report',
            'pwsid': pwsid,
            'water_system_name': system_name,
            'population_served': population_served,
            'system_type': system_type,
            'location': location,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'violation_date': '2025-01-15',
            'violations': [],
            'immediate_actions_required': [],
            'long_term_actions': [],
            'system_data_source': water_system_info['data_source'] if water_system_info else 'FALLBACK'
        }
        
        for parameter, violation_list in violations.items():
            for violation in violation_list:
                federal_report['violations'].append({
                    'parameter': parameter,
                    'violation_type': 'MCL/AL Exceedance',
                    'tier': violation['tier'],
                    'sample_location': violation['sample_location'],
                    'result': violation['result'],
                    'mcl_al': violation['mcl'],
                    'exceedance_factor': violation['exceedance_factor'],
                    'severity': severity[parameter]
                })
        
        # Immediate Actions Required
        if 'E.coli' in violations:
            federal_report['immediate_actions_required'].extend([
                'Issue boil water advisory within 24 hours',
                'Collect repeat samples within 24 hours',
                'Notify state regulatory agency immediately',
                'Implement emergency disinfection protocols'
            ])
        
        if 'Lead' in violations or 'Copper' in violations:
            federal_report['immediate_actions_required'].extend([
                'Optimize corrosion control treatment',
                'Conduct follow-up monitoring',
                'Public notification within 30 days'
            ])
        
        if 'PFOA' in violations:
            federal_report['immediate_actions_required'].extend([
                'Evaluate treatment options',
                'Investigate contamination sources',
                'Public notification within 30 days'
            ])
        
        # Long-term Actions
        federal_report['long_term_actions'] = [
            'Submit corrective action plan within 30 days',
            'Implement enhanced monitoring program',
            'Conduct system-wide evaluation',
            'Submit quarterly compliance reports',
            'Maintain public notification requirements'
        ]
        
        return federal_report

def main():
    """Main compliance analysis workflow."""
    analyzer = EPAComplianceAnalyzer()
    
    print("=== EPA DRINKING WATER COMPLIANCE ANALYSIS ===")
    print("Analysis Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Load data
    df = analyzer.load_data('/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo/demo/springfield_lab_results.csv')
    if df.empty:
        return
    
    # Fetch real water system information from EPA API
    print("=== WATER SYSTEM VERIFICATION ===")
    pwsid = df['PWSID'].iloc[0] if not df.empty else 'OH7700001'
    water_system_info = analyzer.fetch_water_system_info(pwsid)
    
    if water_system_info:
        print(f"System Name: {water_system_info['system_name']}")
        print(f"PWSID: {water_system_info['pwsid']}")
        print(f"Population Served: {water_system_info['population_served']:,}")
        print(f"System Type: {water_system_info['system_type']}")
        print(f"Location: {water_system_info['city_name']}, {water_system_info['county_name']} County, {water_system_info['state_code']}")
        print(f"Data Source: {water_system_info['data_source']}")
    else:
        print("⚠ Could not fetch water system information")
    
    # Data validation
    print("\n=== DATA VALIDATION ===")
    validation_results = analyzer.validate_data_quality(df)
    if validation_results['issues']:
        print("CRITICAL ISSUES:")
        for issue in validation_results['issues']:
            print(f"  ✗ {issue}")
    if validation_results['warnings']:
        print("WARNINGS:")
        for warning in validation_results['warnings']:
            print(f"  ⚠ {warning}")
    
    # Violation detection
    print("\n=== VIOLATION DETECTION ===")
    violations = analyzer.detect_violations(df)
    print(f"Parameters with violations: {list(violations.keys())}")
    
    for parameter, violation_list in violations.items():
        print(f"\n{parameter}: {len(violation_list)} violation(s)")
        for i, violation in enumerate(violation_list, 1):
            print(f"  {i}. Location: {violation['sample_location']}")
            print(f"     Result: {violation['result']}")
            print(f"     MCL/AL: {violation['mcl']}")
            print(f"     Exceedance: {violation['exceedance_factor']}")
    
    # Severity assessment
    print("\n=== SEVERITY ASSESSMENT ===")
    severity = analyzer.assess_severity(violations)
    for parameter, assessment in severity.items():
        print(f"{parameter}: {assessment}")
    
    # Generate notifications
    print("\n=== PUBLIC NOTIFICATIONS ===")
    notifications = analyzer.generate_public_notifications(violations, severity, water_system_info)
    
    # Generate federal reporting
    print("\n=== FEDERAL REPORTING ===")
    federal_report = analyzer.generate_federal_reporting(violations, severity, water_system_info)
    
    # Save results
    with open('/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo/compliance_report.json', 'w') as f:
        json.dump({
            'water_system_info': water_system_info,
            'validation_results': validation_results,
            'violations': violations,
            'severity_assessment': severity,
            'federal_report': federal_report
        }, f, indent=2, default=str)
    
    with open('/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo/public_notifications.json', 'w') as f:
        json.dump(notifications, f, indent=2)
    
    print("✓ Analysis complete. Results saved to compliance_report.json and public_notifications.json")
    
    return violations, severity, notifications, federal_report

if __name__ == "__main__":
    main()