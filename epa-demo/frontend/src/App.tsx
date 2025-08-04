import React, { useState, useEffect, useRef } from 'react';
import QuestionInput from './components/QuestionInput';
import AgentPanel from './components/AgentPanel';
import ResultsPanel from './components/ResultsPanel';
import { AnalysisState, AgentUpdate, AnalysisResults } from './types';

const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

function App() {
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    isAnalyzing: false,
    currentQuestion: '',
    agents: {
      epa_data: { status: 'idle', message: '', confidence: 0 },
      violation_data: { status: 'idle', message: '', confidence: 0 },
      'data-validator': { status: 'idle', message: '', confidence: 0, risk_assessment: '' },
      'violation-analyst': { status: 'idle', message: '', confidence: 0, risk_assessment: '' },
      'notification-specialist': { status: 'idle', message: '', confidence: 0, risk_assessment: '' },
      'remediation-specialist': { status: 'idle', message: '', confidence: 0, risk_assessment: '' },
    },
    results: null,
    naturalResponse: '',
    error: null
  });

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket(WS_URL);
        
        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
        };
        
        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };
        
        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
          // Reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
        
        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'analysis_start':
        setAnalysisState(prev => ({
          ...prev,
          isAnalyzing: true,
          currentQuestion: data.question,
          results: null,
          naturalResponse: '',
          error: null,
          agents: {
            epa_data: { status: 'idle', message: '', confidence: 0 },
            violation_data: { status: 'idle', message: '', confidence: 0 },
            'data-validator': { status: 'idle', message: '', confidence: 0, risk_assessment: '', thinking_stream: '', thinking_preview: '', full_thinking: '', decisions: [], next_actions: [] },
            'violation-analyst': { status: 'idle', message: '', confidence: 0, risk_assessment: '', thinking_stream: '', thinking_preview: '', full_thinking: '', decisions: [], next_actions: [] },
            'notification-specialist': { status: 'idle', message: '', confidence: 0, risk_assessment: '', thinking_stream: '', thinking_preview: '', full_thinking: '', decisions: [], next_actions: [] },
            'remediation-specialist': { status: 'idle', message: '', confidence: 0, risk_assessment: '', thinking_stream: '', thinking_preview: '', full_thinking: '', decisions: [], next_actions: [] },
          }
        }));
        break;

      case 'agent_update':
        setAnalysisState(prev => ({
          ...prev,
          agents: {
            ...prev.agents,
            [data.agent]: {
              status: data.status,
              message: data.message,
              confidence: data.confidence || prev.agents[data.agent]?.confidence || 0,
              risk_assessment: data.risk_assessment || prev.agents[data.agent]?.risk_assessment || '',
              thinking_stream: data.thinking_stream || prev.agents[data.agent]?.thinking_stream || '',
              thinking_preview: data.thinking_preview || prev.agents[data.agent]?.thinking_preview || '',
              full_thinking: data.full_thinking || prev.agents[data.agent]?.full_thinking || '',
              decisions: data.decisions || prev.agents[data.agent]?.decisions || [],
              next_actions: data.next_actions || prev.agents[data.agent]?.next_actions || []
            }
          }
        }));
        break;

      case 'analysis_complete':
        setAnalysisState(prev => ({
          ...prev,
          isAnalyzing: false,
          results: data.results,
          naturalResponse: data.natural_response
        }));
        break;

      case 'error':
        setAnalysisState(prev => ({
          ...prev,
          isAnalyzing: false,
          error: data.message
        }));
        break;

      case 'status':
        // General status updates can be shown in a status bar if needed
        console.log('Status:', data.message);
        break;
    }
  };

  const handleQuestionSubmit = async (question: string) => {
    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Response will come through WebSocket
    } catch (error) {
      setAnalysisState(prev => ({
        ...prev,
        isAnalyzing: false,
        error: `Failed to analyze question: ${error}`
      }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-epa-blue text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold flex items-center">
            <span className="text-4xl mr-3">🏛️</span>
            EPA Intelligent Compliance System
          </h1>
          <p className="text-blue-100 mt-2">Natural Language EPA Water Quality Analysis</p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Question Input */}
        <div className="mb-8">
          <QuestionInput 
            onSubmit={handleQuestionSubmit}
            isAnalyzing={analysisState.isAnalyzing}
          />
        </div>

        {/* Current Question Display */}
        {analysisState.currentQuestion && (
          <div className="mb-6 p-4 bg-blue-50 border-l-4 border-epa-blue rounded">
            <p className="text-sm text-gray-600 mb-1">Current Analysis:</p>
            <p className="text-lg font-medium text-gray-800">{analysisState.currentQuestion}</p>
          </div>
        )}

        {/* Error Display */}
        {analysisState.error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <p className="text-red-700">❌ {analysisState.error}</p>
          </div>
        )}

        {/* Agent Panels */}
        {(analysisState.isAnalyzing || analysisState.results) && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">🤖 EPA Agents Analysis</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              <AgentPanel 
                title="🌐 EPA Data"
                agent={analysisState.agents.epa_data}
                color="blue"
              />
              <AgentPanel 
                title="📊 Violation Data"
                agent={analysisState.agents.violation_data}
                color="yellow"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <AgentPanel 
                title="🔍 Data Validator"
                agent={analysisState.agents['data-validator']}
                color="green"
                showRisk={true}
              />
              <AgentPanel 
                title="🚨 Violation Analyst"
                agent={analysisState.agents['violation-analyst']}
                color="red"
                showRisk={true}
              />
              <AgentPanel 
                title="📢 Notification Specialist"
                agent={analysisState.agents['notification-specialist']}
                color="purple"
                showRisk={true}
              />
              <AgentPanel 
                title="🔧 Remediation Specialist"
                agent={analysisState.agents['remediation-specialist']}
                color="blue"
                showRisk={true}
              />
            </div>
          </div>
        )}

        {/* Results */}
        {analysisState.results && (
          <ResultsPanel 
            results={analysisState.results}
            naturalResponse={analysisState.naturalResponse}
            question={analysisState.currentQuestion}
          />
        )}

        {/* Footer */}
        <footer className="mt-12 py-6 border-t border-gray-200 text-center text-gray-600">
          <p>EPA Intelligent Compliance System • Powered by AI Agents • Real EPA Data Integration</p>
        </footer>
      </div>
    </div>
  );
}

export default App;