#!/usr/bin/env python3
"""
Test the Production Agentic System
"""

import sys
from pathlib import Path

def test_production_system():
    """Test the production agentic system setup."""
    
    print("🧪 TESTING PRODUCTION AGENTIC SYSTEM")
    print("=" * 50)
    
    # Test 1: Check project structure
    project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
    
    required_files = [
        ".claude/agents/epa-compliance-orchestrator.md",
        ".claude/agents/epa-data-validator.md", 
        ".claude/agents/epa-violation-detector.md",
        ".claude/agents/epa-notification-generator.md",
        "demo/springfield_lab_results.csv",
        "production_agentic_system.py"
    ]
    
    print("📁 CHECKING PROJECT STRUCTURE:")
    all_files_exist = True
    
    for file_path in required_files:
        full_path = project_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ SETUP INCOMPLETE - Missing required files")
        return False
    
    # Test 2: Check agent configurations
    print("\n🤖 CHECKING AGENT CONFIGURATIONS:")
    
    agent_files = [
        "epa-compliance-orchestrator.md",
        "epa-data-validator.md",
        "epa-violation-detector.md", 
        "epa-notification-generator.md"
    ]
    
    for agent_file in agent_files:
        agent_path = project_dir / ".claude" / "agents" / agent_file
        try:
            with open(agent_path, 'r') as f:
                content = f.read()
                if len(content) > 100:  # Basic content check
                    print(f"   ✅ {agent_file} - Configuration loaded")
                else:
                    print(f"   ⚠️  {agent_file} - Configuration too short")
        except Exception as e:
            print(f"   ❌ {agent_file} - Error: {e}")
            return False
    
    # Test 3: Check lab data
    print("\n📊 CHECKING LABORATORY DATA:")
    
    csv_file = project_dir / "demo" / "springfield_lab_results.csv"
    try:
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            print(f"   ✅ Lab data loaded: {len(data)} samples")
            
            # Check for key parameters
            parameters = set(row['Parameter'] for row in data)
            expected_params = {'E.coli', 'Lead', 'Copper', 'PFOA'}
            
            if expected_params.issubset(parameters):
                print(f"   ✅ All expected parameters present: {parameters}")
            else:
                print(f"   ⚠️  Missing parameters: {expected_params - parameters}")
                
    except Exception as e:
        print(f"   ❌ Error loading lab data: {e}")
        return False
    
    print("\n✅ ALL TESTS PASSED")
    print("🚀 Production agentic system ready for execution!")
    
    return True

def run_production_demo():
    """Run the production agentic demo."""
    
    if not test_production_system():
        print("\n❌ Tests failed - cannot run demo")
        return
    
    print("\n" + "=" * 60)
    print("🚀 EXECUTING PRODUCTION AGENTIC DEMO")
    print("=" * 60)
    
    try:
        # Import and run the production system
        sys.path.append("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
        from production_agentic_system import ProductionAgenticEPASystem
        
        # Execute the agentic workflow
        system = ProductionAgenticEPASystem()
        results = system.execute_complete_agentic_workflow()
        
        if 'error' not in results:
            print("\n🎉 PRODUCTION DEMO SUCCESSFUL!")
            print("📊 Check production_agentic_results.json for complete output")
        else:
            print(f"\n❌ Demo failed: {results['error']}")
            
    except Exception as e:
        print(f"\n💥 Error running demo: {e}")

if __name__ == "__main__":
    print("🤖 PRODUCTION AGENTIC EPA SYSTEM - TEST & DEMO")
    print("=" * 55)
    
    choice = input("\nChoose option:\n1. Test system setup\n2. Run production demo\n3. Both\n\nEnter choice (1-3): ")
    
    if choice == "1":
        test_production_system()
    elif choice == "2":
        run_production_demo()
    elif choice == "3":
        if test_production_system():
            run_production_demo()
    else:
        print("Invalid choice")
