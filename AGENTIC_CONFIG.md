# EPA Compliance Multi-Agent System Configuration

## Agent Execution Order
1. epa-compliance-orchestrator (Planning Pattern)
2. epa-data-validator (Tool Use Pattern)  
3. epa-violation-detector (ReAct Pattern)
4. epa-notification-generator (Tool Use + Reflection Pattern)

## Auto-Delegation Commands
The orchestrator should automatically execute these commands:

### Step 1: Data Validation
```
Use epa-data-validator to validate Clinton Machine PWS (OH7700001) laboratory data from demo/springfield_lab_results.csv against EPA quality standards
```

### Step 2: Violation Detection  
```
Use epa-violation-detector to analyze the validated Clinton Machine PWS data for EPA regulatory violations using ReAct reasoning
```

### Step 3: Notification Generation
```
Use epa-notification-generator to create EPA-compliant public health notifications for all detected violations
```

## Expected Agent Behaviors

### Orchestrator
- MUST automatically call other agents in sequence
- MUST pass context between agents
- MUST synthesize final comprehensive report
- MUST NOT do analysis work itself

### Data Validator
- MUST make real EPA API call to verify OH7700001
- MUST validate lab certification and data quality
- MUST return structured validation results

### Violation Detector
- MUST use ReAct pattern (Reason → Act → Reflect)
- MUST detect E.coli, Lead, Copper, PFOA violations
- MUST classify as Tier 1, 2, or 3 violations

### Notification Generator
- MUST generate EPA-compliant notifications
- MUST use proper templates for each violation type
- MUST include all required regulatory elements

## True Agentic Indicators
- Agents call each other without human intervention
- Context flows seamlessly between agents
- Final output shows complete audit trail
- No manual steps required after initial trigger
