#!/usr/bin/env python3
"""
Find Major EPA Water Systems
Search for large, well-known municipal water systems
"""

import requests
import json
import time

# Known major city water systems to search for
MAJOR_CITIES = [
    {"city": "COLUMBUS", "state": "OH"},
    {"city": "CLEVELAND", "state": "OH"}, 
    {"city": "CINCINNATI", "state": "OH"},
    {"city": "LOS ANGELES", "state": "CA"},
    {"city": "SAN FRANCISCO", "state": "CA"},
    {"city": "SAN DIEGO", "state": "CA"},
    {"city": "NEW YORK", "state": "NY"},
    {"city": "BUFFALO", "state": "NY"},
    {"city": "HOUSTON", "state": "TX"},
    {"city": "DALLAS", "state": "TX"},
    {"city": "MIAMI", "state": "FL"},
    {"city": "TAMPA", "state": "FL"}
]

def search_by_city(city, state):
    """Search for water systems by city name"""
    
    print(f"🔍 Searching for {city}, {state} water systems...")
    
    url = f"https://data.epa.gov/efservice/sdwis.water_system/city_name/equals/{city}/state_code/equals/{state}/json"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print(f"   No systems found for {city}, {state}")
                return []
            
            # Filter for large, active community water systems
            major_systems = []
            for system in data:
                if (system.get('pws_activity_code') == 'A' and  # Active
                    system.get('pws_type_code') == 'CWS' and  # Community Water System
                    system.get('population_served_count', 0) > 10000):  # Large system
                    
                    major_systems.append({
                        'pwsid': system.get('pwsid'),
                        'name': system.get('pws_name'),
                        'population': system.get('population_served_count', 0),
                        'type': system.get('pws_type_code'),
                        'city': system.get('city_name'),
                        'state': system.get('state_code'),
                        'activity': system.get('pws_activity_code'),
                        'epa_region': system.get('epa_region')
                    })
            
            # Sort by population (largest first)
            major_systems.sort(key=lambda x: x['population'], reverse=True)
            
            for system in major_systems[:3]:  # Show top 3
                print(f"   ✅ {system['name']} - {system['population']:,} people (PWSID: {system['pwsid']})")
            
            return major_systems[:3]
            
        else:
            print(f"   ❌ API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def main():
    print("🏛️  MAJOR EPA WATER SYSTEMS FINDER")
    print("=" * 60)
    
    all_major_systems = {}
    
    for city_info in MAJOR_CITIES:
        systems = search_by_city(city_info["city"], city_info["state"])
        
        for system in systems:
            all_major_systems[system['pwsid']] = {
                "name": system['name'],
                "description": f"Major municipal system serving {system['city']}, {system['state']}",
                "population": system['population'],
                "type": system['type'],
                "city": system['city'],
                "state": system['state'],
                "epa_region": system['epa_region'],
                "category": "major_municipal"
            }
        
        time.sleep(1)  # Rate limiting
    
    # Save results
    with open("major_epa_systems.json", "w") as f:
        json.dump(all_major_systems, f, indent=2)
    
    print(f"\n📋 FOUND {len(all_major_systems)} MAJOR EPA SYSTEMS:")
    print("=" * 60)
    
    # Sort by population for display
    sorted_systems = sorted(all_major_systems.items(), 
                          key=lambda x: x[1]['population'], 
                          reverse=True)
    
    for i, (pwsid, system) in enumerate(sorted_systems[:10], 1):
        print(f"{i:2d}. {system['name']}")
        print(f"    PWSID: {pwsid}")
        print(f"    Population: {system['population']:,}")
        print(f"    Location: {system['city']}, {system['state']}")
        print(f"    EPA Region: {system['epa_region']}")
        print()
    
    print(f"💾 Saved {len(all_major_systems)} major systems to major_epa_systems.json")
    
    # Recommend diverse set for demo
    print("\n🎯 RECOMMENDED DEMO SYSTEMS (by size):")
    print("=" * 60)
    
    mega = [(pwsid, s) for pwsid, s in sorted_systems if s['population'] > 1000000]
    large = [(pwsid, s) for pwsid, s in sorted_systems if 100000 <= s['population'] <= 1000000]
    medium = [(pwsid, s) for pwsid, s in sorted_systems if 10000 <= s['population'] < 100000]
    
    if mega:
        print("🌆 Mega Systems (1M+ people):")
        for pwsid, s in mega[:2]:
            print(f"   • {s['name']} ({pwsid}) - {s['population']:,} people")
    
    if large:
        print("🏙️  Large Systems (100K - 1M people):")
        for pwsid, s in large[:3]:
            print(f"   • {s['name']} ({pwsid}) - {s['population']:,} people")
    
    if medium:
        print("🏘️  Medium Systems (10K - 100K people):")
        for pwsid, s in medium[:2]:
            print(f"   • {s['name']} ({pwsid}) - {s['population']:,} people")

if __name__ == "__main__":
    main()