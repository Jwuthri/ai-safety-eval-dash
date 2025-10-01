'use client';

import React, { useState } from 'react';

interface Safeguard {
  id: string;
  name: string;
  category: string;
  description: string;
  why_it_works?: string;
  implementation_type: string;
  implementation_details?: {
    code_example?: string;
    config?: any;
    techniques?: string[];
    thresholds?: any;
    triggers?: any;
    limits?: any;
    tools?: string[];
    common_constraints?: any;
  };
  aiuc_requirement?: string;
  compliance_level?: string;
  effectiveness_rating?: string;
  reduces_severity?: string[];
  detection_method?: string;
  automated_response?: string;
  priority?: string;
  effectiveness_note?: string;
}

interface SafeguardCardProps {
  safeguard: Safeguard;
  showCode?: boolean;
}

export function SafeguardCard({ safeguard, showCode = true }: SafeguardCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'hallucination_prevention': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      'prompt_injection_defense': 'bg-red-500/20 text-red-300 border-red-500/30',
      'transaction_validation': 'bg-green-500/20 text-green-300 border-green-500/30',
      'content_policy_enforcement': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      'escalation_workflow': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      'abuse_prevention': 'bg-pink-500/20 text-pink-300 border-pink-500/30',
    };
    return colors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  };

  const getPriorityColor = (priority?: string) => {
    const colors: Record<string, string> = {
      'critical': 'text-red-400 font-bold',
      'high': 'text-orange-400 font-semibold',
      'medium': 'text-yellow-400',
      'low': 'text-gray-400',
    };
    return colors[priority || 'medium'] || 'text-gray-400';
  };

  return (
    <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-purple-500/20 rounded-lg p-6 hover:border-purple-400/40 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-white">{safeguard.name}</h3>
            {safeguard.priority && (
              <span className={`text-xs font-bold uppercase ${getPriorityColor(safeguard.priority)}`}>
                {safeguard.priority}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(safeguard.category)}`}>
              {safeguard.category.replace(/_/g, ' ').toUpperCase()}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-700/50 text-gray-300">
              {safeguard.implementation_type.replace(/_/g, ' ')}
            </span>
            {safeguard.effectiveness_rating && (
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-300">
                {safeguard.effectiveness_rating} effectiveness
              </span>
            )}
          </div>

          <p className="text-gray-300 leading-relaxed">{safeguard.description}</p>
          
          {safeguard.effectiveness_note && (
            <div className="mt-2 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <p className="text-sm text-blue-200">
                <span className="font-semibold">Why this works:</span> {safeguard.effectiveness_note}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Details Section */}
      {safeguard.why_it_works && (
        <div className="mt-4 p-4 bg-gray-700/30 rounded-lg">
          <h4 className="text-sm font-semibold text-purple-300 mb-2">💡 How It Works</h4>
          <p className="text-sm text-gray-300 leading-relaxed">{safeguard.why_it_works}</p>
        </div>
      )}

      {/* Reduces Severity */}
      {safeguard.reduces_severity && safeguard.reduces_severity.length > 0 && (
        <div className="mt-3 flex items-center gap-2">
          <span className="text-sm text-gray-400">Prevents:</span>
          <div className="flex gap-2">
            {safeguard.reduces_severity.map((sev) => (
              <span key={sev} className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs font-mono">
                {sev}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Code Implementation - Expandable */}
      {showCode && safeguard.implementation_details?.code_example && (
        <div className="mt-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-sm font-semibold text-purple-400 hover:text-purple-300 transition-colors"
          >
            <span>{isExpanded ? '▼' : '▶'}</span>
            <span>View Implementation Code</span>
          </button>
          
          {isExpanded && (
            <div className="mt-3 bg-black/40 border border-gray-700 rounded-lg overflow-hidden">
              <div className="bg-gray-800/50 px-4 py-2 border-b border-gray-700">
                <span className="text-xs text-gray-400 font-mono">Python Implementation</span>
              </div>
              <pre className="p-4 overflow-x-auto text-sm">
                <code className="text-green-300 font-mono leading-relaxed">
                  {safeguard.implementation_details.code_example}
                </code>
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Detection & Response */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        {safeguard.detection_method && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <h4 className="text-xs font-semibold text-yellow-300 mb-1">🔍 Detection</h4>
            <p className="text-xs text-gray-300">{safeguard.detection_method}</p>
          </div>
        )}
        
        {safeguard.automated_response && (
          <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <h4 className="text-xs font-semibold text-orange-300 mb-1">⚡ Automated Response</h4>
            <p className="text-xs text-gray-300">{safeguard.automated_response}</p>
          </div>
        )}
      </div>

      {/* AIUC Compliance */}
      {safeguard.aiuc_requirement && (
        <div className="mt-4 flex items-center gap-2 text-xs">
          <span className="px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded font-mono">
            {safeguard.aiuc_requirement}
          </span>
          <span className="text-gray-400">AIUC-1 Compliance</span>
          {safeguard.compliance_level && (
            <span className={`px-2 py-1 rounded ${
              safeguard.compliance_level === 'required' ? 'bg-red-500/20 text-red-300' : 'bg-blue-500/20 text-blue-300'
            }`}>
              {safeguard.compliance_level}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

