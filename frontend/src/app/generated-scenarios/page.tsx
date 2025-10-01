"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import { GeneratedScenario } from '@/types/safety';
import './styles.css';

interface Organization {
  id: string;
  name: string;
  business_type_id: string;
}

export default function GeneratedScenariosPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string>('');
  const [scenarios, setScenarios] = useState<GeneratedScenario[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState(20);
  const [incidentNames, setIncidentNames] = useState<Record<string, string>>({});

  // Load organizations on mount
  useEffect(() => {
    loadOrganizations();
  }, []);

  // Load scenarios when org changes
  useEffect(() => {
    if (selectedOrgId) {
      loadScenarios(selectedOrgId);
    }
  }, [selectedOrgId]);

  async function loadOrganizations() {
    try {
      const orgs = await api.getOrganizations();
      setOrganizations(orgs);
      if (orgs.length > 0) {
        setSelectedOrgId(orgs[0].id);
      }
    } catch (err) {
      console.error('Failed to load organizations:', err);
      setError('Failed to load organizations');
    }
  }

  async function loadScenarios(orgId: string) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getGeneratedScenarios(orgId);
      setScenarios(data);
      
      // Fetch incident names for all referenced incidents
      const incidentIds = Array.from(new Set(
        data
          .filter((s: GeneratedScenario) => s.incident_reference)
          .map((s: GeneratedScenario) => s.incident_reference!)
      ));
      
      const names: Record<string, string> = {};
      await Promise.all(
        incidentIds.map(async (id) => {
          try {
            const incident = await api.getIncident(id);
            names[id] = incident.incident_name;
          } catch (err) {
            console.error(`Failed to load incident ${id}:`, err);
            names[id] = 'Unknown Incident';
          }
        })
      );
      setIncidentNames(names);
    } catch (err) {
      console.error('Failed to load scenarios:', err);
      setError('Failed to load scenarios');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleGenerate() {
    if (!selectedOrgId) {
      setError('Please select an organization');
      return;
    }

    setIsGenerating(true);
    setError(null);
    try {
      const result = await api.generateScenarios({
        organization_id: selectedOrgId,
        count: count,
      });
      setScenarios(result.scenarios);
      // alert(`Successfully generated ${result.scenarios_generated} scenarios!`);
    } catch (err: any) {
      console.error('Failed to generate scenarios:', err);
      setError(err.message || 'Failed to generate scenarios');
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleDelete() {
    if (!selectedOrgId) return;
    
    if (!confirm('Are you sure you want to delete all generated scenarios for this organization?')) {
      return;
    }

    try {
      await api.deleteGeneratedScenarios(selectedOrgId);
      setScenarios([]);
      alert('Scenarios deleted successfully');
    } catch (err: any) {
      console.error('Failed to delete scenarios:', err);
      setError(err.message || 'Failed to delete scenarios');
    }
  }

  const selectedOrg = organizations.find(org => org.id === selectedOrgId);

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
                <Link href="/safety-story" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Safety Story
                </Link>
                <Link href="/taxonomy" className="text-gray-400 hover:text-purple-400 transition-colors">
                  AI Scenarios
                </Link>
                <Link href="/evaluations/run" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Run Evaluation
                </Link>
                <Link href="/generated-scenarios" className="text-purple-400 font-medium">
                  Generate Scenarios
                </Link>
              </nav>
            </div>
            {selectedOrg && (
              <div className="flex items-center gap-3 px-4 py-2 bg-background/50 border border-purple-500/30 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-sm font-medium text-white">{selectedOrg.name}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container">
        <div className="header">
          <h1>AI-Generated Test Scenarios</h1>
          <p className="subtitle">
            Auto-generate comprehensive test scenarios based on organization type and context
          </p>
        </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <div className="controls">
        <div className="control-group">
          <label htmlFor="org-select">Organization:</label>
          <select
            id="org-select"
            value={selectedOrgId}
            onChange={(e) => setSelectedOrgId(e.target.value)}
            disabled={isGenerating}
          >
            <option value="">Select an organization...</option>
            {organizations.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="count-input">Number of scenarios:</label>
          <input
            id="count-input"
            type="number"
            min="1"
            max="50"
            value={count}
            onChange={(e) => setCount(parseInt(e.target.value))}
            disabled={isGenerating}
          />
        </div>

        <div className="button-group">
          <button
            onClick={handleGenerate}
            disabled={!selectedOrgId || isGenerating}
            className="btn-primary"
          >
            {isGenerating ? 'Generating...' : 'Generate Scenarios'}
          </button>
          
          {scenarios.length > 0 && (
            <button
              onClick={handleDelete}
              disabled={isGenerating}
              className="btn-danger"
            >
              Delete All
            </button>
          )}
        </div>
      </div>

      {selectedOrg && (
        <div className="org-info">
          <strong>Selected:</strong> {selectedOrg.name}
          {scenarios.length > 0 && (
            <span className="scenario-count">
              {scenarios.length} scenarios loaded
            </span>
          )}
        </div>
      )}

      {isLoading ? (
        <div className="loading">Loading scenarios...</div>
      ) : scenarios.length === 0 ? (
        <div className="empty-state">
          <p>No scenarios generated yet.</p>
          <p>Click "Generate Scenarios" to create AI-powered test scenarios.</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="scenarios-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Sub-Category</th>
                <th>Test Prompt</th>
                <th>Expected Behavior</th>
                <th>Tactics</th>
                <th>Use Case</th>
                <th>Incident Ref</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((scenario) => (
                <tr key={scenario.id}>
                  <td>
                    <span className="badge category-badge">
                      {scenario.category || 'N/A'}
                    </span>
                  </td>
                  <td className="sub-category">{scenario.sub_category || '-'}</td>
                  <td className="prompt-cell">
                    <div className="prompt-text">{scenario.input_prompt}</div>
                  </td>
                  <td className="behavior-cell">
                    <div className="behavior-text">
                      {scenario.expected_behavior || '-'}
                    </div>
                  </td>
                  <td>
                    <div className="tactics">
                      {scenario.tactics && scenario.tactics.length > 0 ? (
                        scenario.tactics.map((tactic, idx) => (
                          <span key={idx} className="badge tactic-badge">
                            {tactic}
                          </span>
                        ))
                      ) : (
                        '-'
                      )}
                    </div>
                  </td>
                  <td className="use-case">{scenario.use_case || '-'}</td>
                  <td className="incident-ref">
                    {scenario.incident_reference ? (
                      <Link 
                        href={`/safety-story?incident=${scenario.incident_reference}`}
                        className="incident-link"
                        title={`Related to: ${incidentNames[scenario.incident_reference] || 'Loading...'}`}
                      >
                        🔗 {incidentNames[scenario.incident_reference] 
                          ? (incidentNames[scenario.incident_reference].length > 20 
                              ? incidentNames[scenario.incident_reference].substring(0, 20) + '...' 
                              : incidentNames[scenario.incident_reference])
                          : 'Loading...'
                        }
                      </Link>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="created-date">
                    {new Date(scenario.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isGenerating && (
        <div className="generating-overlay">
          <div className="generating-spinner">
            <div className="spinner"></div>
            <p>Generating {count} AI-powered test scenarios...</p>
            <p className="generating-hint">This may take 30-60 seconds</p>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

