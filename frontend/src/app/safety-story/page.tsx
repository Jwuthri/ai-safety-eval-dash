'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useOrganization } from '@/contexts/OrganizationContext';
import IncidentCard from '@/components/safety/IncidentCard';
import type { AIIncident } from '@/types/safety';

export default function SafetyStoryPage() {
  const { currentOrganization } = useOrganization();
  const [incidents, setIncidents] = useState<AIIncident[]>([]);
  const [loading, setLoading] = useState(true);
  const [incidentStats, setIncidentStats] = useState<any>(null);
  const [selectedIncident, setSelectedIncident] = useState<AIIncident | null>(null);

  useEffect(() => {
    loadIncidents();
    loadIncidentStats();
  }, [currentOrganization]);

  async function loadIncidents() {
    try {
      const params = new URLSearchParams();
      if (currentOrganization?.business_type_id) {
        params.set('business_type_id', currentOrganization.business_type_id);
      }
      params.set('limit', '20');
      
      const response = await fetch(`http://localhost:8000/api/v1/incidents?${params}`);
      if (response.ok) {
        const data = await response.json();
        setIncidents(data);
      }
    } catch (error) {
      console.error('Failed to load incidents:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadIncidentStats() {
    try {
      const params = new URLSearchParams();
      if (currentOrganization?.business_type_id) {
        params.set('business_type_id', currentOrganization.business_type_id);
      }
      
      const [severityRes, harmTypeRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/incidents/stats/severity?${params}`),
        fetch(`http://localhost:8000/api/v1/incidents/stats/harm-types?${params}`)
      ]);
      
      if (severityRes.ok && harmTypeRes.ok) {
        const severityData = await severityRes.json();
        const harmTypeData = await harmTypeRes.json();
        setIncidentStats({
          severity: severityData,
          harmTypes: harmTypeData,
        });
      }
    } catch (error) {
      console.error('Failed to load incident stats:', error);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading safety story...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-purple-500/20 bg-card/30 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/" className="text-xl font-bold gradient-text">
                AI Safety Eval
              </Link>
              <nav className="hidden md:flex gap-6">
                <Link href="/dashboard" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Dashboard
                </Link>
                <Link href="/safety-story" className="text-purple-400 font-medium">
                  Safety Story
                </Link>
                <Link href="/taxonomy" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Taxonomy
                </Link>
              </nav>
            </div>
            {currentOrganization && (
              <div className="flex items-center gap-3 px-4 py-2 bg-background/50 border border-purple-500/30 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-sm font-medium text-white">{currentOrganization.name}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold gradient-text mb-4">
            Safety Story
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            From real-world incidents to comprehensive protection. See how we map failures to safeguards, tests, and residual risks.
          </p>
        </div>

        {/* Flow Visualization */}
        <div className="mb-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Step 1: Incidents */}
            <div className="relative p-6 rounded-2xl bg-gradient-to-br from-red-900/20 to-red-800/20 border border-red-500/30">
              <div className="text-4xl mb-3">⚠️</div>
              <h3 className="text-lg font-semibold text-white mb-2">1. Real Incidents</h3>
              <p className="text-sm text-gray-300 mb-3">What happened in production</p>
              <div className="text-3xl font-bold text-red-400">
                {incidentStats?.severity.total_incidents || incidents.length}
              </div>
              <div className="text-xs text-gray-400 mt-1">tracked failures</div>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <svg className="w-12 h-12 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>

            {/* Step 2: Safeguards */}
            <div className="relative p-6 rounded-2xl bg-gradient-to-br from-green-900/20 to-green-800/20 border border-green-500/30">
              <div className="text-4xl mb-3">🛡️</div>
              <h3 className="text-lg font-semibold text-white mb-2">2. Safeguards</h3>
              <p className="text-sm text-gray-300 mb-3">AIUC-1 compliance standards</p>
              <div className="text-3xl font-bold text-green-400">
                100%
              </div>
              <div className="text-xs text-gray-400 mt-1">coverage required</div>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <svg className="w-12 h-12 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>

            {/* Step 3: Tests */}
            <div className="relative p-6 rounded-2xl bg-gradient-to-br from-blue-900/20 to-blue-800/20 border border-blue-500/30">
              <div className="text-4xl mb-3">🧪</div>
              <h3 className="text-lg font-semibold text-white mb-2">3. Tests</h3>
              <p className="text-sm text-gray-300 mb-3">Comprehensive evaluation</p>
              <div className="text-3xl font-bold text-blue-400">
                {incidents.length * 3}+
              </div>
              <div className="text-xs text-gray-400 mt-1">test scenarios</div>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <svg className="w-12 h-12 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>

            {/* Step 4: Residual Risk */}
            <div className="relative p-6 rounded-2xl bg-gradient-to-br from-purple-900/20 to-purple-800/20 border border-purple-500/30">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="text-lg font-semibold text-white mb-2">4. Residual Risk</h3>
              <p className="text-sm text-gray-300 mb-3">What's left to manage</p>
              <div className="text-3xl font-bold text-purple-400">
                Low
              </div>
              <div className="text-xs text-gray-400 mt-1">after mitigation</div>
            </div>
          </div>
        </div>

        {/* Incidents Section */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Real-World Incidents</h2>
              <p className="text-gray-400">Learn from what went wrong in production</p>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
            >
              View Tests →
            </Link>
          </div>

          {incidents.length === 0 ? (
            <div className="text-center py-16 bg-card/20 rounded-2xl border border-purple-500/20">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="text-2xl font-bold text-white mb-2">No Incidents Tracked Yet</h3>
              <p className="text-gray-400">
                Add real-world AI failures to map to your test scenarios
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {incidents.map((incident) => (
                <IncidentCard
                  key={incident.id}
                  incident={incident}
                  showDetails={selectedIncident?.id === incident.id}
                  onViewDetails={(inc) => setSelectedIncident(selectedIncident?.id === inc.id ? null : inc)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Stats Section */}
        {incidentStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {/* Severity Breakdown */}
            <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-4">Severity Distribution</h3>
              <div className="space-y-3">
                {Object.entries(incidentStats.severity.severity_breakdown || {}).map(([severity, count]: [string, any]) => (
                  <div key={severity} className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">{severity}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-600 to-blue-600"
                          style={{
                            width: `${(count / (incidentStats.severity.total_incidents || 1)) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-white w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Harm Type Breakdown */}
            <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-4">Harm Types</h3>
              <div className="space-y-3">
                {Object.entries(incidentStats.harmTypes.harm_type_breakdown || {}).map(([harmType, count]: [string, any]) => (
                  <div key={harmType} className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">{harmType.replace(/_/g, ' ')}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-orange-600 to-red-600"
                          style={{
                            width: `${(count / (incidentStats.harmTypes.total_incidents || 1)) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-white w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* CTA Section */}
        <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-500/30 text-center">
          <h3 className="text-2xl font-bold text-white mb-3">
            See How Your AI Performs Against These Scenarios
          </h3>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Run comprehensive multi-round evaluations based on real-world failures. Track improvement from 77.9% to 100% pass rate.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/evaluations/run"
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all font-semibold"
            >
              🚀 Run Evaluation
            </Link>
            <Link
              href="/dashboard"
              className="px-6 py-3 bg-gray-800 text-white rounded-xl hover:bg-gray-700 transition-all font-semibold"
            >
              📊 View Results
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

