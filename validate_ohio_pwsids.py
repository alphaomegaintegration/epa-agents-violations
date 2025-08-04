#!/usr/bin/env python3
"""
EPA ECHO API Validator for Real Ohio PWSIDs

This script tests real Ohio PWSIDs against the EPA ECHO API to find
systems that return actual data instead of empty responses.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sys

class EPAECHOValidator:
    """
    EPA ECHO API validator for testing real Ohio PWSIDs
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EPA-PWSID-Validator/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        # Multiple EPA API endpoint formats to try
        self.api_endpoints = [
            'https://data.epa.gov/efservice/sdwis.water_system/pwsid/equals/{pwsid}/json',
            'https://data.epa.gov/efservice/SDWIS.WATER_SYSTEM/PWSID/EQUALS/{pwsid}/JSON',
            'https://data.epa.gov/efservice/sdwis_water_system/pwsid/equals/{pwsid}/json',
            'https://data.epa.gov/efservice/SDWIS_WATER_SYSTEM/PWSID/EQUALS/{pwsid}/JSON',
            'https://data.epa.gov/efservice/water_system/pwsid/equals/{pwsid}/json',
            'https://data.epa.gov/efservice/WATER_SYSTEM/PWSID/EQUALS/{pwsid}/JSON'
        ]
        
        self.timeout = 15
        self.delay_between_requests = 1.0
        
        # Real Ohio PWSIDs to test based on major water systems
        self.ohio_test_pwsids = [
            'OH3900001',  # Cincinnati area (Hamilton County)
            'OH1800001',  # Cleveland area (Cuyahoga County)
            'OH2500001',  # Columbus area (Franklin County)
            'OH5100001',  # Toledo area (Lucas County)
            'OH7700001',  # Akron area (Summit County)
            'OH3901000',  # Alternative Cincinnati pattern
            'OH1801000',  # Alternative Cleveland pattern
            'OH2501000',  # Alternative Columbus pattern
            'OH0390001',  # Different Hamilton County format
            'OH0180001',  # Different Cuyahoga County format
            'OH0250001',  # Different Franklin County format
            'OH3900100',  # Another Cincinnati variation
            'OH1800100',  # Another Cleveland variation
            'OH2500100',  # Another Columbus variation
            # Additional realistic patterns
            'OH0000001', 'OH0000010', 'OH0000100', 'OH0001000',
            'OH1000000', 'OH2000000', 'OH3000000',
            'OH0100000', 'OH0200000', 'OH0300000'
        ]
    
    def test_api_connectivity(self) -> bool:
        """
        Test basic EPA API connectivity
        """
        print("🔗 Testing EPA API connectivity...")
        
        # Try a simple EPA data service query
        test_urls = [
            'https://data.epa.gov/efservice/sdwis.water_system/state_code/equals/OH/rows/0:1/json',
            'https://data.epa.gov/efservice/SDWIS.WATER_SYSTEM/STATE_CODE/EQUALS/OH/ROWS/0:1/JSON'
        ]
        
        for url in test_urls:
            try:
                print(f"   Testing: {url}")
                response = self.session.get(url, timeout=self.timeout)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and len(data) > 0:
                            print("   ✓ API is responsive and returning data")
                            print(f"   Sample response keys: {list(data[0].keys())[:10]}")
                            return True
                    except json.JSONDecodeError:
                        print("   ⚠ API responded but data is not valid JSON")
                        
            except Exception as e:
                print(f"   ✗ Error: {e}")
        
        print("   ⚠ API connectivity test failed")
        return False
    
    def test_pwsid_against_endpoints(self, pwsid: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Test a PWSID against all available EPA API endpoints
        
        Returns:
            Tuple of (success, data, endpoint_used)
        """
        print(f"   Testing PWSID {pwsid} against EPA endpoints...")
        
        for endpoint_template in self.api_endpoints:
            endpoint = endpoint_template.format(pwsid=pwsid)
            
            try:
                print(f"     Trying: {endpoint}")
                response = self.session.get(endpoint, timeout=self.timeout)
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check if we got actual data
                        if data and len(data) > 0:
                            if isinstance(data, list):
                                if len(data) > 0 and isinstance(data[0], dict):
                                    print(f"     ✓ Found data! Record keys: {list(data[0].keys())[:10]}")
                                    return True, data, endpoint
                            elif isinstance(data, dict):
                                if data:  # Non-empty dict
                                    print(f"     ✓ Found data! Dict keys: {list(data.keys())[:10]}")
                                    return True, [data], endpoint  # Wrap in list for consistency
                            
                        print("     ○ Empty response")
                        
                    except json.JSONDecodeError as e:
                        print(f"     ✗ JSON decode error: {e}")
                        
                elif response.status_code == 404:
                    print("     ○ Not found")
                else:
                    print(f"     ✗ HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"     ✗ Timeout after {self.timeout}s")
            except Exception as e:
                print(f"     ✗ Error: {e}")
            
            # Small delay between endpoint tests
            time.sleep(0.2)
        
        return False, None, ""
    
    def extract_system_info(self, data: Dict) -> Dict[str, Any]:
        """
        Extract and standardize system information from EPA response
        """
        if not data:
            return {}
        
        # Handle different field name variations in EPA responses
        system_info = {}
        
        # PWSID
        system_info['pwsid'] = (
            data.get('PWSID') or 
            data.get('pwsid') or 
            data.get('PWS_ID') or 
            'Unknown'
        )
        
        # System Name
        system_info['system_name'] = (
            data.get('PWS_NAME') or 
            data.get('pws_name') or 
            data.get('SYSTEM_NAME') or 
            data.get('system_name') or 
            'Unknown'
        )
        
        # Population
        population_fields = ['POPULATION_SERVED_COUNT', 'population_served_count', 
                           'POPULATION_SERVED', 'population_served', 'POP_SERVED']
        system_info['population_served'] = 'Unknown'
        for field in population_fields:
            if field in data and data[field] is not None:
                try:
                    system_info['population_served'] = int(data[field])
                    break
                except (ValueError, TypeError):
                    continue
        
        # System Type
        system_info['system_type'] = (
            data.get('PWS_TYPE_CODE') or 
            data.get('pws_type_code') or 
            data.get('SYSTEM_TYPE') or 
            'Unknown'
        )
        
        # Activity Status
        system_info['activity_status'] = (
            data.get('PWS_ACTIVITY_CODE') or 
            data.get('pws_activity_code') or 
            data.get('ACTIVITY_CODE') or 
            'Unknown'
        )
        
        # Location info
        system_info['city'] = (
            data.get('CITY_NAME') or 
            data.get('city_name') or 
            data.get('CITY') or 
            'Unknown'
        )
        
        system_info['county'] = (
            data.get('COUNTY_NAME') or 
            data.get('county_name') or 
            data.get('COUNTY') or 
            'Unknown'
        )
        
        system_info['state'] = (
            data.get('STATE_CODE') or 
            data.get('state_code') or 
            data.get('STATE') or 
            'Unknown'
        )
        
        # Additional fields that might be useful
        system_info['owner_type'] = (
            data.get('OWNER_TYPE_CODE') or 
            data.get('owner_type_code') or 
            'Unknown'
        )
        
        system_info['primacy_agency'] = (
            data.get('PRIMACY_AGENCY_CODE') or 
            data.get('primacy_agency_code') or 
            'Unknown'
        )
        
        # Violation count
        violation_fields = ['VIOLATION_COUNT', 'violation_count', 'VIOLATIONS']
        system_info['violations'] = 0
        for field in violation_fields:
            if field in data and data[field] is not None:
                try:
                    system_info['violations'] = int(data[field])
                    break
                except (ValueError, TypeError):
                    continue
        
        return system_info
    
    def validate_ohio_pwsids(self) -> List[Dict[str, Any]]:
        """
        Test all Ohio PWSIDs against EPA ECHO API to find valid systems
        
        Returns:
            List of systems that returned actual data
        """
        print("🏛 EPA ECHO API Validation for Ohio PWSIDs")
        print("=" * 70)
        print(f"Testing {len(self.ohio_test_pwsids)} Ohio PWSID patterns")
        print(f"Timeout: {self.timeout}s per request")
        print(f"Delay between requests: {self.delay_between_requests}s")
        print()
        
        valid_systems = []
        
        for i, pwsid in enumerate(self.ohio_test_pwsids, 1):
            print(f"[{i:2d}/{len(self.ohio_test_pwsids)}] Testing {pwsid}")
            print("-" * 50)
            
            success, data, endpoint = self.test_pwsid_against_endpoints(pwsid)
            
            if success and data:
                print(f"   🎉 SUCCESS! Found valid system data")
                
                # Extract system information
                system_data = data[0] if isinstance(data, list) else data
                system_info = self.extract_system_info(system_data)
                system_info['api_endpoint'] = endpoint
                system_info['raw_data'] = system_data
                
                valid_systems.append(system_info)
                
                # Display found system information
                print(f"   📋 System Information:")
                print(f"       PWSID: {system_info['pwsid']}")
                print(f"       Name: {system_info['system_name']}")
                print(f"       Population: {system_info['population_served']}")
                print(f"       Type: {system_info['system_type']}")
                print(f"       Status: {system_info['activity_status']}")
                print(f"       Location: {system_info['city']}, {system_info['county']} County, {system_info['state']}")
                print(f"       Working Endpoint: {endpoint}")
                
                if system_info['violations'] > 0:
                    print(f"       ⚠ Violations: {system_info['violations']}")
                
                print()
                
            else:
                print(f"   ○ No data found for {pwsid}")
                print()
            
            # Be respectful to the EPA API
            time.sleep(self.delay_between_requests)
        
        return valid_systems
    
    def generate_summary_report(self, valid_systems: List[Dict]) -> str:
        """
        Generate a summary report of validation results
        """
        report = []
        report.append("EPA ECHO API Validation Summary Report")
        report.append("=" * 60)
        report.append(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total PWSIDs Tested: {len(self.ohio_test_pwsids)}")
        report.append(f"Valid Systems Found: {len(valid_systems)}")
        report.append(f"Success Rate: {len(valid_systems)/len(self.ohio_test_pwsids)*100:.1f}%")
        report.append("")
        
        if valid_systems:
            report.append("VALID OHIO WATER SYSTEMS FOUND:")
            report.append("-" * 40)
            
            for i, system in enumerate(valid_systems, 1):
                report.append(f"{i}. PWSID: {system['pwsid']}")
                report.append(f"   System Name: {system['system_name']}")
                report.append(f"   Population: {system['population_served']}")
                report.append(f"   Location: {system['city']}, {system['county']} County")
                report.append(f"   System Type: {system['system_type']}")
                report.append(f"   Status: {system['activity_status']}")
                report.append(f"   Working API Endpoint: {system['api_endpoint']}")
                
                if system['violations'] > 0:
                    report.append(f"   ⚠ Violations on Record: {system['violations']}")
                
                report.append("")
            
            report.append("RECOMMENDED FOR EPA COMPLIANCE TESTING:")
            report.append("-" * 45)
            
            # Sort by population for recommendations
            sorted_systems = sorted(valid_systems, 
                                  key=lambda x: x['population_served'] if isinstance(x['population_served'], int) else 0, 
                                  reverse=True)
            
            categories = [
                ("Large System (>100k population)", lambda s: isinstance(s['population_served'], int) and s['population_served'] > 100000),
                ("Medium System (10k-100k population)", lambda s: isinstance(s['population_served'], int) and 10000 <= s['population_served'] <= 100000),
                ("Small System (<10k population)", lambda s: isinstance(s['population_served'], int) and s['population_served'] < 10000)
            ]
            
            for category_name, filter_func in categories:
                matching_systems = [s for s in sorted_systems if filter_func(s)]
                if matching_systems:
                    best_system = matching_systems[0]
                    report.append(f"{category_name}:")
                    report.append(f"  Recommended PWSID: {best_system['pwsid']}")
                    report.append(f"  System: {best_system['system_name']}")
                    report.append(f"  Population: {best_system['population_served']:,}")
                    report.append("")
        
        else:
            report.append("NO VALID SYSTEMS FOUND")
            report.append("-" * 25)
            report.append("This could indicate:")
            report.append("• EPA API endpoints have changed")
            report.append("• API is temporarily unavailable")
            report.append("• Network connectivity issues")
            report.append("• Different PWSID patterns needed")
            report.append("")
            report.append("Recommendations:")
            report.append("• Check EPA's current API documentation")
            report.append("• Try alternative endpoint formats")
            report.append("• Use mock data for testing purposes")
        
        report.append("=" * 60)
        return "\n".join(report)

def main():
    """
    Main execution function
    """
    print("EPA ECHO API Validator for Real Ohio PWSIDs")
    print("Testing authentic Ohio water system identifiers")
    print("=" * 70)
    
    validator = EPAECHOValidator()
    
    try:
        # Test API connectivity first
        if not validator.test_api_connectivity():
            print("\n⚠ WARNING: EPA API connectivity test failed")
            print("Proceeding with PWSID tests anyway...")
        
        print("\n")
        
        # Test all Ohio PWSIDs
        valid_systems = validator.validate_ohio_pwsids()
        
        # Generate and display summary report
        print("\n" + "=" * 70)
        summary_report = validator.generate_summary_report(valid_systems)
        print(summary_report)
        
        # Save results to files
        if valid_systems:
            # Save detailed JSON results
            results_data = {
                'validation_timestamp': datetime.now().isoformat(),
                'total_tested': len(validator.ohio_test_pwsids),
                'valid_systems_found': len(valid_systems),
                'valid_systems': valid_systems
            }
            
            with open('ohio_pwsid_validation_results.json', 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
            
            print(f"\n📁 Detailed results saved to: ohio_pwsid_validation_results.json")
        
        # Save summary report
        with open('ohio_pwsid_validation_summary.txt', 'w') as f:
            f.write(summary_report)
        
        print(f"📁 Summary report saved to: ohio_pwsid_validation_summary.txt")
        
        # Return success code based on results
        if valid_systems:
            print(f"\n✅ Validation completed successfully!")
            print(f"Found {len(valid_systems)} valid Ohio water systems")
            print("These can be used for authentic EPA compliance testing.")
            return 0
        else:
            print(f"\n⚠ No valid systems found")
            print("Consider using mock data for testing purposes.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠ Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        print("Check network connectivity and EPA API availability")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)