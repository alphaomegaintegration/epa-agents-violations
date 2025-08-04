#!/usr/bin/env python3
"""
Fetch Real EPA Violation Data
Query EPA ECHO API for actual drinking water violations from real water systems
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Real major water systems we found
MAJOR_SYSTEMS = [
    "CA1910067",  # Los Angeles DWP - 3.8M people
    "FL4130871",  # Miami-Dade - 2.3M people  
    "TX1010013",  # Houston - 2.2M people
    "OH1801212",  # Cleveland - 1.3M people
    "OH2504412",  # Columbus - 1.3M people
    "OH3102612",  # Cincinnati - 750K people
    "CA3710020",  # San Diego - 1.4M people
    "OH7700001"   # Clinton Machine - 76 people (our test system)
]

def fetch_sdwis_violations(pwsid):
    """Fetch real violations from EPA SDWIS database"""
    
    print(f"🔍 Fetching real violations for {pwsid}...")
    
    # Try multiple EPA SDWIS endpoints for violations
    endpoints = [
        f"https://data.epa.gov/efservice/sdwis.violation/pwsid/equals/{pwsid}/json",
        f"https://data.epa.gov/efservice/sdwis.enforcement_action/pwsid/equals/{pwsid}/json",
        f"https://data.epa.gov/efservice/sdwis.lcr_sample_result/pwsid/equals/{pwsid}/json"
    ]
    
    all_violations = []
    
    for endpoint in endpoints:
        try:
            print(f"   📡 Querying: {endpoint.split('/')[-3]}...")
            response = requests.get(endpoint, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    print(f"   ✅ Found {len(data)} records")
                    all_violations.extend(data)
                else:
                    print(f"   ⚪ No data found")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    return all_violations

def fetch_echo_violations(pwsid):
    """Fetch violations from EPA ECHO database"""
    
    print(f"🔍 Checking EPA ECHO for {pwsid}...")
    
    # EPA ECHO API for drinking water facilities
    echo_url = f"https://echo.epa.gov/echo/sdw_rest_services.get_facilities"
    
    params = {
        'output': 'JSON',
        'p_pwsid': pwsid,
        'p_rows': 50
    }
    
    try:
        response = requests.get(echo_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'Results' in data and 'Results' in data['Results']:
                facilities = data['Results']['Results']
                print(f"   ✅ Found {len(facilities)} ECHO facilities")
                return facilities
            else:
                print(f"   ⚪ No ECHO data found")
                return []
        else:
            print(f"   ❌ ECHO HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ ECHO Error: {e}")
        return []

def analyze_system_violations():
    """Analyze violations across multiple real EPA systems"""
    
    print("🏛️  REAL EPA VIOLATION DATA FETCHER")
    print("=" * 60)
    print("Fetching actual violation data from EPA databases...")
    print()
    
    all_system_data = {}
    
    for i, pwsid in enumerate(MAJOR_SYSTEMS, 1):
        print(f"📊 SYSTEM {i}/{len(MAJOR_SYSTEMS)}: {pwsid}")
        print("-" * 40)
        
        # Get basic system info
        try:
            sys_url = f"https://data.epa.gov/efservice/sdwis.water_system/pwsid/equals/{pwsid}/json"
            sys_response = requests.get(sys_url, timeout=15)
            
            if sys_response.status_code == 200:
                sys_data = sys_response.json()
                if sys_data and len(sys_data) > 0:
                    system_info = sys_data[0]
                    name = system_info.get('pws_name', 'Unknown')
                    population = system_info.get('population_served_count', 0)
                    print(f"🏛️  {name} - {population:,} people")
                else:
                    print(f"⚠️  System info not found")
                    continue
            else:
                print(f"❌ System lookup failed")
                continue
                
        except Exception as e:
            print(f"❌ System error: {e}")
            continue
        
        # Fetch violations from multiple sources
        sdwis_violations = fetch_sdwis_violations(pwsid)
        echo_data = fetch_echo_violations(pwsid)
        
        # Store results
        all_system_data[pwsid] = {
            "system_info": system_info,
            "sdwis_violations": sdwis_violations,
            "echo_data": echo_data,
            "total_violation_records": len(sdwis_violations),
            "echo_facilities": len(echo_data)
        }
        
        print(f"📈 Total Records: {len(sdwis_violations)} SDWIS + {len(echo_data)} ECHO")
        print()
        
        time.sleep(2)  # Rate limiting between systems
    
    # Save all data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"real_epa_violations_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_system_data, f, indent=2, default=str)
    
    print("=" * 60)
    print("📊 REAL EPA VIOLATION DATA SUMMARY:")
    print("=" * 60)
    
    total_systems = len(all_system_data)
    total_violations = sum(data['total_violation_records'] for data in all_system_data.values())
    total_echo_records = sum(data['echo_facilities'] for data in all_system_data.values())
    
    print(f"🏛️  Systems Analyzed: {total_systems}")
    print(f"🚨 Total SDWIS Records: {total_violations}")
    print(f"📡 Total ECHO Records: {total_echo_records}")
    print(f"💾 Data saved to: {filename}")
    
    # Show systems with most violation data
    print(f"\n🎯 SYSTEMS WITH MOST VIOLATION DATA:")
    print("-" * 40)
    
    sorted_systems = sorted(all_system_data.items(), 
                           key=lambda x: x[1]['total_violation_records'], 
                           reverse=True)
    
    for pwsid, data in sorted_systems[:5]:
        name = data['system_info'].get('pws_name', 'Unknown')
        violations = data['total_violation_records']
        echo_records = data['echo_facilities']
        population = data['system_info'].get('population_served_count', 0)
        
        print(f"• {name[:50]}")
        print(f"  PWSID: {pwsid} | Pop: {population:,}")
        print(f"  Violations: {violations} | ECHO: {echo_records}")
        print()
    
    return all_system_data

if __name__ == "__main__":
    violation_data = analyze_system_violations()
    
    print("\n🚀 NEXT STEPS:")
    print("=" * 60)
    print("1. Review the violation data in the generated JSON file")
    print("2. Identify systems with interesting violation patterns")  
    print("3. Use real violation data in the agentic system demo")
    print("4. Create realistic violation scenarios based on actual EPA data")