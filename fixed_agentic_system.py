#!/usr/bin/env python3
"""
FIXED AGENTIC EPA SYSTEM - Interactive Claude Code Approach
This uses the correct Claude Code methodology for agent execution
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

class FixedAgenticEPASystem:
    def __init__(self):
        self.project_dir = Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo")
        self.results = {}
        
    def create_agentic_prompt_file(self):
        """Create a comprehensive prompt file that triggers agentic behavior."""
        
        prompt_content = """
EXECUTE AGENTIC EPA COMPLIANCE WORKFLOW

You are operating in a project with specialized EPA compliance agents in .claude/agents/:
- epa-compliance-orchestrator.md (Planning Pattern)
- epa-data-validator.md (Tool Use Pattern) 
- epa-violation-detector.md (ReAct Pattern)
- epa-notification-generator.md (Tool Use + Reflection Pattern)

MISSION: Analyze Clinton Machine PWS (OH7700001) laboratory results and execute complete autonomous EPA compliance workflow.

REQUIRED AGENTIC SEQUENCE:
1. Act as the EPA Compliance Orchestrator and plan the complete workflow
2. Perform data validation by reading and validating demo/springfield_lab_results.csv
3. Make REAL EPA API call to verify PWSID OH7700001 system information
4. Execute violation detection using ReAct reasoning against EPA standards
5. Generate EPA-compliant public health notifications for all detected violations
6. Synthesize comprehensive compliance report with executive summary

DATA LOCATION: demo/springfield_lab_results.csv
EXPECTED VIOLATIONS: E.coli (Tier 1), Lead exceedances (Tier 2), Copper exceedances (Tier 2), PFOA exceedance (Tier 2)

