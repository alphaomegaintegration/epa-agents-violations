import React, { useState } from 'react';
import { AnalysisResults } from '../types';
import MapVisualization from './MapVisualization';

interface ResultsPanelProps {
  results: AnalysisResults;
  naturalResponse: string;
  question: string;
  onNewQuestion?: (question: string) => void;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results, naturalResponse, question, onNewQuestion }) => {
  const [activeTab, setActiveTab] = useState<'briefing' | 'summary' | 'details' | 'geographic' | 'raw'>('briefing');
  
  const { summary } = results;
  
  // Handle both old and new summary structures
  const isNewStructure = summary && 'executive_summary' in summary;
  
  let water_system, violations, ai_assessment;
  
  if (isNewStructure) {
    // New direct briefing structure
    water_system = {
      name: summary.system_information?.name || 'Unknown',
      pwsid: summary.system_information?.pwsid || 'Unknown',
      location: summary.system_information?.location || 'Unknown',
      status: summary.system_information?.system_type || 'Unknown',
      population: parseInt(summary.executive_summary?.population_affected?.replace(/[^\d]/g, '') || '0')
    };
    
    violations = {
      total: summary.violation_details?.by_tier?.tier_1 + summary.violation_details?.by_tier?.tier_2 || 0,
      critical: summary.violation_details?.by_severity?.critical || 0,
      parameters: summary.violation_details?.parameters_affected || []
    };
    
    ai_assessment = {
      overall_risk: summary.executive_summary?.overall_risk?.toLowerCase() || 'unknown',
      confidence: parseFloat(summary.executive_summary?.confidence_level?.replace('%', '') || '0') / 100
    };
  } else {
    // Legacy structure fallback
    water_system = summary.water_system || {};
    violations = summary.violations || {};
    ai_assessment = summary.ai_assessment || {};
  }

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-100 border-green-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const downloadResults = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `epa-analysis-${water_system.pwsid}-${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Natural Language Response */}
      <div className="bg-gradient-to-r from-epa-blue to-blue-600 text-white p-6">
        <div className="flex items-start gap-4">
          <div className="text-3xl">🤖</div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold mb-2">EPA Agent Analysis Complete</h2>
            <p className="text-blue-100 text-lg leading-relaxed">{naturalResponse}</p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex">
          {[
            { id: 'briefing', label: '🏛️ Intel Briefing', icon: '🏛️' },
            { id: 'summary', label: '📊 Summary', icon: '📊' },
            { id: 'details', label: '🔍 Details', icon: '🔍' },
            { id: 'geographic', label: '🗺️ Geographic', icon: '🗺️' },
            { id: 'raw', label: '📄 Raw Data', icon: '📄' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-epa-blue text-epa-blue bg-blue-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'briefing' && isNewStructure && (
          <div className="space-y-6">
            {/* Executive Summary */}
            <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-red-800 mb-4">🚨 EXECUTIVE SUMMARY</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg p-4 border border-red-300 text-center">
                  <div className="text-2xl font-bold text-red-600">{summary.executive_summary?.overall_risk}</div>
                  <div className="text-sm text-red-800">Overall Risk</div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-300 text-center">
                  <div className="text-2xl font-bold text-orange-600">{summary.executive_summary?.population_affected}</div>
                  <div className="text-sm text-orange-800">Population Affected</div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-300 text-center">
                  <div className="text-2xl font-bold text-blue-600">{summary.executive_summary?.confidence_level}</div>
                  <div className="text-sm text-blue-800">AI Confidence</div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-300 text-center">
                  <div className="text-2xl font-bold text-purple-600">{summary.executive_summary?.immediate_action_required ? '🔴 YES' : '🟢 NO'}</div>
                  <div className="text-sm text-purple-800">Action Required</div>
                </div>
              </div>
              <div className="mt-4 bg-white rounded-lg p-4 border border-red-300">
                <p className="text-gray-800 font-medium">{summary.executive_summary?.violations_summary}</p>
              </div>
            </div>

            {/* Key Findings */}
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-blue-800 mb-4">🎯 KEY FINDINGS</h3>
              <div className="space-y-2">
                {summary.key_findings?.map((finding: string, index: number) => (
                  <div key={index} className="bg-white rounded-lg p-3 border border-blue-300">
                    <p className="text-sm text-gray-800">• {finding}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Immediate Actions */}
            <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-green-800 mb-4">⚡ IMMEDIATE ACTIONS</h3>
              <div className="space-y-2">
                {summary.immediate_actions?.map((action: string, index: number) => (
                  <div key={index} className="bg-white rounded-lg p-3 border border-green-300">
                    <p className="text-sm text-gray-800">▶ {action}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Agent Assessments */}
            <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-purple-800 mb-4">🤖 AGENT ASSESSMENTS</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {summary.agent_assessments?.map((assessment: any, index: number) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-purple-300">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-800">{assessment.agent}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(assessment.risk)}`}>
                        {assessment.risk}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mb-2">Confidence: {assessment.confidence}</div>
                    <div className="text-xs text-gray-700">
                      <strong>Top Decision:</strong> {assessment.decisions?.[0] || 'No decisions recorded'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* EPA Resources */}
            {summary.epa_resources?.serpapi_enhanced && (
              <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-yellow-800 mb-4">📄 EPA RESOURCES FOUND</h3>
                <div className="mb-3">
                  <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    ✅ SerpAPI Enhanced - {summary.epa_resources.total_resources} resources found
                  </span>
                </div>
                <div className="space-y-2">
                  {summary.epa_resources?.guidance_documents?.map((resource: string, index: number) => (
                    <div key={index} className="bg-white rounded-lg p-3 border border-yellow-300">
                      <p className="text-sm text-gray-800">📄 {resource}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* System Information */}
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">🏛️ SYSTEM INFORMATION</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2 text-sm">
                  <div><strong>System Name:</strong> {summary.system_information?.name}</div>
                  <div><strong>PWSID:</strong> {summary.system_information?.pwsid}</div>
                  <div><strong>Location:</strong> {summary.system_information?.location}</div>
                  <div><strong>EPA Region:</strong> {summary.system_information?.epa_region}</div>
                </div>
                <div className="space-y-2 text-sm">
                  <div><strong>Water Source:</strong> {summary.system_information?.water_source}</div>
                  <div><strong>System Type:</strong> {summary.system_information?.system_type}</div>
                  <div><strong>Service Connections:</strong> {summary.system_information?.service_connections}</div>
                </div>
              </div>
            </div>

            {/* Metadata */}
            <div className="bg-gray-100 rounded-lg p-4 text-xs text-gray-600">
              <strong>Report Metadata:</strong> Generated at {new Date(summary.metadata?.generated_at).toLocaleString()} | 
              Agents: {summary.metadata?.agents_analyzed}/4 | 
              Real-time Enhanced: {summary.metadata?.real_time_enhanced ? 'Yes' : 'No'} |
              Data Sources: {summary.metadata?.data_sources?.join(', ')}
            </div>
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="text-2xl font-bold text-blue-600">{violations.total}</div>
                <div className="text-sm text-blue-800">Total Violations</div>
              </div>
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <div className="text-2xl font-bold text-red-600">{violations.critical}</div>
                <div className="text-sm text-red-800">Critical Issues</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="text-2xl font-bold text-green-600">{water_system.population.toLocaleString()}</div>
                <div className="text-sm text-green-800">People Affected</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <div className="text-2xl font-bold text-purple-600">{Math.round(ai_assessment.confidence * 100)}%</div>
                <div className="text-sm text-purple-800">AI Confidence</div>
              </div>
            </div>

            {/* Water System Info */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3">🏛️ Water System Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div><span className="font-medium">System Name:</span> {water_system.name}</div>
                <div><span className="font-medium">PWSID:</span> {water_system.pwsid}</div>
                <div><span className="font-medium">Location:</span> {water_system.location}</div>
                <div><span className="font-medium">Status:</span> {water_system.status}</div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className={`p-4 rounded-lg border-2 ${getRiskColor(ai_assessment.overall_risk)}`}>
              <h3 className="font-semibold mb-2">🎯 AI Risk Assessment</h3>
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold">{ai_assessment.overall_risk.toUpperCase()} RISK</span>
                <span className="text-sm">Confidence: {Math.round(ai_assessment.confidence * 100)}%</span>
              </div>
            </div>

            {/* Violations by Parameter */}
            {violations.parameters.length > 0 && (
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h3 className="font-semibold text-yellow-800 mb-3">🚨 Contaminated Parameters</h3>
                <div className="flex flex-wrap gap-2">
                  {violations.parameters.map((param, index) => (
                    <span key={index} className="px-3 py-1 bg-yellow-200 text-yellow-800 rounded-full text-sm font-medium">
                      {param}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'details' && (
          <div className="space-y-6">
            {/* Individual Violations */}
            {results.violations && results.violations.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-4">🚨 Detailed Violations</h3>
                <div className="space-y-3">
                  {results.violations.map((violation, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-lg">{violation.parameter}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          violation.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {violation.severity}
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div><span className="font-medium">Result:</span> {violation.result}</div>
                        <div><span className="font-medium">MCL:</span> {violation.mcl}</div>
                        <div><span className="font-medium">Location:</span> {violation.sample_location}</div>
                      </div>
                      <div className="mt-2 text-sm text-gray-700">
                        <span className="font-medium">Health Risk:</span> {violation.health_risk}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Agent Intelligence Summary */}
            {results.agent_intelligence && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-4">🧠 Agent Intelligence Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(results.agent_intelligence).map(([agentName, intelligence]: [string, any]) => (
                    <div key={agentName} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-800 mb-2 capitalize">
                        {agentName.replace('_', ' ')}
                      </h4>
                      <div className="space-y-2 text-sm">
                        {intelligence.risk_assessment && (
                          <div className={`px-2 py-1 rounded text-xs ${getRiskColor(intelligence.risk_assessment)}`}>
                            Risk: {intelligence.risk_assessment.toUpperCase()}
                          </div>
                        )}
                        {intelligence.confidence && (
                          <div>Confidence: {Math.round(intelligence.confidence * 100)}%</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'geographic' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-800">🗺️ Geographic Visualization</h3>
              <div className="text-sm text-gray-600">
                Click markers to analyze different water systems
              </div>
            </div>
            
            <MapVisualization
              results={results}
              selectedSystem={results?.epa_data?.pwsid}
              onSystemClick={(pwsid, systemName) => {
                if (onNewQuestion) {
                  const question = `What EPA violations does ${systemName} have?`;
                  onNewQuestion(question);
                }
              }}
            />
            
            <div className="bg-blue-50 border-l-4 border-epa-blue p-4 rounded">
              <div className="flex">
                <div className="text-epa-blue text-lg mr-3">ℹ️</div>
                <div>
                  <h4 className="font-medium text-epa-blue mb-1">Interactive EPA System Map</h4>
                  <p className="text-sm text-gray-700">
                    This map shows the 6 major water systems in our database. Circle sizes represent population served, 
                    colors indicate risk levels based on EPA violations and enforcement actions. 
                    Click any system marker to analyze its compliance status.
                  </p>
                  <div className="mt-2 text-xs text-gray-600">
                    <strong>Systems Available:</strong> Los Angeles (3.9M), Houston (2.2M), Miami-Dade (2.3M), 
                    Cleveland (1.3M), San Diego (1.4M), Clinton Machine (76)
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'raw' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-800">📄 Raw Analysis Data</h3>
              <button
                onClick={downloadResults}
                className="px-4 py-2 bg-epa-blue text-white rounded hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                📥 Download JSON
              </button>
            </div>
            <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-auto max-h-96 border">
              {JSON.stringify(results, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;