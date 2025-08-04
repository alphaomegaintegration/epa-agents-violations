#!/usr/bin/env python3
"""
AGENTIC SYSTEM TEST - Verify True Multi-Agent Behavior
"""

import subprocess
import sys
from pathlib import Path

def test_claude_code_setup():
    """Test if Claude Code is properly set up."""
    print("🔧 TESTING CLAUDE CODE SETUP")
    print("-" * 40)
    
    # Test 1: Check if claude command exists
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Claude Code is installed")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ Claude Code not responding properly")
            return False
    except FileNotFoundError:
        print("❌ Claude Code not installed")
        print("   Install with: pip install claude-dev")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude Code: {e}")
        return False
    
    # Test 2: Check if we're in the right directory
    project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
    if not project_dir.exists():
        print("❌ Project directory not found")
        return False
    
    agents_dir = project_dir / ".claude" / "agents"
    if not agents_dir.exists():
        print("❌ Agents directory not found")
        return False
    
    # Test 3: Check if all agents exist
    required_agents = [
        'epa-compliance-orchestrator.md',
        'epa-data-validator.md', 
        'epa-violation-detector.md',
        'epa-notification-generator.md'
    ]
    
    for agent in required_agents:
        agent_file = agents_dir / agent
        if agent_file.exists():
            print(f"✅ {agent} found")
        else:
            print(f"❌ {agent} missing")
            return False
    
    print("✅ All components ready for agentic execution")
    return True

def test_simple_agent_call():
    """Test a simple agent call to verify basic functionality."""
    print("\n🎯 TESTING SIMPLE AGENT CALL")
    print("-" * 40)
    
    project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
    
    try:
        # Test calling the orchestrator with the correct Claude Code format
        # The correct format is just: claude "prompt"
        result = subprocess.run([
            'claude',
            'Use epa-compliance-orchestrator to provide a brief status report and test agent responsiveness'
        ], 
        capture_output=True, 
        text=True, 
        timeout=30,
        cwd=project_dir
        )
        
        if result.returncode == 0:
            print("✅ Agent call successful")
            print("📋 Agent Response:")
            print("-" * 20)
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            print("-" * 20)
            return True
        else:
            print("❌ Agent call failed")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Agent call timed out")
        return False
    except Exception as e:
        print(f"💥 Error calling agent: {e}")
        return False

def main():
    """Run all agentic system tests."""
    print("🤖 AGENTIC EPA COMPLIANCE SYSTEM - TESTS")
    print("=" * 50)
    
    # Test 1: Basic setup
    if not test_claude_code_setup():
        print("\n❌ SETUP FAILED - Cannot proceed with agentic execution")
        sys.exit(1)
    
    # Test 2: Simple agent call
    if not test_simple_agent_call():
        print("\n❌ AGENT CALL FAILED - Agents may not be configured correctly")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED")
    print("🚀 Ready for true agentic execution!")
    print("\nRun: python3 agentic_compliance_analysis.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