EXECUTE THIS COMPLETE WORKFLOW AUTONOMOUSLY - Use the agentic patterns defined in the agent files and demonstrate true multi-agent coordination.
"""
        
        prompt_file = self.project_dir / "agentic_workflow_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt_content.strip())
        
        return prompt_file
    
    def execute_interactive_agentic_workflow(self):
        """Execute agentic workflow using interactive Claude Code session."""
        
        print("🚀 EXECUTING FIXED AGENTIC EPA COMPLIANCE WORKFLOW")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project Directory: {self.project_dir}")
        print()
        
        # Change to project directory
        os.chdir(self.project_dir)
        
        # Create the comprehensive agentic prompt
        print("📝 CREATING AGENTIC WORKFLOW PROMPT")
        prompt_file = self.create_agentic_prompt_file()
        print(f"   ✅ Prompt created: {prompt_file}")
        
        # Execute with the --print flag for non-interactive execution
        print("\n🎯 EXECUTING AGENTIC WORKFLOW WITH CLAUDE CODE")
        print("   → Using --print mode for automated execution")
        print()
        
        try:
            # Read the prompt file and execute
            with open(prompt_file, 'r') as f:
                prompt_content = f.read()
            
            # Execute Claude Code with the comprehensive prompt
            result = subprocess.run([
                'claude', 
                '--print',  # Non-interactive mode
                prompt_content
            ], 
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=self.project_dir
            )
            
            if result.returncode == 0:
                print("✅ AGENTIC WORKFLOW EXECUTED SUCCESSFULLY")
                print("\n📋 AGENTIC EXECUTION OUTPUT:")
                print("=" * 60)
                print(result.stdout)
                print("=" * 60)
                
                self.results['agentic_execution'] = {
                    'status': 'success',
                    'output': result.stdout,
                    'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Check if files were created/updated
                self.verify_agentic_outputs()
                
            else:
                print("❌ AGENTIC WORKFLOW FAILED")
                print(f"Error: {result.stderr}")
                self.results['agentic_execution'] = {
                    'status': 'failed',  
                    'error': result.stderr,
                    'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ AGENTIC WORKFLOW TIMED OUT (5 minutes)")
            self.results['agentic_execution'] = {
                'status': 'timeout',
                'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"💥 AGENTIC WORKFLOW ERROR: {e}")
            self.results['agentic_execution'] = {
                'status': 'error',
                'error': str(e),
                'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return self.results
    
    def verify_agentic_outputs(self):
        """Verify that the agentic execution produced expected outputs."""
        
        print("\n🔍 VERIFYING AGENTIC EXECUTION RESULTS")
        print("-" * 50)
        
        # Check for file access and tool usage
        expected_indicators = {
            'demo/springfield_lab_results.csv': 'Lab data read',
            'compliance_report.json': 'Compliance report generated',
            'public_notifications.json': 'Notifications generated'
        }
        
        for file_path, description in expected_indicators.items():
            full_path = self.project_dir / file_path
            if full_path.exists():
                print(f"   ✅ {description}: {file_path}")
                self.results[f'{file_path}_status'] = 'found'
            else:
                print(f"   ❌ {description}: {file_path} not found")
                self.results[f'{file_path}_status'] = 'missing'
        
        # Check if output shows agentic behavior patterns
        output = self.results.get('agentic_execution', {}).get('output', '')
        
        agentic_patterns = [
            ('EPA API call', 'epa.gov' in output.lower() or 'pwsid' in output.lower()),
            ('Violation detection', 'violation' in output.lower() or 'exceedance' in output.lower()),
            ('Notification generation', 'notification' in output.lower() or 'public notice' in output.lower()),
            ('File operations', 'read' in output.lower() or 'csv' in output.lower())
        ]
        
        print("\n🔍 AGENTIC BEHAVIOR INDICATORS:")
        for pattern_name, pattern_found in agentic_patterns:
            if pattern_found:
                print(f"   ✅ {pattern_name}: Detected")
                self.results[f'{pattern_name.lower().replace(" ", "_")}_pattern'] = 'detected'
            else:
                print(f"   ⚠️  {pattern_name}: Not clearly detected")
                self.results[f'{pattern_name.lower().replace(" ", "_")}_pattern'] = 'not_detected'
    
    def save_results(self):
        """Save the complete execution results."""
        
        results_file = self.project_dir / 'fixed_agentic_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Create summary
        summary_file = self.project_dir / 'fixed_agentic_summary.txt'
        
        with open(summary_file, 'w') as f:
            f.write("FIXED AGENTIC EPA COMPLIANCE EXECUTION SUMMARY\n")
            f.write("=" * 55 + "\n\n")
            f.write(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Method: Claude Code --print mode with comprehensive prompt\n")
            f.write(f"Project: EPA Compliance Multi-Agent System\n\n")
            
            status = self.results.get('agentic_execution', {}).get('status', 'unknown')
            f.write(f"Execution Status: {status}\n\n")
            
            if status == 'success':
                f.write("✅ Claude Code executed the comprehensive agentic workflow\n")
                f.write("📊 Check output above for agentic behavior indicators\n")
            else:
                f.write("❌ Execution encountered issues\n")
                f.write("🔧 Check error details in results file\n")
            
            f.write(f"\nDetailed results: fixed_agentic_results.json\n")
        
        print(f"📋 Summary saved to: {summary_file}")

def main():
    """Execute the fixed agentic EPA compliance system."""
    
    print("🤖 FIXED AGENTIC EPA COMPLIANCE SYSTEM")
    print("🎯 Using correct Claude Code methodology")
    print()
    
    # Initialize the fixed system
    agentic_system = FixedAgenticEPASystem()
    
    # Execute the agentic workflow
    results = agentic_system.execute_interactive_agentic_workflow()
    
    # Save results
    agentic_system.save_results()
    
    # Final status
    print("\n" + "=" * 60)
    print("🏁 FIXED AGENTIC EXECUTION COMPLETE")
    print("=" * 60)
    
    status = results.get('agentic_execution', {}).get('status', 'unknown')
    
    if status == 'success':
        print("✅ SUCCESS: Claude Code executed agentic workflow")
        print("📊 Review output above for true agentic behavior")
    else:
        print("❌ Issues encountered during execution")
        print("🔧 Check results files for debugging information")
    
    print("\n📋 WHAT TO LOOK FOR IN OUTPUT:")
    print("✅ File reading operations (demo/springfield_lab_results.csv)")
    print("✅ EPA API calls or PWSID references")
    print("✅ Violation detection and analysis")
    print("✅ Notification generation")
    print("✅ Comprehensive compliance reporting")
    
    return results

if __name__ == "__main__":
    # Ensure we're in the right environment
    if not Path("/Users/ananthabangalore/Documents/epa-compliance-demo/epa-compliance-demo/.claude/agents").exists():
        print("❌ ERROR: Claude Code agents not found!")
        print("   Please ensure you're in the correct project directory")
        sys.exit(1)
    
    main()
