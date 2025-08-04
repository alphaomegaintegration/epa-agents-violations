#!/usr/bin/env python3
"""
TRUE AGENTIC EPA COMPLIANCE SYSTEM
This script automatically triggers Claude Code agents for fully autonomous compliance analysis
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

class TrueAgenticEPASystem:
    def __init__(self):
        self.project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
        self.results = {}
        
    def execute_agentic_compliance_workflow(self):
        """Execute fully autonomous multi-agent EPA compliance workflow."""
        
        print("🚀 INITIATING TRUE AGENTIC EPA COMPLIANCE WORKFLOW")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project Directory: {self.project_dir}")
        print()
        
        # Change to project directory for Claude Code execution
        os.chdir(self.project_dir)
        
        # Step 1: Trigger EPA Compliance Orchestrator (which should auto-delegate)
        print("🎯 STEP 1: TRIGGERING EPA COMPLIANCE ORCHESTRATOR")
        print("   → This agent should AUTOMATICALLY delegate to all sub-agents")
        print()
        
        # Use the correct Claude Code format - just claude "prompt"
        orchestrator_prompt = "Use epa-compliance-orchestrator to analyze Clinton Machine PWS (OH7700001) laboratory results from demo/springfield_lab_results.csv and execute complete automated EPA compliance workflow with automatic delegation to all specialist agents"
        
        orchestrator_command = ['claude', orchestrator_prompt]
        
        try:
            print("⚡ Executing orchestrator agent...")
            result = subprocess.run(
                orchestrator_command,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_dir
            )
            
            if result.returncode == 0:
                print("✅ ORCHESTRATOR EXECUTED SUCCESSFULLY")
                print("📋 ORCHESTRATOR OUTPUT:")
                print("-" * 40)
                print(result.stdout)
                print("-" * 40)
                self.results['orchestrator'] = {
                    'status': 'success',
                    'output': result.stdout,
                    'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                print("❌ ORCHESTRATOR FAILED")
                print(f"Error: {result.stderr}")
                self.results['orchestrator'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ ORCHESTRATOR TIMED OUT (5 minutes)")
            self.results['orchestrator'] = {
                'status': 'timeout',
                'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"💥 ORCHESTRATOR ERROR: {e}")
            self.results['orchestrator'] = {
                'status': 'error',
                'error': str(e),
                'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # Step 2: Verify autonomous agent execution
        print("\n🔍 STEP 2: VERIFYING AUTONOMOUS EXECUTION")
        self.verify_agentic_outputs()
        
        # Step 3: Save comprehensive results
        print("\n💾 STEP 3: SAVING AGENTIC EXECUTION RESULTS")
        self.save_agentic_results()
        
        return self.results
    
    def verify_agentic_outputs(self):
        """Verify that agents actually executed and produced outputs."""
        
        expected_outputs = [
            'compliance_report.json',
            'public_notifications.json'
        ]
        
        print("   Checking for agent-generated outputs:")
        
        for output_file in expected_outputs:
            file_path = self.project_dir / output_file
            if file_path.exists():
                # Check if file was recently modified (within last 5 minutes)
                file_mtime = file_path.stat().st_mtime
                current_time = datetime.now().timestamp()
                
                if (current_time - file_mtime) < 300:  # 5 minutes
                    print(f"   ✅ {output_file} - Recently updated by agents")
                    self.results[f'{output_file}_status'] = 'updated_by_agents'
                else:
                    print(f"   ⚠️  {output_file} - Exists but not recently updated")
                    self.results[f'{output_file}_status'] = 'stale'
            else:
                print(f"   ❌ {output_file} - Not found")
                self.results[f'{output_file}_status'] = 'missing'
    
    def save_agentic_results(self):
        """Save the complete agentic execution results."""
        
        results_file = self.project_dir / 'agentic_execution_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"   ✅ Results saved to: {results_file}")
        
        # Also create a summary report
        summary_file = self.project_dir / 'agentic_execution_summary.txt'
        
        with open(summary_file, 'w') as f:
            f.write("AGENTIC EPA COMPLIANCE EXECUTION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Project: EPA Compliance Multi-Agent System\n")
            f.write(f"System: Clinton Machine PWS (OH7700001)\n\n")
            
            f.write("ORCHESTRATOR EXECUTION:\n")
            f.write(f"Status: {self.results.get('orchestrator', {}).get('status', 'unknown')}\n")
            
            if self.results.get('orchestrator', {}).get('status') == 'success':
                f.write("✅ Orchestrator successfully executed autonomous workflow\n")
            else:
                f.write("❌ Orchestrator failed to execute properly\n")
            
            f.write("\nAGENT OUTPUT VERIFICATION:\n")
            for key, value in self.results.items():
                if key.endswith('_status'):
                    f.write(f"{key}: {value}\n")
            
            f.write(f"\nComplete results available in: agentic_execution_results.json\n")
        
        print(f"   ✅ Summary saved to: {summary_file}")

def main():
    """Execute the true agentic EPA compliance system."""
    
    print("🤖 TRUE AGENTIC EPA COMPLIANCE SYSTEM")
    print("🎯 This system uses ACTUAL Claude Code agents with autonomous delegation")
    print()
    
    # Initialize the agentic system
    agentic_system = TrueAgenticEPASystem()
    
    # Execute the complete agentic workflow
    results = agentic_system.execute_agentic_compliance_workflow()
    
    # Final status report
    print("\n" + "=" * 60)
    print("🏁 AGENTIC EXECUTION COMPLETE")
    print("=" * 60)
    
    if results.get('orchestrator', {}).get('status') == 'success':
        print("✅ SUCCESS: Orchestrator agent executed autonomous workflow")
        print("📊 Check compliance_report.json and public_notifications.json for results")
    else:
        print("❌ FAILURE: Orchestrator agent did not execute properly")
        print("🔧 Check agent configurations and Claude Code setup")
    
    print("\n📋 NEXT STEPS:")
    print("1. Review agentic_execution_results.json for detailed execution logs")
    print("2. Check if agents actually produced updated compliance outputs")
    print("3. Verify true autonomous delegation occurred")
    
    return results

if __name__ == "__main__":
    # Ensure we're in the right environment
    if not Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo/.claude/agents").exists():
        print("❌ ERROR: Claude Code agents not found!")
        print("   Please ensure you're in the correct project directory")
        sys.exit(1)
    
    main()
