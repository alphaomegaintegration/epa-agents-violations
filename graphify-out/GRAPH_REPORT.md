# Graph Report - epa-agents-violations  (2026-10-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 651 nodes · 951 edges · 29 communities (18 shown, 11 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0cc3eefa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- main.py
- HeatMapLayer.tsx
- RealViolationDataLoader
- backend/chart/values.yaml
- frontend/chart/values.yaml
- sys
- package.json
- ProductionAgenticEPASystem
- EPA Intelligent Compliance System
- backend
- TrueAgenticEPASystem
- EPA Intelligent Compliance System - Production Deployment Guide
- backend
- test_epa_api.py
- main
- 🏛️ Natural Language EPA Water Quality Analysis
- EPAECHOValidator
- EPA Compliance Multi-Agent System Configuration
- FixedAgenticEPASystem
- backend/chart/Chart.yaml
- frontend/chart/Chart.yaml
- vite-env.d.ts

## God Nodes (most connected - your core abstractions)
1. `ProductionAgenticEPASystem` - 17 edges
2. `🏛️ Natural Language EPA Water Quality Analysis` - 15 edges
3. `EPA Intelligent Compliance System` - 15 edges
4. `TrueAgenticEPASystem` - 13 edges
5. `main()` - 11 edges
6. `EPAComplianceAnalyzer` - 10 edges
7. `RealViolationDataLoader` - 10 edges
8. `EPA Intelligent Compliance System - Production Deployment Guide` - 10 edges
9. `EPAECHOTestClient` - 9 edges
10. `EPAECHOValidator` - 9 edges

## Surprising Connections (you probably didn't know these)
- `NaturalLanguageProcessor` --uses--> `IntelligentAgent`  [INFERRED]
  epa-demo/backend/main.py → intelligent_agentic_system.py
- `RealViolationDataLoader` --uses--> `RealViolationData`  [INFERRED]
  epa-demo/backend/main.py → intelligent_agentic_system.py
- `HeatMapLayerProps` --references--> `SystemMarkerData`  [EXTRACTED]
  epa-demo/frontend/src/components/HeatMapLayer.tsx → epa-demo/frontend/src/types/geographic.ts
- `AgentPanelProps` --references--> `AgentState`  [EXTRACTED]
  epa-demo/frontend/src/components/AgentPanel.tsx → epa-demo/frontend/src/types.ts
- `ResultsPanelProps` --references--> `AnalysisResults`  [EXTRACTED]
  epa-demo/frontend/src/components/ResultsPanel.tsx → epa-demo/frontend/src/types.ts

## Import Cycles
- None detected.

## Communities (29 total, 11 thin omitted)

### Community 0 - "json"
Cohesion: 0.06
Nodes (16): analyze_violations(), main(), test_anthropic_api(), EPAAPIDebugger, main(), analyze_system_violations(), fetch_echo_violations(), fetch_sdwis_violations() (+8 more)

### Community 1 - "main.py"
Cohesion: 0.05
Nodes (15): analyze_question(), ConnectionManager, create_specialized_prompt(), create_summary(), generate_natural_response(), health_check(), IntentResponse, list_available_systems() (+7 more)

### Community 2 - "HeatMapLayer.tsx"
Cohesion: 0.08
Nodes (36): leaflet@^1.9.4, react-leaflet@^4.2.1, App(), AgentPanel(), AgentPanelProps, colorClasses, statusIcons, calculateIntensity() (+28 more)

### Community 3 - "RealViolationDataLoader"
Cohesion: 0.06
Nodes (6): RealViolationDataLoader, IntelligentAgent, IntelligentAgenticSystem, main(), RealEPADataSource, RealViolationData

### Community 4 - "backend/chart/values.yaml"
Cohesion: 0.05
Nodes (41): affinity, alb.ingress.kubernetes.io/backend-protocol, alb.ingress.kubernetes.io/listen-ports, alb.ingress.kubernetes.io/load-balancer-attributes, alb.ingress.kubernetes.io/scheme, alb.ingress.kubernetes.io/target-type, kubernetes.io/ingress.class, aws_iam_role_arn (+33 more)

