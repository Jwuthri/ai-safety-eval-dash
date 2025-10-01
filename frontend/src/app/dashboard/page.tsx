'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api/client';
import type { EvaluationRound, RoundStatistics, SeverityGrade } from '@/lib/types';

// Dynamically import Plotly
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

// Mock data for demo (replace with real API calls)
const MOCK_ORG_ID = "9a4c8fe4-0b4e-4e87-9dab-de5afdae9014"; // AirCanada

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

  useEffect(() => {
    loadRounds();
  }, []);

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

  async function loadRounds() {
    try {
      const data = await api.getOrganizationRounds(MOCK_ORG_ID);
      setRounds(data);
      if (data.length > 0) {
        setSelectedRound(data[0].id);
        // Load stats for all rounds
        const statsPromises = data.map(round => api.getRoundStatistics(round.id));
        const allStats = await Promise.all(statsPromises);
        setAllRoundsStats(allStats);
        
        // Load comparison data for category breakdown
        const compRes = await fetch(`http://localhost:8000/api/v1/comparisons/organizations/${MOCK_ORG_ID}/rounds-comparison`);
        if (compRes.ok) {
          const compData = await compRes.json();
          setComparisonData(compData);
        }
      }
    } catch (error) {
      console.error('Failed to load rounds:', error);
    } finally {
      setLoading(false);
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

  if (loading) {
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
                <Link href="/evaluations/run" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Run Evaluation
                </Link>
                <Link href="/taxonomy" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Taxonomy
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">AirCanada Corp</span>
              <div className="w-2 h-2 rounded-full bg-green-500" />
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
                    href={`/certification?round_id=${selectedRound}`}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-card/50 border border-purple-500/20 text-white rounded-xl hover:border-purple-500/40 transition-all"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    Check AIUC-1 Eligibility
                  </Link>
                </div>
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
                    background: `linear-gradient(to right, #8b5cf6 0%, #8b5cf6 ${(currentRoundIndex / (comparisonData.rounds.length - 1)) * 100}%, #374151 ${(currentRoundIndex / (comparisonData.rounds.length - 1)) * 100}%, #374151 100%)`
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
                              [0, '#1a1f35'],
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
