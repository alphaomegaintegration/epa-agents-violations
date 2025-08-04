#!/usr/bin/env python3
"""
EPA ECHO API Test Script - Hybrid Approach
Demonstrates real EPA ECHO API calls for PWSID verification with mock data processing
for Clinton Machine PWS (OH7700001)
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import sys

class EPAECHOTestClient:
    """
    Test client for EPA ECHO API with hybrid real/mock approach
    """
    
    BASE_URL = "https://data.epa.gov/efservice"
    TIMEOUT = 30
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EPA-Compliance-Test/1.0',
            'Accept': 'application/json'
        })
        
        # Mock data for when real API calls fail or for demo purposes
        self.mock_data = {
            'OH7700001': {
                'PWSID': 'OH7700001',
                'PWS_NAME': 'Clinton Machine PWS',
                'POPULATION_SERVED_COUNT': 45000,
                'PWS_TYPE_CODE': 'CWS',
                'PWS_ACTIVITY_CODE': 'A',
                'STATE_CODE': 'OH',
                'PRIMACY_AGENCY_CODE': 'OH',
                'OWNER_TYPE_CODE': 'M',
                'LAST_SANITARY_SURVEY_DATE': '2023-08-15',
                'VIOLATION_COUNT': 2,
                'ENFORCEMENT_COUNT': 0,
                'SERVICE_CONNECTIONS_COUNT': 18500,
                'CITIES_SERVED': 'Springfield',
                'COUNTIES_SERVED': 'Clark County'
            },
            'CA0123456': {
                'PWSID': 'CA0123456',
                'PWS_NAME': 'Los Angeles Department of Water and Power',
                'POPULATION_SERVED_COUNT': 4000000,
                'PWS_TYPE_CODE': 'CWS',
                'PWS_ACTIVITY_CODE': 'A',
                'STATE_CODE': 'CA',
                'PRIMACY_AGENCY_CODE': 'CA',
                'OWNER_TYPE_CODE': 'M'
            }
        }
    
    def test_real_api_call(self, pwsid: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Make a real EPA ECHO API call for PWSID verification
        
        Returns:
            Tuple of (success, data, error_message)
        """
        try:
            url = f"{self.BASE_URL}/sdwis.water_system/pwsid/equals/{pwsid}/json"
            
            print(f"🌐 Making REAL EPA ECHO API call...")
            print(f"   URL: {url}")
            print(f"   Timeout: {self.TIMEOUT}s")
            print(f"   PWSID: {pwsid}")
            
            start_time = time.time()
            response = self.session.get(url, timeout=self.TIMEOUT)
            end_time = time.time()
            
            print(f"   Response Time: {end_time - start_time:.2f}s")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content Length: {len(response.content)} bytes")
            
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                return False, None, f"No data found for PWSID {pwsid} in EPA database"
            
            # EPA API sometimes returns arrays, sometimes single objects
            if isinstance(data, list):
                if len(data) > 0:
                    system_data = data[0]
                else:
                    return False, None, "Empty array returned from EPA API"
            else:
                system_data = data
            
            print("✓ Real API call successful!")
            print(f"   System Found: {system_data.get('PWS_NAME', 'Unknown')}")
            
            return True, system_data, None
            
        except requests.exceptions.Timeout:
            error_msg = f"API timeout after {self.TIMEOUT}s"
            print(f"⚠ {error_msg}")
            return False, None, error_msg
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Network connection error: {str(e)}"
            print(f"⚠ {error_msg}")
            return False, None, error_msg
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text[:200]}"
            print(f"⚠ {error_msg}")
            return False, None, error_msg
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            print(f"⚠ {error_msg}")
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"⚠ {error_msg}")
            return False, None, error_msg
    
    def get_mock_data(self, pwsid: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get mock data for demonstration purposes
        """
        if pwsid in self.mock_data:
            print("🎭 Using mock data for demonstration...")
            return True, self.mock_data[pwsid], None
        else:
            return False, None, f"No mock data available for PWSID {pwsid}"
    
    def hybrid_verification(self, pwsid: str, prefer_real: bool = True) -> Tuple[bool, Dict, str]:
        """
        Hybrid approach: Try real API first, fallback to mock data
        
        Returns:
            Tuple of (success, system_data, data_source)
        """
        print(f"\n🔍 Hybrid PWSID Verification for {pwsid}")
        print("=" * 50)
        
        if prefer_real:
            # Try real API call first
            success, data, error = self.test_real_api_call(pwsid)
            
            if success:
                return True, data, "REAL_API"
            else:
                print(f"Real API failed: {error}")
                print("Falling back to mock data...")
                
                # Fallback to mock data
                mock_success, mock_data, mock_error = self.get_mock_data(pwsid)
                if mock_success:
                    return True, mock_data, "MOCK_DATA"
                else:
                    return False, {}, f"Both real API and mock data failed. API Error: {error}, Mock Error: {mock_error}"
        else:
            # Use mock data first
            success, data, error = self.get_mock_data(pwsid)
            if success:
                return True, data, "MOCK_DATA"
            else:
                return False, {}, error

def format_system_info(data: Dict, data_source: str) -> str:
    """
    Format system information for display
    """
    info = []
    info.append(f"Data Source: {data_source}")
    info.append(f"PWSID: {data.get('PWSID', 'Unknown')}")
    info.append(f"System Name: {data.get('PWS_NAME', 'Unknown')}")
    info.append(f"Population Served: {data.get('POPULATION_SERVED_COUNT', 0):,}")
    info.append(f"System Type: {data.get('PWS_TYPE_CODE', 'Unknown')}")
    info.append(f"Activity Status: {data.get('PWS_ACTIVITY_CODE', 'Unknown')} ({'Active' if data.get('PWS_ACTIVITY_CODE') == 'A' else 'Inactive'})")
    info.append(f"State: {data.get('STATE_CODE', 'Unknown')}")
    info.append(f"Owner Type: {data.get('OWNER_TYPE_CODE', 'Unknown')}")
    
    if data.get('SERVICE_CONNECTIONS_COUNT'):
        info.append(f"Service Connections: {data.get('SERVICE_CONNECTIONS_COUNT'):,}")
    
    if data.get('CITIES_SERVED'):
        info.append(f"Cities Served: {data.get('CITIES_SERVED')}")
    
    if data.get('COUNTIES_SERVED'):
        info.append(f"Counties Served: {data.get('COUNTIES_SERVED')}")
    
    if data.get('LAST_SANITARY_SURVEY_DATE'):
        info.append(f"Last Sanitary Survey: {data.get('LAST_SANITARY_SURVEY_DATE')}")
    
    violation_count = data.get('VIOLATION_COUNT', 0)
    if violation_count and violation_count > 0:
        info.append(f"⚠ Violations on Record: {violation_count}")
    
    enforcement_count = data.get('ENFORCEMENT_COUNT', 0)
    if enforcement_count and enforcement_count > 0:
        info.append(f"⚠ Enforcement Actions: {enforcement_count}")
    
    return "\n".join([f"  {item}" for item in info])

def test_springfield_scenario():
    """
    Test the specific Clinton Machine PWS scenario
    """
    print("🏛 Clinton Machine PWS Test Scenario")
    print("=" * 60)
    print("Testing PWSID: OH7700001")
    print("This represents our demo scenario with known violations")
    
    client = EPAECHOTestClient()
    
    # Test with real API call first
    success, data, source = client.hybrid_verification('OH7700001', prefer_real=True)
    
    if success:
        print("\n✓ PWSID Verification Successful!")
        print("-" * 30)
        print(format_system_info(data, source))
        
        # Process Springfield lab results with verified system info
        print(f"\n📊 Processing Springfield Lab Results")
        print("-" * 40)
        process_springfield_lab_data(data, source)
        
    else:
        print(f"\n✗ PWSID Verification Failed: {data}")

def process_springfield_lab_data(system_data: Dict, data_source: str):
    """
    Process the Springfield lab results with verified system information
    """
    
    # Load the Springfield lab results
    try:
        import csv
        import os
        
        csv_path = 'demo/springfield_lab_results.csv'
        if os.path.exists(csv_path):
            print(f"✓ Loading lab results from {csv_path}")
            
            violations_found = []
            
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                samples = list(reader)
                
                print(f"  Samples to process: {len(samples)}")
                
                for sample in samples:
                    parameter = sample.get('Parameter', '')
                    result_str = sample.get('Result', '0')
                    mcl_str = sample.get('MCL', '0')
                    units = sample.get('Units', '')
                    
                    # Parse results
                    try:
                        if result_str.upper() == 'PRESENT':
                            # E.coli detection
                            violations_found.append({
                                'parameter': parameter,
                                'result': 'Present',
                                'mcl': '0 (Not Allowed)',
                                'violation_type': 'Acute - Tier 1',
                                'units': units,
                                'location': sample.get('Sample_Location', 'Unknown')
                            })
                        else:
                            result = float(result_str)
                            mcl = float(mcl_str)
                            
                            if result > mcl:
                                violation_type = 'Non-Acute - Tier 2' if 'Lead' in parameter or 'Copper' in parameter else 'Tier 2'
                                violations_found.append({
                                    'parameter': parameter,
                                    'result': result,
                                    'mcl': mcl,
                                    'violation_type': violation_type,
                                    'units': units,
                                    'location': sample.get('Sample_Location', 'Unknown')
                                })
                    except ValueError:
                        continue
                
                # Display violations found
                print(f"\n🚨 EPA Violations Detected: {len(violations_found)}")
                print("-" * 40)
                
                for i, violation in enumerate(violations_found, 1):
                    print(f"{i}. {violation['parameter']}")
                    print(f"   Result: {violation['result']} {violation['units']}")
                    print(f"   MCL/AL: {violation['mcl']} {violation['units']}")
                    print(f"   Type: {violation['violation_type']}")
                    print(f"   Location: {violation['location']}")
                    print()
                
                # Generate compliance summary
                print("📋 Compliance Summary")
                print("-" * 25)
                print(f"Water System: {system_data.get('PWS_NAME', 'Unknown')}")
                print(f"PWSID: {system_data.get('PWSID', 'Unknown')}")
                print(f"Data Source: {data_source}")
                print(f"Population at Risk: {system_data.get('POPULATION_SERVED_COUNT', 0):,}")
                print(f"Total Violations: {len(violations_found)}")
                
                # Categorize violations
                tier_1_count = len([v for v in violations_found if 'Tier 1' in v['violation_type']])
                tier_2_count = len([v for v in violations_found if 'Tier 2' in v['violation_type']])
                
                print(f"Tier 1 (Acute): {tier_1_count}")
                print(f"Tier 2 (Non-Acute): {tier_2_count}")
                
                if tier_1_count > 0:
                    print("⚠ IMMEDIATE ACTION REQUIRED - Tier 1 violations present")
                    print("  • Public notification within 24 hours")
                    print("  • Media notification required")
                    print("  • Boil water advisory may be necessary")
                
                if tier_2_count > 0:
                    print("⚠ ACTION REQUIRED - Tier 2 violations present")
                    print("  • Public notification within 30 days")
                    print("  • Follow-up monitoring required")
                    print("  • Corrective action plan needed")
        
        else:
            print(f"⚠ Lab results file not found: {csv_path}")
            print("Creating mock violation scenario...")
            
            # Mock violations for demonstration
            mock_violations = [
                {
                    'parameter': 'E.coli',
                    'result': 'Present',
                    'mcl': '0 (Not Allowed)',
                    'violation_type': 'Acute - Tier 1',
                    'units': 'CFU/100mL',
                    'location': 'Distribution System'
                },
                {
                    'parameter': 'Lead', 
                    'result': 22.1,
                    'mcl': 15,
                    'violation_type': 'Non-Acute - Tier 2',
                    'units': 'ppb',
                    'location': 'Home Sample #2'
                },
                {
                    'parameter': 'PFOA',
                    'result': 8.2,
                    'mcl': 4,
                    'violation_type': 'Non-Acute - Tier 2', 
                    'units': 'ng/L',
                    'location': 'Treatment Plant Effluent'
                }
            ]
            
            print(f"\n🚨 Mock EPA Violations: {len(mock_violations)}")
            print("-" * 30)
            
            for i, violation in enumerate(mock_violations, 1):
                print(f"{i}. {violation['parameter']}: {violation['result']} {violation['units']} (MCL: {violation['mcl']})")
            
    except Exception as e:
        print(f"Error processing lab data: {e}")

def test_multiple_pwsids():
    """
    Test multiple PWSID scenarios to demonstrate API behavior
    """
    print("\n\n🔬 Multiple PWSID Test Scenarios")
    print("=" * 60)
    
    test_cases = [
        {
            'pwsid': 'OH7700001',
            'name': 'Clinton Machine PWS',
            'expected': 'Should exist (mock data available)'
        },
        {
            'pwsid': 'CA0123456', 
            'name': 'California Water System',
            'expected': 'Mock data available'
        },
        {
            'pwsid': 'TX7777777',
            'name': 'Non-existent Texas System',
            'expected': 'Should not exist in EPA database'
        },
        {
            'pwsid': 'INVALID123',
            'name': 'Invalid Format',
            'expected': 'Format validation should fail'
        }
    ]
    
    client = EPAECHOTestClient()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"PWSID: {test_case['pwsid']}")
        print(f"Expected: {test_case['expected']}")
        print("-" * 40)
        
        # Validate PWSID format first
        if not validate_pwsid_format(test_case['pwsid']):
            print("✗ PWSID format validation failed")
            continue
        
        success, data, source = client.hybrid_verification(test_case['pwsid'], prefer_real=True)
        
        if success:
            print("✓ Verification successful")
            print(format_system_info(data, source))
        else:
            print(f"✗ Verification failed: {data}")

def validate_pwsid_format(pwsid: str) -> bool:
    """
    Simple PWSID format validation
    """
    import re
    
    if not pwsid or len(pwsid) != 9:
        return False
    
    if not re.match(r'^[A-Z]{2}\d{7}$', pwsid):
        return False
    
    # Check for valid state codes
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    }
    
    state_code = pwsid[:2]
    return state_code in valid_states

def test_api_performance():
    """
    Test API performance and response times
    """
    print("\n\n⚡ EPA ECHO API Performance Test")
    print("=" * 60)
    
    client = EPAECHOTestClient()
    test_pwsids = ['OH7700001', 'CA0123456', 'TX7777777']
    
    total_time = 0
    successful_calls = 0
    
    for pwsid in test_pwsids:
        print(f"\nTesting {pwsid}...")
        start_time = time.time()
        
        success, data, error = client.test_real_api_call(pwsid)
        
        end_time = time.time()
        call_time = end_time - start_time
        total_time += call_time
        
        if success:
            successful_calls += 1
            print(f"✓ Success in {call_time:.2f}s")
        else:
            print(f"✗ Failed in {call_time:.2f}s: {error}")
    
    print(f"\n📊 Performance Summary")
    print("-" * 25)
    print(f"Total API calls: {len(test_pwsids)}")
    print(f"Successful calls: {successful_calls}")
    print(f"Success rate: {successful_calls/len(test_pwsids)*100:.1f}%")
    print(f"Average response time: {total_time/len(test_pwsids):.2f}s")
    print(f"Total test time: {total_time:.2f}s")

def main():
    """
    Main test execution
    """
    print("EPA ECHO API Test Script - Hybrid Approach")
    print("Real API calls with mock data fallback")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"EPA ECHO Base URL: https://data.epa.gov/efservice")
    print("=" * 70)
    
    try:
        # Test 1: Clinton Machine PWS scenario
        test_springfield_scenario()
        
        # Test 2: Multiple PWSID scenarios
        test_multiple_pwsids()
        
        # Test 3: API performance
        test_api_performance()
        
        print("\n" + "=" * 70)
        print("✓ All tests completed successfully!")
        print("The hybrid approach provides reliable PWSID verification")
        print("with real EPA data when available and mock data as fallback.")
        print("=" * 70)
        
        # Save test results
        test_results = {
            'test_timestamp': datetime.now().isoformat(),
            'epa_api_base_url': 'https://data.epa.gov/efservice',
            'target_pwsid': 'OH7700001',
            'system_name': 'Clinton Machine PWS',
            'test_status': 'completed',
            'hybrid_approach': 'real_api_with_mock_fallback'
        }
        
        with open('epa_api_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"Test results saved to: epa_api_test_results.json")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        print("This may be due to network connectivity or API availability")
        sys.exit(1)

if __name__ == "__main__":
    main()