### Community 5 - "frontend/chart/values.yaml"
Cohesion: 0.06
Nodes (35): alb.ingress.kubernetes.io/backend-protocol, alb.ingress.kubernetes.io/listen-ports, alb.ingress.kubernetes.io/scheme, alb.ingress.kubernetes.io/target-type, kubernetes.io/ingress.class, env, VITE_API_BASE, VITE_WS_URL (+27 more)

### Community 6 - "sys"
Cohesion: 0.09
Nodes (8): main(), TrueAgenticEPASystem, test_claude_agents_list(), test_claude_help(), test_simple_claude_call(), main(), test_claude_code_setup(), test_simple_agent_call()

### Community 7 - "package.json"
Cohesion: 0.08
Nodes (32): dependencies, autoprefixer@^10.4.16, leaflet.heat@^0.2.0, postcss@^8.4.31, react@^18.2.0, react-dom@^18.2.0, tailwindcss@^3.3.0, @types/leaflet@^1.9.8 (+24 more)

### Community 8 - "ProductionAgenticEPASystem"
Cohesion: 0.11
Nodes (4): main(), ProductionAgenticEPASystem, run_production_demo(), test_production_system()

### Community 9 - "EPA Intelligent Compliance System"
Cohesion: 0.07
Nodes (30): AI Agents, AI & Data, 🔧 Architecture, AWS EC2 / Production Server Deployment, Backend, Compliance Analysis, 🤝 Contributing, Current EPA Guidance (+22 more)

### Community 10 - "backend"
Cohesion: 0.08
Nodes (25): VITE_API_BASE, VITE_WS_URL, build, env_file, healthcheck, ports, restart, volumes (+17 more)

### Community 12 - "EPA Intelligent Compliance System - Production Deployment Guide"
Cohesion: 0.08
Nodes (22): 1. Backend CORS Configuration, 2. Frontend API Configuration, 3. Production Docker Compose, 4. Production Environment File, 🔒 AWS Security Group Configuration, Common Issues:, Debug Commands:, 🔧 Deployment Steps (+14 more)

### Community 13 - "backend"
Cohesion: 0.09
Nodes (23): build, environment, healthcheck, ports, restart, volumes, context, dockerfile (+15 more)

### Community 14 - "test_epa_api.py"
Cohesion: 0.14
Nodes (8): EPAECHOTestClient, format_system_info(), main(), process_springfield_lab_data(), test_api_performance(), test_multiple_pwsids(), test_springfield_scenario(), validate_pwsid_format()

### Community 16 - "🏛️ Natural Language EPA Water Quality Analysis"
Cohesion: 0.11
Nodes (18): 📱 API Endpoints, 🏗️ Architecture, 🔧 Configuration, 🤝 Contributing, 🚢 EC2 Deployment, 🤖 EPA Agents, EPA Intelligent Compliance System, 🎯 Example Questions (+10 more)

### Community 18 - "EPA Compliance Multi-Agent System Configuration"
Cohesion: 0.15
Nodes (12): Agent Execution Order, Auto-Delegation Commands, Data Validator, EPA Compliance Multi-Agent System Configuration, Expected Agent Behaviors, Notification Generator, Orchestrator, Step 1: Data Validation (+4 more)

### Community 20 - "backend/chart/Chart.yaml"
Cohesion: 0.33
Nodes (5): apiVersion, appVersion, description, name, version

### Community 21 - "frontend/chart/Chart.yaml"
Cohesion: 0.33
Nodes (5): apiVersion, appVersion, description, name, version

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProductionAgenticEPASystem` connect `ProductionAgenticEPASystem` to `json`, `sys`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.055130784708249496 - nodes in this community are weakly interconnected._
- **Why does `TrueAgenticEPASystem` connect `TrueAgenticEPASystem` to `json`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053109713487071976 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `main` to `json`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `HeatMapLayer.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07955596669750231 - nodes in this community are weakly interconnected._
- **Should `RealViolationDataLoader` be split into smaller, more focused modules?**
  _Cohesion score 0.0647342995169082 - nodes in this community are weakly interconnected._