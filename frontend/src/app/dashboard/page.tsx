'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api/client';
import type { EvaluationRound, RoundStatistics, SeverityGrade } from '@/lib/types';
import { useOrganization } from '@/contexts/OrganizationContext';

// Dynamically import Plotly
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface BusinessType {
  id: string;
  name: string;
  industry: string;
  description: string;
}

interface ComparisonData {
  organization_id: string
  organization_name: string
  rounds: Array<{
    round_id: string
    round_number: number
    description: string | null
    status: string
    started_at: string
    completed_at: string | null
    total_tests: number
    pass_count: number
    pass_rate: number
    category_breakdown: {
      [category: string]: {
        total: number
        pass_count: number
        pass_rate: number
        severity_breakdown: { [grade: string]: number }
        sub_categories: {
          [subCategory: string]: {
            total: number
            pass_count: number
            pass_rate: number
            severity_breakdown: { [grade: string]: number }
          }
        }
      }
    }
  }>
}

export default function DashboardPage() {
  // Use global organization context
  const { 
    organizations, 
    selectedOrg, 
    setSelectedOrg, 
    currentOrganization, 
    loading: orgLoading,
    refreshOrganizations 
  } = useOrganization();
  
  const [businessTypes, setBusinessTypes] = useState<BusinessType[]>([]);
  const [showCreateOrgModal, setShowCreateOrgModal] = useState(false);
  
  const [rounds, setRounds] = useState<EvaluationRound[]>([]);
  const [selectedRound, setSelectedRound] = useState<string>('');
  const [stats, setStats] = useState<RoundStatistics | null>(null);
  const [allRoundsStats, setAllRoundsStats] = useState<RoundStatistics[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'compare'>('overview');
  const [groupBy, setGroupBy] = useState<'category' | 'subcategory'>('category');
  const [currentRoundIndex, setCurrentRoundIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [eligibilityResult, setEligibilityResult] = useState<any>(null);
  const [showEligibilityModal, setShowEligibilityModal] = useState(false);

  // New org creation form
  const [newOrgName, setNewOrgName] = useState('');
  const [newOrgSlug, setNewOrgSlug] = useState('');
  const [newOrgBusinessType, setNewOrgBusinessType] = useState('');
  const [newOrgContactEmail, setNewOrgContactEmail] = useState('');
  const [newOrgContactName, setNewOrgContactName] = useState('');
  const [creatingOrg, setCreatingOrg] = useState(false);

  useEffect(() => {
    loadBusinessTypes();
  }, []);

  // Set loading to false once organizations are loaded
  useEffect(() => {
    if (!orgLoading) {
      setLoading(false);
    }
  }, [orgLoading]);

  useEffect(() => {
    if (selectedOrg) {
      loadRounds();
    }
  }, [selectedOrg]);

  useEffect(() => {
    if (selectedRound) {
      loadStats(selectedRound);
    }
  }, [selectedRound]);

  // Animation timer
  useEffect(() => {
    if (!isPlaying || !comparisonData) return;
    
    const timer = setInterval(() => {
      setCurrentRoundIndex((prev) => {
        if (prev >= comparisonData.rounds.length - 1) {
          setIsPlaying(false);
          return 0; // Reset to beginning
        }
        return prev + 1;
      });
    }, 2000); // 2 seconds per round
    
    return () => clearInterval(timer);
  }, [isPlaying, comparisonData]);

  async function loadBusinessTypes() {
    try {
      const typesResponse = await fetch('http://localhost:8000/api/v1/business-types/');
      if (!typesResponse.ok) {
        throw new Error(`Failed to fetch business types: ${typesResponse.status}`);
      }
      
      const types = await typesResponse.json();
      console.log('✅ Loaded business types:', types.length);
      setBusinessTypes(types);
    } catch (error) {
      console.error('❌ Failed to load business types:', error);
    }
  }

  async function loadRounds() {
    if (!selectedOrg) return;
    
    try {
      const data = await api.getOrganizationRounds(selectedOrg);
      setRounds(data);
      if (data.length > 0) {
        setSelectedRound(data[0].id);
        // Load stats for all rounds
        const statsPromises = data.map((round: any) => api.getRoundStatistics(round.id));
        const allStats = await Promise.all(statsPromises);
        setAllRoundsStats(allStats as any);
        
        // Load comparison data for category breakdown
        const compRes = await fetch(`http://localhost:8000/api/v1/comparisons/organizations/${selectedOrg}/rounds-comparison`);
        if (compRes.ok) {
          const compData = await compRes.json();
          setComparisonData(compData);
        }
      }
    } catch (error) {
      console.error('Failed to load rounds:', error);
    }
  }
  
  async function createOrganization() {
    if (!newOrgName || !newOrgSlug || !newOrgBusinessType) {
      alert('Please fill in all required fields');
      return;
    }
    
    setCreatingOrg(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/organizations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newOrgName,
          slug: newOrgSlug,
          business_type_id: newOrgBusinessType,
          contact_email: newOrgContactEmail || null,
          contact_name: newOrgContactName || null,
        }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create organization');
      }
      
      const newOrg = await response.json();
      
      // Reload organizations
      await refreshOrganizations();
      
      // Select the new org
      setSelectedOrg(newOrg.id);
      
      // Close modal and reset form
      setShowCreateOrgModal(false);
      setNewOrgName('');
      setNewOrgSlug('');
      setNewOrgBusinessType('');
      setNewOrgContactEmail('');
      setNewOrgContactName('');
    } catch (error: any) {
      console.error('Failed to create organization:', error);
      alert(error.message || 'Failed to create organization');
    } finally {
      setCreatingOrg(false);
    }
  }

  async function loadStats(roundId: string) {
    try {
      const data = await api.getRoundStatistics(roundId);
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }

  async function checkEligibility() {
    if (!selectedRound || !selectedOrg) return;
    
    setCheckingEligibility(true);
    
    try {
      // Check eligibility for the selected round
      const eligibilityUrl = `http://localhost:8000/api/v1/certifications/organizations/${selectedOrg}/eligibility?evaluation_round_id=${selectedRound}`;
      console.log('Checking eligibility at:', eligibilityUrl);
      
      const eligibilityResponse = await fetch(eligibilityUrl);
      
      if (!eligibilityResponse.ok) {
        const errorText = await eligibilityResponse.text();
        console.error('Eligibility check failed:', errorText);
        throw new Error(`Failed to check eligibility: ${eligibilityResponse.status}`);
      }
      
      const eligibility = await eligibilityResponse.json();
      console.log('Eligibility result:', eligibility);
      
      setEligibilityResult(eligibility);
      setShowEligibilityModal(true);
    } catch (error: any) {
      console.error('Failed to check eligibility:', error);
      alert(error.message || 'Failed to check AIUC-1 eligibility');
    } finally {
      setCheckingEligibility(false);
    }
  }

  if (orgLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const currentRound = rounds.find(r => r.id === selectedRound);
  const passRate = stats?.pass_rate || 0;
  const totalTests = stats?.total_tests || 0;

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
                <Link href="/dashboard" className="text-purple-400 font-medium">
                  Dashboard
                </Link>
                <Link href="/safety-story" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Safety Story
                </Link>
                <Link href="/evaluations/run" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Run Evaluation
                </Link>
                <Link href="/taxonomy" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Taxonomy
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              {/* Current Organization Display */}
              {currentOrganization ? (
                <>
                  <div className="flex items-center gap-3 px-4 py-2 bg-background/50 border border-purple-500/30 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-green-500" />
                      <span className="text-sm font-medium text-white">{currentOrganization.name}</span>
                    </div>
                  </div>
                  
                  <Link
                    href="/"
                    className="px-4 py-2 text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium"
                  >
                    Change Org
                  </Link>
                </>
              ) : (
                <Link
                  href="/"
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                >
                  Select Organization
                </Link>
              )}
              
              {/* Create Org Button */}
              <button
                onClick={() => setShowCreateOrgModal(true)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
              >
                + New Org
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">
            Safety Evaluation Dashboard
          </h1>
          <p className="text-gray-400">
            Multi-round AI safety testing with comprehensive metrics
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex gap-4 border-b border-purple-500/20">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 font-medium transition-all ${
                activeTab === 'overview'
                  ? 'text-purple-400 border-b-2 border-purple-400'
                  : 'text-gray-400 hover:text-purple-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('compare')}
              className={`px-6 py-3 font-medium transition-all ${
                activeTab === 'compare'
                  ? 'text-purple-400 border-b-2 border-purple-400'
                  : 'text-gray-400 hover:text-purple-300'
              }`}
            >
              Compare Rounds
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {rounds.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-2xl font-bold text-white mb-2">No Evaluation Rounds Yet</h3>
                <p className="text-gray-400 mb-6">
                  {selectedOrg 
                    ? `This organization hasn't run any evaluation rounds yet.`
                    : 'Please select an organization first.'}
                </p>
                <Link
                  href="/evaluations/run"
                  className="inline-block px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all font-semibold"
                >
                  🚀 Run First Evaluation
                </Link>
              </div>
            ) : (
              <>
                {/* Round Selector */}
                <div className="mb-8">
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Select Evaluation Round
                  </label>
                  <select
                    value={selectedRound}
                    onChange={(e) => setSelectedRound(e.target.value)}
                    className="w-full md:w-96 px-4 py-3 bg-card border border-purple-500/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                  >
                    {rounds.map((round) => (
                      <option key={round.id} value={round.id}>
                        Round {round.round_number} - {round.status} ({new Date(round.started_at).toLocaleDateString()})
                      </option>
                    ))}
                  </select>
                </div>

                {stats && (
              <>
                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                  <KPICard
                    title="Pass Rate"
                    value={`${passRate.toFixed(1)}%`}
                    icon={
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    }
                    color="text-green-400"
                  />
                  <KPICard
                    title="Total Tests"
                    value={totalTests.toString()}
                    icon={
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    }
                    color="text-blue-400"
                  />
                  <KPICard
                    title="Critical Errors"
                    value={(stats.severity_breakdown.P0 + stats.severity_breakdown.P1).toString()}
                    icon={
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    }
                    color="text-red-400"
                  />
                  <KPICard
                    title="Round Status"
                    value={currentRound?.status || 'Unknown'}
                    icon={
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    }
                    color="text-purple-400"
                  />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  {/* Pass Rate Chart */}
                  <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
                    <h3 className="text-xl font-semibold text-white mb-4">Pass Rate Overview</h3>
                    <div className="space-y-4">
                      <PassRateVisual passRate={passRate} />
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Passed: {stats.severity_breakdown.PASS}</span>
                        <span className="text-gray-400">Failed: {totalTests - stats.severity_breakdown.PASS}</span>
                      </div>
                    </div>
                  </div>

                  {/* Severity Distribution */}
                  <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
                    <h3 className="text-xl font-semibold text-white mb-4">Severity Distribution</h3>
                    <div className="space-y-3">
                      <SeverityBar label="P0 - Catastrophic" count={stats.severity_breakdown.P0} total={totalTests} color="bg-red-900" />
                      <SeverityBar label="P1 - Critical" count={stats.severity_breakdown.P1} total={totalTests} color="bg-red-600" />
                      <SeverityBar label="P2 - Serious" count={stats.severity_breakdown.P2} total={totalTests} color="bg-orange-500" />
                      <SeverityBar label="P3 - Moderate" count={stats.severity_breakdown.P3} total={totalTests} color="bg-yellow-500" />
                      <SeverityBar label="P4 - Trivial" count={stats.severity_breakdown.P4} total={totalTests} color="bg-yellow-300" />
                      <SeverityBar label="PASS" count={stats.severity_breakdown.PASS} total={totalTests} color="bg-green-500" />
                    </div>
                  </div>
                </div>

                {/* Failed Tests Summary */}
                <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold text-white">Failed Tests Summary</h3>
                    <Link
                      href={`/evaluations/${selectedRound}/results`}
                      className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
                    >
                      View All Results →
                    </Link>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                    {Object.entries(stats.severity_breakdown)
                      .filter(([key]) => key !== 'PASS')
                      .map(([severity, count]) => (
                        <div key={severity} className="text-center p-4 rounded-xl bg-background/50">
                          <div className={`text-2xl font-bold mb-1 ${getSeverityColor(severity as SeverityGrade)}`}>
                            {count}
                          </div>
                          <div className="text-xs text-gray-400">{severity}</div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* CTA */}
                <div className="mt-8 flex gap-4">
                  <Link
                    href="/evaluations/run"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all shadow-lg hover:shadow-purple-glow"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Run New Round
                  </Link>
                  <Link
                    href={`/human-review${selectedRound ? `?round_id=${selectedRound}` : ''}`}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-xl hover:from-amber-700 hover:to-orange-700 transition-all shadow-lg hover:shadow-orange-glow"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Human in the Loop
                  </Link>
                  <button
                    onClick={checkEligibility}
                    disabled={checkingEligibility || !selectedRound}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {checkingEligibility ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Checking...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        Check AIUC-1 Eligibility
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
              </>
            )}
          </>
        )}

        {/* Compare Rounds Tab */}
        {activeTab === 'compare' && comparisonData && (
          <>
            {/* Group By Toggle */}
            <div className="mb-8 flex items-center gap-4">
              <span className="text-sm text-gray-400">Group by:</span>
              <button
                onClick={() => setGroupBy('category')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  groupBy === 'category'
                    ? 'bg-purple-600 text-white'
                    : 'bg-card border border-purple-500/20 text-gray-400 hover:text-white'
                }`}
              >
                Category
              </button>
              <button
                onClick={() => setGroupBy('subcategory')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  groupBy === 'subcategory'
                    ? 'bg-purple-600 text-white'
                    : 'bg-card border border-purple-500/20 text-gray-400 hover:text-white'
                }`}
              >
                Sub-Category
              </button>
            </div>

            {/* Severity Distribution Per Round */}
            <div className="mb-8 p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">📊 Severity Distribution by Round</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {comparisonData.rounds.map((round) => (
                  <div key={round.round_id} className="p-4 rounded-xl bg-background/30">
                    <h4 className="text-lg font-semibold text-purple-300 mb-4">
                      Round {round.round_number}
                    </h4>
                    <div className="space-y-3">
                      {Object.entries(round).length > 0 && (() => {
                        const severityBreakdown = { P0: 0, P1: 0, P2: 0, P3: 0, P4: 0, PASS: 0 };
                        Object.values(round.category_breakdown).forEach((cat: any) => {
                          Object.entries(cat.severity_breakdown).forEach(([grade, count]) => {
                            severityBreakdown[grade as keyof typeof severityBreakdown] += count as number;
                          });
                        });
                        return Object.entries(severityBreakdown).map(([severity, count]) => (
                          <SeverityBar
                            key={severity}
                            label={severity}
                            count={count}
                            total={round.total_tests}
                            color={
                              severity === 'PASS' ? 'bg-green-500' :
                              severity === 'P4' ? 'bg-yellow-300' :
                              severity === 'P3' ? 'bg-yellow-500' :
                              severity === 'P2' ? 'bg-orange-500' :
                              severity === 'P1' ? 'bg-red-600' :
                              'bg-red-900'
                            }
                          />
                        ));
                      })()}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Animated Bubble Chart */}
            <div className="mb-8 p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">🎬 Grade Evolution Animation</h3>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => {
                      if (!isPlaying) {
                        setCurrentRoundIndex(0);
                      }
                      setIsPlaying(!isPlaying);
                    }}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
                  >
                    {isPlaying ? '⏸ Pause' : '▶ Play'}
                  </button>
                  <span className="text-sm text-gray-400">
                    Round {currentRoundIndex + 1} / {comparisonData.rounds.length}
                  </span>
                </div>
              </div>
              
              {/* Slider */}
              <div className="mb-6">
                <input
                  type="range"
                  min="0"
                  max={comparisonData.rounds.length - 1}
                  value={currentRoundIndex}
                  onChange={(e) => {
                    setIsPlaying(false);
                    setCurrentRoundIndex(parseInt(e.target.value));
                  }}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  style={{
                    background: `linear-gradient(to right, #8b5cf6 0%, #8b5cf6 ${(currentRoundIndex / (comparisonData.rounds.length - 1)) * 100}%, #334155 ${(currentRoundIndex / (comparisonData.rounds.length - 1)) * 100}%, #334155 100%)`
                  }}
                />
                <div className="flex justify-between mt-2">
                  {comparisonData.rounds.map((round, idx) => (
                    <span key={round.round_id} className="text-xs text-gray-400">
                      R{round.round_number}
                    </span>
                  ))}
                </div>
              </div>

              {(() => {
                const gradeOrder = ['PASS', 'P4', 'P3', 'P2', 'P1', 'P0'];
                const gradeColors: Record<string, string> = {
                  'P0': '#991b1b',
                  'P1': '#dc2626',
                  'P2': '#ef4444',
                  'P3': '#f97316',
                  'P4': '#facc15',
                  'PASS': '#10b981',
                };
                
                const round = comparisonData.rounds[currentRoundIndex];
                const items = groupBy === 'category'
                  ? Object.keys(round.category_breakdown)
                  : Object.values(round.category_breakdown).flatMap((cat: any) =>
                      Object.keys(cat.sub_categories)
                    );
                
                const uniqueItems = Array.from(new Set(items)).sort();
                
                // Collect all bubbles for current round
                const bubbles: Array<{
                  id: string;
                  x: number;
                  y: number;
                  size: number;
                  color: string;
                  item: string;
                  grade: string;
                  count: number;
                }> = [];
                
                uniqueItems.forEach((item, itemIdx) => {
                  gradeOrder.forEach((grade, gradeIdx) => {
                    let count = 0;
                    if (groupBy === 'category') {
                      count = round.category_breakdown[item]?.severity_breakdown[grade] || 0;
                    } else {
                      Object.values(round.category_breakdown).forEach((cat: any) => {
                        if (cat.sub_categories[item]) {
                          count += cat.sub_categories[item].severity_breakdown[grade] || 0;
                        }
                      });
                    }
                    
                    if (count > 0) {
                      bubbles.push({
                        id: `${item}-${grade}`,
                        x: (itemIdx / (uniqueItems.length - 1 || 1)) * 100,
                        y: (gradeIdx / (gradeOrder.length - 1)) * 100,
                        size: Math.sqrt(count) * 4 + 8,
                        color: gradeColors[grade],
                        item,
                        grade,
                        count
                      });
                    }
                  });
                });
                
                return (
                  <div className="relative w-full" style={{ height: '500px' }}>
                    {/* Y-axis labels */}
                    <div className="absolute left-0 top-0 w-16 flex flex-col justify-between py-4" style={{ height: '400px' }}>
                      {gradeOrder.map((grade) => (
                        <div key={grade} className="text-xs text-gray-400 text-right pr-2">
                          {grade}
                        </div>
                      ))}
                    </div>
                    
                    {/* Chart area */}
                    <div className="absolute left-16 right-0 top-0" style={{ height: '400px' }}>
                      <AnimatePresence mode="sync">
                        {bubbles.map((bubble) => (
                          <motion.div
                            key={bubble.id}
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{
                              scale: 1,
                              opacity: 0.8,
                              left: `${bubble.x}%`,
                              top: `${bubble.y}%`
                            }}
                            exit={{ scale: 0, opacity: 0 }}
                            transition={{
                              duration: 0.5,
                              ease: 'easeInOut'
                            }}
                            className="absolute rounded-full cursor-pointer hover:opacity-100 transition-opacity"
                            style={{
                              width: `${bubble.size}px`,
                              height: `${bubble.size}px`,
                              backgroundColor: bubble.color,
                              transform: 'translate(-50%, -50%)',
                              border: '2px solid rgba(255, 255, 255, 0.3)'
                            }}
                            title={`${bubble.item}: ${bubble.grade} (${bubble.count} tests)`}
                          >
                            <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
                              {bubble.count}
                            </div>
                          </motion.div>
                        ))}
                      </AnimatePresence>
                    </div>
                    
                    {/* X-axis labels */}
                    <div className="absolute left-16 right-0 bottom-0 flex items-start pt-4" style={{ height: '80px' }}>
                      {uniqueItems.map((item, idx) => (
                        <div
                          key={item}
                          className="flex-1 flex justify-center"
                          style={{
                            position: 'absolute',
                            left: `${(idx / (uniqueItems.length - 1 || 1)) * 100}%`,
                            transform: 'translateX(-50%)'
                          }}
                        >
                          <div
                            className="text-xs text-gray-300 font-medium whitespace-nowrap px-2 py-1 rounded bg-gray-800/50"
                            style={{
                              transform: 'rotate(-45deg)',
                              transformOrigin: 'center center',
                              maxWidth: '150px'
                            }}
                          >
                            {item}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* Confusion Matrices */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-white mb-6">🎯 Performance Heatmaps by {groupBy === 'category' ? 'Category' : 'Sub-Category'}</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {(() => {
                  // Collect ALL unique categories/subcategories across ALL rounds first
                  const allItems = new Set<string>();
                  comparisonData.rounds.forEach(round => {
                    if (groupBy === 'category') {
                      Object.keys(round.category_breakdown).forEach(cat => allItems.add(cat));
                    } else {
                      Object.values(round.category_breakdown).forEach((cat: any) => {
                        Object.keys(cat.sub_categories).forEach(subCat => allItems.add(subCat));
                      });
                    }
                  });
                  
                  // Sort alphabetically for consistent ordering
                  const sortedItems = Array.from(allItems).sort();
                  const severityLevels = ['PASS', 'P4', 'P3', 'P2', 'P1', 'P0'];
                  
                  return comparisonData.rounds.map((round) => {
                    // Create matrix: rows = items (sorted consistently), cols = severity
                    const zValues: number[][] = [];
                    const yLabels: string[] = [];
                    
                    sortedItems.forEach((item) => {
                      yLabels.push(item);
                      const row: number[] = [];
                      
                      severityLevels.forEach((severity) => {
                        let count = 0;
                        if (groupBy === 'category') {
                          const catData = round.category_breakdown[item];
                          count = catData?.severity_breakdown[severity] || 0;
                        } else {
                          // Sub-category: find it across all categories
                          Object.values(round.category_breakdown).forEach((cat: any) => {
                            if (cat.sub_categories[item]) {
                              count += cat.sub_categories[item].severity_breakdown[severity] || 0;
                            }
                          });
                        }
                        row.push(count);
                      });
                      
                      zValues.push(row);
                    });
                  
                  return (
                    <div key={round.round_id} className="p-4 rounded-xl bg-card/30 backdrop-blur-sm border border-purple-500/20">
                      <h4 className="text-lg font-semibold text-purple-300 mb-4 text-center">
                        Round {round.round_number}
                      </h4>
                      <Plot
                        data={[
                          {
                            z: zValues,
                            x: severityLevels,
                            y: yLabels,
                            type: 'heatmap',
                            colorscale: [
                              [0, '#0f172a'],
                              [0.2, '#3730a3'],
                              [0.4, '#7c3aed'],
                              [0.6, '#a78bfa'],
                              [0.8, '#c4b5fd'],
                              [1, '#ddd6fe']
                            ],
                            showscale: true,
                            colorbar: {
                              thickness: 10,
                              len: 0.7,
                              tickfont: { color: '#e5e7eb', size: 10 }
                            },
                            hovertemplate: '<b>%{y}</b><br>%{x}: %{z}<extra></extra>'
                          }
                        ]}
                        layout={{
                          paper_bgcolor: 'transparent',
                          plot_bgcolor: 'transparent',
                          font: { color: '#e5e7eb', family: 'Inter, sans-serif', size: 10 },
                          xaxis: {
                            side: 'bottom',
                            tickfont: { size: 10 }
                          },
                          yaxis: {
                            tickfont: { size: 9 },
                            automargin: true
                          },
                          height: 400,
                          margin: { t: 10, b: 40, l: 100, r: 40 }
                        }}
                        config={{
                          displayModeBar: false,
                          responsive: true
                        }}
                        style={{ width: '100%' }}
                      />
                    </div>
                  );
                  });
                })()}
              </div>
            </div>
          </>
        )}

        {/* Eligibility Modal */}
        {showEligibilityModal && eligibilityResult && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-2xl w-full bg-card rounded-2xl border border-purple-500/30 shadow-2xl overflow-hidden"
            >
              {/* Header */}
              <div className={`p-6 ${eligibilityResult.is_eligible ? 'bg-gradient-to-r from-green-600/20 to-emerald-600/20 border-b border-green-500/30' : 'bg-gradient-to-r from-orange-600/20 to-red-600/20 border-b border-orange-500/30'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-5xl">
                      {eligibilityResult.is_eligible ? '✅' : '⚠️'}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">
                        AIUC-1 Certification Status
                      </h2>
                      <p className="text-sm text-gray-300 mt-1">
                        Round {currentRound?.round_number}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowEligibilityModal(false)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Eligibility Status */}
                <div className="text-center">
                  {eligibilityResult.is_eligible ? (
                    <div>
                      <h3 className="text-3xl font-bold text-green-400 mb-2">
                        🎉 Certified Eligible!
                      </h3>
                      <p className="text-gray-300">
                        Your organization meets all AIUC-1 certification requirements.
                      </p>
                    </div>
                  ) : (
                    <div>
                      <h3 className="text-3xl font-bold text-orange-400 mb-2">
                        Not Yet Eligible
                      </h3>
                      <p className="text-gray-300">
                        Additional improvements needed to meet certification standards.
                      </p>
                    </div>
                  )}
                </div>

                {/* Pass Rate */}
                <div className="p-4 rounded-xl bg-background/50 border border-purple-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 font-medium">Overall Pass Rate</span>
                    <span className="text-2xl font-bold text-purple-400">
                      {eligibilityResult.pass_rate}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-background/80 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${eligibilityResult.pass_rate === 100 ? 'bg-green-500' : 'bg-purple-500'}`}
                      style={{ width: `${eligibilityResult.pass_rate}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    {eligibilityResult.total_tests} total tests
                  </p>
                </div>

                {/* Requirements Checklist */}
                <div className="space-y-3">
                  <h4 className="text-lg font-semibold text-white mb-3">Certification Requirements</h4>
                  
                  {Object.entries(eligibilityResult.requirements).map(([key, passed]: [string, any]) => (
                    <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-background/30">
                      {passed ? (
                        <div className="text-green-400">
                          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      ) : (
                        <div className="text-red-400">
                          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      )}
                      <span className={`flex-1 ${passed ? 'text-gray-300' : 'text-red-300 font-medium'}`}>
                        {key.replace(/_/g, ' ').replace(/zero/g, 'Zero').replace(/errors/g, 'Errors')}
                      </span>
                      {!passed && (
                        <span className="text-sm text-red-400 font-bold">
                          {eligibilityResult.severity_breakdown[key.replace('zero_', '').replace('_errors', '').toUpperCase()]} found
                        </span>
                      )}
                    </div>
                  ))}
                </div>

                {/* Severity Breakdown */}
                <div className="p-4 rounded-xl bg-background/30 border border-purple-500/10">
                  <h4 className="text-sm font-medium text-gray-300 mb-3">Severity Breakdown</h4>
                  <div className="grid grid-cols-6 gap-2">
                    {Object.entries(eligibilityResult.severity_breakdown).reverse().map(([severity, count]: [string, any]) => (
                      <div key={severity} className="text-center">
                        <div className={`text-2xl font-bold ${getSeverityColor(severity as SeverityGrade)}`}>
                          {count}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">{severity}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Button */}
                <div className="pt-4">
                  {eligibilityResult.is_eligible ? (
                    <button
                      onClick={() => setShowEligibilityModal(false)}
                      className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all font-semibold"
                    >
                      🎊 Ready for Certification!
                    </button>
                  ) : (
                    <button
                      onClick={() => setShowEligibilityModal(false)}
                      className="w-full py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all font-semibold"
                    >
                      Close
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Create Organization Modal */}
        {showCreateOrgModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-2xl w-full bg-card rounded-2xl border border-purple-500/30 shadow-2xl overflow-hidden"
            >
              {/* Header */}
              <div className="p-6 bg-gradient-to-r from-purple-600/20 to-blue-600/20 border-b border-purple-500/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-4xl">🏢</div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">Create Organization</h2>
                      <p className="text-sm text-gray-300 mt-1">Set up a new organization for evaluation</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowCreateOrgModal(false)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Form */}
              <div className="p-6 space-y-4">
                {/* Organization Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Organization Name *
                  </label>
                  <input
                    type="text"
                    value={newOrgName}
                    onChange={(e) => {
                      setNewOrgName(e.target.value);
                      // Auto-generate slug from name
                      setNewOrgSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
                    }}
                    placeholder="e.g., AirCanada Corp"
                    className="w-full px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                  />
                </div>

                {/* Slug */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Slug * <span className="text-xs text-gray-500">(URL-friendly identifier)</span>
                  </label>
                  <input
                    type="text"
                    value={newOrgSlug}
                    onChange={(e) => setNewOrgSlug(e.target.value)}
                    placeholder="e.g., aircanada"
                    className="w-full px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors font-mono text-sm"
                  />
                </div>

                {/* Business Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Business Type *
                  </label>
                  <select
                    value={newOrgBusinessType}
                    onChange={(e) => setNewOrgBusinessType(e.target.value)}
                    className="w-full px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white focus:outline-none focus:border-purple-500 transition-colors"
                  >
                    <option value="">Select a business type...</option>
                    {businessTypes.map(type => (
                      <option key={type.id} value={type.id}>
                        {type.name} - {type.industry}
                      </option>
                    ))}
                  </select>
                  {newOrgBusinessType && businessTypes.find(t => t.id === newOrgBusinessType) && (
                    <p className="text-xs text-gray-400 mt-2">
                      {businessTypes.find(t => t.id === newOrgBusinessType)?.description}
                    </p>
                  )}
                </div>

                {/* Contact Email (Optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contact Email <span className="text-xs text-gray-500">(optional)</span>
                  </label>
                  <input
                    type="email"
                    value={newOrgContactEmail}
                    onChange={(e) => setNewOrgContactEmail(e.target.value)}
                    placeholder="e.g., safety@aircanada.com"
                    className="w-full px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                  />
                </div>

                {/* Contact Name (Optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contact Person <span className="text-xs text-gray-500">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={newOrgContactName}
                    onChange={(e) => setNewOrgContactName(e.target.value)}
                    placeholder="e.g., John Doe"
                    className="w-full px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={() => setShowCreateOrgModal(false)}
                    disabled={creatingOrg}
                    className="flex-1 py-3 bg-background border border-purple-500/30 text-white rounded-xl hover:border-purple-500 transition-all font-semibold disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createOrganization}
                    disabled={creatingOrg || !newOrgName || !newOrgSlug || !newOrgBusinessType}
                    className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creatingOrg ? (
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Creating...
                      </div>
                    ) : (
                      '🚀 Create Organization'
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  );
}

// Components
function KPICard({ title, value, icon, color }: { title: string; value: string; icon: React.ReactNode; color: string }) {
  return (
    <div className="p-6 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20 hover:border-purple-500/40 transition-all">
      <div className="flex items-center gap-4">
        <div className={`${color}`}>{icon}</div>
        <div>
          <div className="text-sm text-gray-400 mb-1">{title}</div>
          <div className="text-2xl font-bold text-white">{value}</div>
        </div>
      </div>
    </div>
  );
}

function PassRateVisual({ passRate }: { passRate: number }) {
  return (
    <div className="relative">
      <div className="flex items-center justify-center h-40">
        <div className="relative">
          <svg className="w-32 h-32 -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              fill="none"
              stroke="rgba(139, 92, 246, 0.1)"
              strokeWidth="12"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              fill="none"
              stroke="#8b5cf6"
              strokeWidth="12"
              strokeDasharray={`${2 * Math.PI * 56}`}
              strokeDashoffset={`${2 * Math.PI * 56 * (1 - passRate / 100)}`}
              strokeLinecap="round"
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-3xl font-bold gradient-text">{passRate.toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SeverityBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
  const percentage = total > 0 ? (count / total) * 100 : 0;
  
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-400">{label}</span>
        <span className="text-sm font-medium text-white">{count}</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function getSeverityColor(severity: SeverityGrade): string {
  const colors: Record<SeverityGrade, string> = {
    PASS: 'text-green-400',
    P4: 'text-yellow-300',
    P3: 'text-yellow-500',
    P2: 'text-orange-500',
    P1: 'text-red-600',
    P0: 'text-red-900',
  };
  return colors[severity] || 'text-gray-400';
}
