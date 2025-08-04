#!/usr/bin/env python3
"""
Quick Claude Code Format Test
"""

import subprocess
from pathlib import Path

def test_claude_help():
    """Check Claude Code help to understand the correct syntax."""
    print("🔍 CHECKING CLAUDE CODE COMMAND FORMAT")
    print("-" * 50)
    
    try:
        # Check help
        result = subprocess.run(['claude', '--help'], capture_output=True, text=True, timeout=10)
        print("📋 Claude Code Help Output:")
        print(result.stdout)
        print("\n" + "="*50)
        
        if result.stderr:
            print("Error output:")
            print(result.stderr)
        
    except Exception as e:
        print(f"Error: {e}")

def test_claude_agents_list():
    """Try to list available agents."""
    print("\n🤖 CHECKING AVAILABLE AGENTS")
    print("-" * 50)
    
    project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
    
    try:
        # Try to list agents or get status
        result = subprocess.run(['claude', 'list agents'], capture_output=True, text=True, timeout=10, cwd=project_dir)
        
        print("📋 Agents List Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Error output:")
            print(result.stderr)
        
    except Exception as e:
        print(f"Error: {e}")

def test_simple_claude_call():
    """Test the simplest possible Claude call."""
    print("\n🎯 TESTING SIMPLE CLAUDE CALL")
    print("-" * 50)
    
    project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
    
    try:
        # Simplest test
        result = subprocess.run(['claude', 'Hello, test the system'], capture_output=True, text=True, timeout=30, cwd=project_dir)
        
        print(f"Return code: {result.returncode}")
        print("📋 Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Error output:") 
            print(result.stderr)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_claude_help()
    test_claude_agents_list() 
    test_simple_claude_call()
