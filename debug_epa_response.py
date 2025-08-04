#!/usr/bin/env python3
"""
EPA API Response Debug Script
Shows the exact raw JSON response from EPA ECHO API for PWSID OH7700001

This script helps debug what data we actually receive from the EPA API
to understand the structure and content of real responses.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class EPAAPIDebugger:
    """
    Debug tool for examining EPA ECHO API responses in detail
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EPA-API-Debugger/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        self.timeout = 30
        
        # Multiple EPA API endpoint formats to test
        self.api_endpoints = [
            'https://data.epa.gov/efservice/sdwis.water_system/pwsid/equals/{pwsid}/json',
            'https://data.epa.gov/efservice/SDWIS.WATER_SYSTEM/PWSID/EQUALS/{pwsid}/JSON',
            'https://data.epa.gov/efservice/sdwis_water_system/pwsid/equals/{pwsid}/json',
            'https://data.epa.gov/efservice/SDWIS_WATER_SYSTEM/PWSID/EQUALS/{pwsid}/JSON',
            'https://data.epa.gov/efservice/water_system/pwsid/equals/{pwsid}/json',
            'https://data.epa.gov/efservice/WATER_SYSTEM/PWSID/EQUALS/{pwsid}/JSON'
        ]
    
    def test_api_connectivity(self) -> bool:
        """Test basic EPA API connectivity"""
        print("🔗 Testing EPA API Connectivity")
        print("-" * 50)
        
        # Test general EPA data service availability
        test_urls = [
            'https://data.epa.gov/efservice/sdwis.water_system/state_code/equals/OH/rows/0:1/json',
            'https://data.epa.gov/efservice/SDWIS.WATER_SYSTEM/STATE_CODE/EQUALS/OH/ROWS/0:1/JSON'
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\nTest {i}: General API Connectivity")
            print(f"URL: {url}")
            
            try:
                start_time = time.time()
                response = self.session.get(url, timeout=self.timeout)
                end_time = time.time()
                
                print(f"Status Code: {response.status_code}")
                print(f"Response Time: {end_time - start_time:.2f}s")
                print(f"Content Length: {len(response.content)} bytes")
                print(f"Content Type: {response.headers.get('Content-Type', 'Unknown')}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"JSON Valid: Yes")
                        print(f"Response Type: {type(data)}")
                        
                        if isinstance(data, list):
                            print(f"Array Length: {len(data)}")
                            if len(data) > 0:
                                print(f"First Record Keys: {list(data[0].keys())[:10]}")
                                print("✅ API is responsive and returning valid data")
                                return True
                        elif isinstance(data, dict):
                            print(f"Object Keys: {list(data.keys())[:10]}")
                            if data:
                                print("✅ API is responsive and returning valid data")
                                return True
                        else:
                            print(f"Unexpected data type: {type(data)}")
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {e}")
                        print(f"Raw Response (first 500 chars): {response.text[:500]}")
                        
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"Response Headers: {dict(response.headers)}")
                    
            except requests.exceptions.Timeout:
                print(f"❌ Timeout after {self.timeout}s")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("⚠️ API connectivity test failed")
        return False
    
    def debug_pwsid_response(self, pwsid: str) -> Dict[str, Any]:
        """
        Debug EPA API response for specific PWSID
        
        Returns detailed information about the API response
        """
        print(f"\n🔍 Debugging EPA API Response for PWSID: {pwsid}")
        print("=" * 70)
        
        debug_results = {
            'pwsid': pwsid,
            'timestamp': datetime.now().isoformat(),
            'endpoints_tested': [],
            'successful_endpoints': [],
            'failed_endpoints': [],
            'raw_responses': {},
            'parsed_data': {},
            'summary': {}
        }
        
        for i, endpoint_template in enumerate(self.api_endpoints, 1):
            endpoint = endpoint_template.format(pwsid=pwsid)
            
            print(f"\n[{i}/{len(self.api_endpoints)}] Testing Endpoint")
            print(f"URL: {endpoint}")
            print("-" * 50)
            
            endpoint_result = {
                'url': endpoint,
                'status': 'unknown',
                'status_code': None,
                'response_time': None,
                'content_length': 0,
                'content_type': None,
                'headers': {},
                'raw_response': None,
                'parsed_data': None,
                'error': None
            }
            
            try:
                start_time = time.time()
                response = self.session.get(endpoint, timeout=self.timeout)
                end_time = time.time()
                
                endpoint_result['status_code'] = response.status_code
                endpoint_result['response_time'] = round(end_time - start_time, 3)
                endpoint_result['content_length'] = len(response.content)
                endpoint_result['content_type'] = response.headers.get('Content-Type', 'Unknown')
                endpoint_result['headers'] = dict(response.headers)
                endpoint_result['raw_response'] = response.text
                
                print(f"Status Code: {response.status_code}")
                print(f"Response Time: {endpoint_result['response_time']}s")
                print(f"Content Length: {endpoint_result['content_length']} bytes")
                print(f"Content Type: {endpoint_result['content_type']}")
                
                if response.status_code == 200:
                    try:
                        parsed_data = response.json()
                        endpoint_result['parsed_data'] = parsed_data
                        endpoint_result['status'] = 'success'
                        
                        print(f"✅ SUCCESS - Valid JSON Response")
                        print(f"Response Type: {type(parsed_data)}")
                        
                        if isinstance(parsed_data, list):
                            print(f"Array Length: {len(parsed_data)}")
                            
                            if len(parsed_data) > 0:
                                first_record = parsed_data[0]
                                print(f"First Record Type: {type(first_record)}")
                                
                                if isinstance(first_record, dict):
                                    print(f"First Record Keys ({len(first_record)}): {list(first_record.keys())}")
                                    
                                    # Show key water system fields
                                    key_fields = ['PWSID', 'PWS_NAME', 'POPULATION_SERVED_COUNT', 
                                                'PWS_TYPE_CODE', 'PWS_ACTIVITY_CODE', 'CITY_NAME', 
                                                'COUNTY_NAME', 'STATE_CODE']
                                    
                                    print("\nKey Water System Fields:")
                                    for field in key_fields:
                                        if field in first_record:
                                            value = first_record[field]
                                            print(f"  {field}: {value}")
                                    
                                    # Show all fields for complete analysis
                                    print(f"\nAll Fields in Response:")
                                    for key, value in first_record.items():
                                        value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                                        print(f"  {key}: {value_str}")
                                
                                debug_results['successful_endpoints'].append(endpoint)
                                
                            else:
                                print("Empty array - no data found")
                                endpoint_result['status'] = 'empty'
                                
                        elif isinstance(parsed_data, dict):
                            print(f"Object Keys ({len(parsed_data)}): {list(parsed_data.keys())}")
                            
                            if parsed_data:
                                print("\nObject Contents:")
                                for key, value in parsed_data.items():
                                    value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                                    print(f"  {key}: {value_str}")
                                
                                debug_results['successful_endpoints'].append(endpoint)
                            else:
                                print("Empty object - no data found")
                                endpoint_result['status'] = 'empty'
                        
                        else:
                            print(f"Unexpected response type: {type(parsed_data)}")
                            print(f"Raw data: {parsed_data}")
                            endpoint_result['status'] = 'unexpected_format'
                    
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Parse Error: {e}")
                        print(f"Raw Response (first 1000 chars):")
                        print(response.text[:1000])
                        print("..." if len(response.text) > 1000 else "")
                        
                        endpoint_result['status'] = 'json_error'
                        endpoint_result['error'] = str(e)
                
                elif response.status_code == 404:
                    print("⚪ Not Found (404) - PWSID may not exist")
                    endpoint_result['status'] = 'not_found'
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"Response Headers: {dict(response.headers)}")
                    print(f"Response Text (first 500 chars): {response.text[:500]}")
                    
                    endpoint_result['status'] = 'http_error'
                    endpoint_result['error'] = f"HTTP {response.status_code}"
            
            except requests.exceptions.Timeout:
                print(f"❌ Timeout after {self.timeout}s")
                endpoint_result['status'] = 'timeout'
                endpoint_result['error'] = f"Timeout after {self.timeout}s"
                
            except Exception as e:
                print(f"❌ Request Error: {e}")
                endpoint_result['status'] = 'request_error'
                endpoint_result['error'] = str(e)
            
            debug_results['endpoints_tested'].append(endpoint_result)
            
            if endpoint_result['status'] == 'success':
                debug_results['successful_endpoints'].append(endpoint)
                debug_results['raw_responses'][endpoint] = endpoint_result['raw_response']
                debug_results['parsed_data'][endpoint] = endpoint_result['parsed_data']
            else:
                debug_results['failed_endpoints'].append(endpoint)
            
            # Small delay between requests to be respectful
            time.sleep(0.5)
        
        # Generate summary
        debug_results['summary'] = {
            'total_endpoints_tested': len(self.api_endpoints),
            'successful_endpoints': len(debug_results['successful_endpoints']),
            'failed_endpoints': len(debug_results['failed_endpoints']),
            'success_rate': len(debug_results['successful_endpoints']) / len(self.api_endpoints) * 100,
            'data_found': len(debug_results['successful_endpoints']) > 0
        }
        
        return debug_results
    
    def generate_debug_report(self, debug_results: Dict[str, Any]) -> str:
        """Generate a comprehensive debug report"""
        
        report = []
        report.append("EPA API Debug Report")
        report.append("=" * 60)
        report.append(f"PWSID: {debug_results['pwsid']}")
        report.append(f"Debug Timestamp: {debug_results['timestamp']}")
        report.append(f"Total Endpoints Tested: {debug_results['summary']['total_endpoints_tested']}")
        report.append(f"Successful Endpoints: {debug_results['summary']['successful_endpoints']}")
        report.append(f"Failed Endpoints: {debug_results['summary']['failed_endpoints']}")
        report.append(f"Success Rate: {debug_results['summary']['success_rate']:.1f}%")
        report.append(f"Data Found: {'Yes' if debug_results['summary']['data_found'] else 'No'}")
        report.append("")
        
        if debug_results['successful_endpoints']:
            report.append("SUCCESSFUL ENDPOINTS:")
            report.append("-" * 30)
            for endpoint in debug_results['successful_endpoints']:
                report.append(f"✅ {endpoint}")
            report.append("")
            
            # Show first successful response in detail
            first_successful = debug_results['successful_endpoints'][0]
            if first_successful in debug_results['parsed_data']:
                data = debug_results['parsed_data'][first_successful]
                report.append("SAMPLE SUCCESSFUL RESPONSE:")
                report.append("-" * 35)
                report.append(f"Endpoint: {first_successful}")
                
                if isinstance(data, list) and len(data) > 0:
                    record = data[0]
                    report.append(f"Record Type: {type(record)}")
                    report.append(f"Field Count: {len(record) if isinstance(record, dict) else 'N/A'}")
                    
                    if isinstance(record, dict):
                        report.append("\nKey Fields:")
                        key_fields = ['PWSID', 'PWS_NAME', 'POPULATION_SERVED_COUNT', 
                                    'PWS_TYPE_CODE', 'PWS_ACTIVITY_CODE']
                        for field in key_fields:
                            if field in record:
                                report.append(f"  {field}: {record[field]}")
                
                elif isinstance(data, dict):
                    report.append(f"Object Type: {type(data)}")
                    report.append(f"Key Count: {len(data)}")
                    report.append("\nKeys:")
                    for key in list(data.keys())[:10]:
                        report.append(f"  {key}: {data[key]}")
        
        if debug_results['failed_endpoints']:
            report.append("\nFAILED ENDPOINTS:")
            report.append("-" * 25)
            for endpoint in debug_results['failed_endpoints']:
                report.append(f"❌ {endpoint}")
        
        # Show endpoint test details
        report.append("\nDETAILED ENDPOINT RESULTS:")
        report.append("-" * 35)
        for i, result in enumerate(debug_results['endpoints_tested'], 1):
            report.append(f"\n{i}. {result['url']}")
            report.append(f"   Status: {result['status']}")
            report.append(f"   HTTP Code: {result['status_code']}")
            report.append(f"   Response Time: {result['response_time']}s")
            report.append(f"   Content Length: {result['content_length']} bytes")
            if result['error']:
                report.append(f"   Error: {result['error']}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)

def main():
    """Main debug execution"""
    
    # Target PWSID for our Clinton Machine PWS demo
    target_pwsid = 'OH7700001'
    
    print("EPA API Response Debugger")
    print("=" * 70)
    print(f"Target PWSID: {target_pwsid} (Clinton Machine PWS)")
    print(f"Purpose: Debug real EPA API responses for compliance testing")
    print("=" * 70)
    
    debugger = EPAAPIDebugger()
    
    try:
        # Test API connectivity first
        print("Phase 1: Testing EPA API Connectivity")
        api_available = debugger.test_api_connectivity()
        
        print(f"\nPhase 2: Debugging PWSID {target_pwsid}")
        debug_results = debugger.debug_pwsid_response(target_pwsid)
        
        # Generate and display report
        print(f"\n{'='*70}")
        print("DEBUG RESULTS SUMMARY")
        print(f"{'='*70}")
        
        report = debugger.generate_debug_report(debug_results)
        print(report)
        
        # Save detailed results to JSON file
        debug_filename = f'epa_api_debug_{target_pwsid}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(debug_filename, 'w') as f:
            json.dump(debug_results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed debug results saved to: {debug_filename}")
        
        # Save report to text file
        report_filename = f'epa_api_debug_report_{target_pwsid}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"📁 Debug report saved to: {report_filename}")
        
        # Return status
        if debug_results['summary']['data_found']:
            print(f"\n✅ SUCCESS: Found EPA data for PWSID {target_pwsid}")
            print("This PWSID can be used for authentic EPA compliance testing!")
            return 0
        else:
            print(f"\n⚠️ NO DATA: EPA API did not return data for PWSID {target_pwsid}")
            print("This may indicate the PWSID doesn't exist or API issues.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Debug interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Debug failed with error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)