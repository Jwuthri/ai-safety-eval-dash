'use client';

import { AIIncident, SeverityLevel } from '@/types/safety';

interface IncidentCardProps {
  incident: AIIncident;
  showDetails?: boolean;
  onViewDetails?: (incident: AIIncident) => void;
}

export default function IncidentCard({ incident, showDetails = false, onViewDetails }: IncidentCardProps) {
  const severityColors: Record<SeverityLevel, string> = {
    P0: 'from-red-900 to-red-800',
    P1: 'from-red-700 to-red-600',
    P2: 'from-orange-600 to-orange-500',
    P3: 'from-yellow-600 to-yellow-500',
    P4: 'from-yellow-400 to-yellow-300',
    PASS: 'from-green-600 to-green-500',
  };

  const severityBadgeColors: Record<SeverityLevel, string> = {
    P0: 'bg-red-900 text-red-100',
    P1: 'bg-red-600 text-white',
    P2: 'bg-orange-500 text-white',
    P3: 'bg-yellow-500 text-gray-900',
    P4: 'bg-yellow-300 text-gray-900',
    PASS: 'bg-green-500 text-white',
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="group relative rounded-xl bg-gray-900/50 border border-gray-800 hover:border-purple-500/40 transition-all duration-300 overflow-hidden">
      {/* Severity indicator stripe */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${severityColors[incident.severity]}`} />
      
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${severityBadgeColors[incident.severity]}`}>
                {incident.severity}
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-300">
                {incident.harm_type.replace(/_/g, ' ')}
              </span>
            </div>
            <h3 className="text-xl font-semibold text-white group-hover:text-purple-400 transition-colors">
              {incident.incident_name}
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              {incident.company} {incident.date_occurred && `• ${formatDate(incident.date_occurred)}`}
            </p>
          </div>
          
          {/* Impact icon */}
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-600/20 to-blue-600/20 flex items-center justify-center">
            <span className="text-2xl">⚠️</span>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-300 leading-relaxed mb-4">
          {incident.description}
        </p>

        {/* Impact stats */}
        <div className="flex flex-wrap gap-4 mb-4">
          {incident.estimated_cost !== undefined && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800/50">
              <span className="text-xl">💰</span>
              <div>
                <div className="text-xs text-gray-400">Est. Cost</div>
                <div className="text-sm font-semibold text-white">
                  {formatCurrency(incident.estimated_cost)}
                </div>
              </div>
            </div>
          )}
          
          {incident.affected_users !== undefined && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800/50">
              <span className="text-xl">👥</span>
              <div>
                <div className="text-xs text-gray-400">Affected Users</div>
                <div className="text-sm font-semibold text-white">
                  {incident.affected_users.toLocaleString()}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Expandable details */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-gray-800">
            {incident.root_cause && (
              <div className="mb-3">
                <div className="text-xs font-medium text-purple-400 mb-1">Root Cause</div>
                <div className="text-sm text-gray-300">{incident.root_cause}</div>
              </div>
            )}
            
            {incident.impact_description && (
              <div className="mb-3">
                <div className="text-xs font-medium text-purple-400 mb-1">Impact</div>
                <div className="text-sm text-gray-300">{incident.impact_description}</div>
              </div>
            )}
            
            {incident.source_url && (
              <a
                href={incident.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                <span>Read more</span>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            )}
          </div>
        )}

        {/* View details button */}
        {!showDetails && onViewDetails && (
          <button
            onClick={() => onViewDetails(incident)}
            className="mt-4 w-full py-2 px-4 bg-gray-800 hover:bg-purple-600/20 text-gray-300 hover:text-purple-400 rounded-lg transition-all font-medium text-sm"
          >
            View Details →
          </button>
        )}
      </div>
    </div>
  );
}

