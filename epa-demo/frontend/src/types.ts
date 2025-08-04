export interface AgentState {
  status: 'idle' | 'running' | 'thinking' | 'complete' | 'error';
  message: string;
  confidence: number;
  risk_assessment?: string;
  thinking_stream?: string;
  thinking_preview?: string;
  full_thinking?: string;
  decisions?: string[];
  next_actions?: string[];
}

export interface AnalysisState {
  isAnalyzing: boolean;
  currentQuestion: string;
  agents: {
    epa_data: AgentState;
    violation_data: AgentState;
    'data-validator': AgentState;
    'violation-analyst': AgentState;
    'notification-specialist': AgentState;
  };
  results: AnalysisResults | null;
  naturalResponse: string;
  error: string | null;
}

export interface AgentUpdate {
  agent: string;
  status: string;
  message: string;
  confidence?: number;
  risk_assessment?: string;
}

export interface WaterSystem {
  name: string;
  pwsid: string;
  population: number;
  status: string;
  location: string;
}

export interface ViolationSummary {
  total: number;
  critical: number;
  parameters: string[];
}

export interface AIAssessment {
  overall_risk: string;
  confidence: number;
}

export interface AnalysisResults {
  epa_data: any;
  violations: any[];
  agent_intelligence: any;
  summary: {
    water_system: WaterSystem;
    violations: ViolationSummary;
    ai_assessment: AIAssessment;
  };
}