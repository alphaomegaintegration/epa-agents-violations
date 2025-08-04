#!/usr/bin/env python3
"""
Find Real EPA Water Systems
Query EPA ECHO API to find actual, active water systems for demo
"""

import requests
import json
import time

def search_epa_systems(state_code="OH", limit=10):
    """Search for real EPA water systems"""
    
    print(f"🔍 Searching for real EPA water systems in {state_code}...")
    
    url = f"https://data.epa.gov/efservice/sdwis.water_system/state_code/equals/{state_code}/json"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Found {len(data)} water systems in {state_code}")
            
            # Filter for active systems with good data
            active_systems = []
            for system in data[:50]:  # Check first 50
                if (system.get('pws_activity_code') == 'A' and  # Active
                    system.get('population_served_count', 0) > 0 and  # Has population
                    system.get('pws_name') and  # Has name
                    system.get('pwsid')):  # Has PWSID
                    
                    active_systems.append({
                        'pwsid': system.get('pwsid'),
                        'name': system.get('pws_name'),
                        'population': system.get('population_served_count', 0),
                        'type': system.get('pws_type_code'),
                        'city': system.get('city_name'),
                        'activity': system.get('pws_activity_code')
                    })
                
                if len(active_systems) >= limit:
                    break
            
            return active_systems
            
        else:
            print(f"❌ EPA API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def get_system_details(pwsid):
    """Get detailed info for a specific system"""
    
    print(f"📊 Getting details for {pwsid}...")
    
    url = f"https://data.epa.gov/efservice/sdwis.water_system/pwsid/equals/{pwsid}/json"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
        return None
    except:
        return None

def main():
    print("🏛️  REAL EPA WATER SYSTEMS FINDER")
    print("=" * 60)
    
    # Search multiple states for variety
    states = ["OH", "CA", "NY", "TX", "FL"]
    all_systems = []
    
    for state in states:
        systems = search_epa_systems(state, limit=3)
        all_systems.extend(systems)
        time.sleep(1)  # Be nice to EPA API
    
    print(f"\n📋 FOUND {len(all_systems)} REAL ACTIVE EPA SYSTEMS:")
    print("=" * 60)
    
    real_systems = {}
    
    for i, system in enumerate(all_systems[:10], 1):  # Limit to 10 for demo
        print(f"\n{i}. {system['name']}")
        print(f"   PWSID: {system['pwsid']}")
        print(f"   Population: {system['population']:,}")
        print(f"   Type: {system['type']}")
        print(f"   Location: {system['city']}")
        
        # Get full details
        details = get_system_details(system['pwsid'])
        if details:
            real_systems[system['pwsid']] = {
                "name": system['name'],
                "description": f"{system['type']} serving {system['city']}",
                "population": system['population'],
                "type": system['type'],
                "city": system['city'],
                "state": details.get('state_code'),
                "epa_region": details.get('epa_region'),
                "source_type": details.get('primary_source_code'),
                "owner_type": details.get('owner_type_code')
            }
        
        time.sleep(0.5)  # Rate limiting
    
    # Save results
    with open("real_epa_systems.json", "w") as f:
        json.dump(real_systems, f, indent=2)
    
    print(f"\n💾 Saved {len(real_systems)} real EPA systems to real_epa_systems.json")
    
    print("\n🎯 RECOMMENDED SYSTEMS FOR DEMO:")
    print("=" * 60)
    
    # Categorize by size for demo variety
    small = [s for s in real_systems.values() if s['population'] < 1000]
    medium = [s for s in real_systems.values() if 1000 <= s['population'] < 50000]
    large = [s for s in real_systems.values() if s['population'] >= 50000]
    
    if small:
        print("🏘️  Small Systems (< 1,000 people):")
        for s in small[:2]:
            print(f"   • {s['name']} - {s['population']:,} people")
    
    if medium:
        print("🏙️  Medium Systems (1K - 50K people):")
        for s in medium[:2]:
            print(f"   • {s['name']} - {s['population']:,} people")
    
    if large:
        print("🌆 Large Systems (50K+ people):")
        for s in large[:2]:
            print(f"   • {s['name']} - {s['population']:,} people")

if __name__ == "__main__":
    main()