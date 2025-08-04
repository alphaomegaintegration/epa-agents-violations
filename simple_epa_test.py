#!/usr/bin/env python3
"""
Simple EPA API Test for PWSID OH7700001
Shows the exact EPA response data clearly and concisely
"""

import requests
import json
import time

def test_epa_api():
    """Test EPA API for PWSID OH7700001 and show response"""
    
    pwsid = 'OH7700001'
    print(f"EPA API Test for PWSID: {pwsid}")
    print("=" * 50)
    
    # EPA API endpoint
    url = f'https://data.epa.gov/efservice/sdwis.water_system/pwsid/equals/{pwsid}/json'
    
    print(f"API Endpoint: {url}")
    print(f"Making request...")
    
    try:
        # Make the API request
        start_time = time.time()
        response = requests.get(url, timeout=15)
        end_time = time.time()
        
        print(f"Response Time: {end_time - start_time:.2f}s")
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ API Request Successful")
            
            try:
                # Parse JSON response
                data = response.json()
                
                print(f"\nResponse Type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"Array Length: {len(data)}")
                    
                    if len(data) > 0:
                        print("\n🎉 DATA FOUND!")
                        print("-" * 30)
                        
                        # Show the first (and likely only) record
                        record = data[0]
                        print(f"Record Type: {type(record)}")
                        print(f"Number of Fields: {len(record) if isinstance(record, dict) else 'N/A'}")
                        
                        if isinstance(record, dict):
                            print(f"\nWater System Information:")
                            print(f"  PWSID: {record.get('PWSID', 'N/A')}")
                            print(f"  System Name: {record.get('PWS_NAME', 'N/A')}")
                            print(f"  Population Served: {record.get('POPULATION_SERVED_COUNT', 'N/A')}")
                            print(f"  System Type: {record.get('PWS_TYPE_CODE', 'N/A')}")
                            print(f"  Activity Status: {record.get('PWS_ACTIVITY_CODE', 'N/A')}")
                            print(f"  City: {record.get('CITY_NAME', 'N/A')}")
                            print(f"  County: {record.get('COUNTY_NAME', 'N/A')}")
                            print(f"  State: {record.get('STATE_CODE', 'N/A')}")
                            
                            print(f"\nComplete Raw JSON Response:")
                            print(json.dumps(record, indent=2))
                            
                            # Save to file
                            with open(f'epa_response_{pwsid}.json', 'w') as f:
                                json.dump(data, f, indent=2)
                            
                            print(f"\n📁 Full response saved to: epa_response_{pwsid}.json")
                            
                        return True, data
                    else:
                        print("\n⚪ Empty Response - No data found")
                        return False, None
                
                elif isinstance(data, dict):
                    print(f"Object Keys: {list(data.keys())}")
                    
                    if data:
                        print("\n🎉 DATA FOUND!")
                        print("-" * 30)
                        print(json.dumps(data, indent=2))
                        return True, data
                    else:
                        print("\n⚪ Empty Object - No data found")
                        return False, None
                
                else:
                    print(f"\n❓ Unexpected response type: {type(data)}")
                    print(f"Raw data: {data}")
                    return False, None
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON Parse Error: {e}")
                print(f"Raw Response: {response.text[:1000]}")
                return False, None
        
        elif response.status_code == 404:
            print(f"\n⚪ PWSID {pwsid} not found in EPA database")
            return False, None
        
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 15 seconds")
        return False, None
    
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False, None

def main():
    """Main test execution"""
    
    print("Simple EPA API Test")
    print("Testing real working PWSID OH7700001 (Clinton Machine PWS)")
    print("=" * 60)
    
    success, data = test_epa_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST RESULT: SUCCESS")
        print("PWSID OH7700001 returns actual EPA data!")
        print("This can be used for authentic compliance testing.")
    else:
        print("❌ TEST RESULT: NO DATA")
        print("PWSID OH7700001 did not return EPA data.")
        print("May need to use mock data for testing.")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())