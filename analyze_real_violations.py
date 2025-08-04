#!/usr/bin/env python3
"""
Analyze Real EPA Violations
Parse the fetched violation data to understand what we have
"""

import json
from collections import defaultdict, Counter

def analyze_violations():
    """Analyze the real EPA violation data we fetched"""
    
    # Load the violation data
    with open("real_epa_violations_20250731_144819.json", "r") as f:
        data = json.load(f)
    
    print("🏛️  REAL EPA VIOLATION DATA ANALYSIS")
    print("=" * 60)
    
    violation_types = Counter()
    contaminant_types = Counter() 
    systems_with_data = []
    
    for pwsid, system_data in data.items():
        system_name = system_data["system_info"]["pws_name"]
        population = system_data["system_info"]["population_served_count"]
        violations = system_data["sdwis_violations"]
        
        if violations:
            systems_with_data.append({
                "pwsid": pwsid,
                "name": system_name,
                "population": population,
                "violation_count": len(violations)
            })
            
            # Analyze violation types
            for violation in violations:
                # Common violation fields
                viol_code = violation.get("violation_code", "Unknown")
                viol_category = violation.get("violation_category_code", "Unknown")
                contaminant = violation.get("contaminant_code", "Unknown")
                
                violation_types[viol_code] += 1
                contaminant_types[contaminant] += 1
    
    print(f"📊 SYSTEMS WITH VIOLATION DATA: {len(systems_with_data)}")
    print("-" * 40)
    
    for system in sorted(systems_with_data, key=lambda x: x["violation_count"], reverse=True):
        print(f"• {system['name'][:50]}")
        print(f"  PWSID: {system['pwsid']} | Pop: {system['population']:,} | Violations: {system['violation_count']}")
        print()
    
    print("🚨 TOP VIOLATION TYPES:")
    print("-" * 40)
    for viol_type, count in violation_types.most_common(10):
        print(f"• {viol_type}: {count} occurrences")
    
    print(f"\n🧪 TOP CONTAMINANTS:")
    print("-" * 40)
    for contaminant, count in contaminant_types.most_common(10):
        print(f"• {contaminant}: {count} occurrences")
    
    # Sample some violations for detailed view
    print(f"\n🔍 SAMPLE VIOLATION DETAILS:")
    print("-" * 40)
    
    # Find a system with interesting violations
    sample_system = None
    for pwsid, system_data in data.items():
        if len(system_data["sdwis_violations"]) > 5:
            sample_system = (pwsid, system_data)
            break
    
    if sample_system:
        pwsid, system_data = sample_system
        system_name = system_data["system_info"]["pws_name"]
        print(f"Sample from: {system_name} ({pwsid})")
        print()
        
        # Show first few violations with details
        for i, violation in enumerate(system_data["sdwis_violations"][:3]):
            print(f"Violation {i+1}:")
            
            # Print key fields
            for key in ["violation_code", "violation_category_code", "contaminant_code", 
                       "compl_per_begin_date", "viol_measure", "unit_of_measure"]:
                if key in violation:
                    print(f"  {key}: {violation[key]}")
            print()
    
    return data

if __name__ == "__main__":
    analyze_violations()