import React, { useState } from 'react';
import { AgentState } from '../types';

interface AgentPanelProps {
  title: string;
  agent: AgentState;
  color: 'blue' | 'green' | 'red' | 'yellow' | 'purple';
  showRisk?: boolean;
}

const colorClasses = {
  blue: {
    border: 'border-blue-200',
    bg: 'bg-blue-50',
    text: 'text-blue-800',
    accent: 'bg-blue-500'
  },
  green: {
    border: 'border-green-200',
    bg: 'bg-green-50',
    text: 'text-green-800',
    accent: 'bg-green-500'
  },
  red: {
    border: 'border-red-200',
    bg: 'bg-red-50',
    text: 'text-red-800',
    accent: 'bg-red-500'
  },
  yellow: {
    border: 'border-yellow-200',
    bg: 'bg-yellow-50',
    text: 'text-yellow-800',
    accent: 'bg-yellow-500'
  },
  purple: {
    border: 'border-purple-200',
    bg: 'bg-purple-50',
    text: 'text-purple-800',
    accent: 'bg-purple-500'
  }
};

const statusIcons = {
  idle: '⚪',
  running: '🔄',
  thinking: '🤔',
  complete: '✅',
  error: '❌'
};

const AgentPanel: React.FC<AgentPanelProps> = ({ title, agent, color, showRisk = false }) => {
  const [expanded, setExpanded] = useState(false);
  const colors = colorClasses[color];
  const isActive = agent.status === 'running' || agent.status === 'thinking';
  
  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const hasThinking = agent.thinking_preview || agent.full_thinking || agent.thinking_stream;
  const hasActions = agent.decisions?.length > 0 || agent.next_actions?.length > 0;

  return (
    <div className={`border-2 ${colors.border} ${colors.bg} rounded-lg p-4 transition-all duration-300 ${isActive ? 'shadow-lg scale-105' : 'shadow-sm'}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className={`font-semibold ${colors.text}`}>{title}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xl">{statusIcons[agent.status]}</span>
          {hasThinking && agent.status === 'complete' && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded transition-colors"
            >
              {expanded ? '🔼 Hide' : '🔽 Think'}
            </button>
          )}
        </div>
      </div>
      
      <div className="space-y-2">
        {/* Status Message */}
        <p className="text-sm text-gray-700 min-h-[2.5rem]">
          {agent.message || 'Waiting...'}
        </p>
        
        {/* Thinking Stream (for active agents) */}
        {isActive && agent.thinking_stream && (
          <div className="bg-gray-100 p-2 rounded text-xs text-gray-600 italic animate-pulse">
            💭 {agent.thinking_stream}
          </div>
        )}
        
        {/* Show temporary thinking preview even during analysis */}
        {isActive && agent.thinking_preview && (
          <div className="bg-blue-50 p-2 rounded text-xs text-blue-700 border-l-2 border-blue-300">
            🧠 Thinking: {agent.thinking_preview.substring(0, 200)}...
          </div>
        )}
        
        {/* Progress Bar */}
        {isActive && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className={`h-2 rounded-full ${colors.accent} animate-pulse`} style={{width: '60%'}}></div>
          </div>
        )}
        
        {/* Expanded Thinking (for completed agents) */}
        {expanded && agent.status === 'complete' && (
          <div className="mt-3 p-3 bg-white rounded border-l-4 border-gray-300 space-y-2">
            {agent.thinking_preview && (
              <div>
                <h4 className="text-xs font-semibold text-gray-700 mb-1">🧠 Agent Reasoning:</h4>
                <p className="text-xs text-gray-600 leading-relaxed">
                  {agent.thinking_preview}
                </p>
              </div>
            )}
            
            {agent.decisions && agent.decisions.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-gray-700 mb-1">⚖️ Decisions:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  {agent.decisions.map((decision, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span className="text-blue-500">•</span>
                      <span>{decision}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {agent.next_actions && agent.next_actions.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-gray-700 mb-1">⚡ Next Actions:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  {agent.next_actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span className="text-green-500">▶</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {/* Confidence and Risk */}
        {agent.status === 'complete' && (
          <div className="flex items-center justify-between text-xs">
            {agent.confidence > 0 && (
              <span className="flex items-center gap-1">
                🎯 <span className="font-medium">{Math.round(agent.confidence * 100)}%</span>
              </span>
            )}
            
            {showRisk && agent.risk_assessment && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(agent.risk_assessment)}`}>
                {agent.risk_assessment.toUpperCase()}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentPanel;