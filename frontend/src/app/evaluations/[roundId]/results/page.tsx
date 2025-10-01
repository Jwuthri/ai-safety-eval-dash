'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api/client';

interface EvaluationResult {
  id: string;
  scenario_id: string;
  system_response: string;
  final_grade: string;
  judge_1_grade: string;
  judge_1_reasoning: string;
  judge_1_recommendation: string;
  judge_1_model: string;
  judge_2_grade: string;
  judge_2_reasoning: string;
  judge_2_recommendation: string;
  judge_2_model: string;
  judge_3_grade: string;
  judge_3_reasoning: string;
  judge_3_recommendation: string;
  judge_3_model: string;
  scenario: {
    id: string;
    category: string;
    sub_category: string;
    methodology: string;
    input_prompt: string;
    expected_behavior: string;
  };
}

interface RoundInfo {
  id: string;
  round_number: number;
  description: string;
  status: string;
  organization_id: string;
}

export default function EvaluationResultsPage() {
  const params = useParams();
  const router = useRouter();
  const roundId = params.roundId as string;

  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [roundInfo, setRoundInfo] = useState<RoundInfo | null>(null);
  const [selectedGrade, setSelectedGrade] = useState<string>('all');
  const [expandedResult, setExpandedResult] = useState<string | null>(null);

  useEffect(() => {
    loadResults();
  }, [roundId]);

  async function loadResults() {
    try {
      // Get round info and results
      const [round, resultsData] = await Promise.all([
        api.getEvaluationRound(roundId),
        api.getRoundResults(roundId, 1000)
      ]);
      
      setRoundInfo(round);
      setResults(resultsData);
    } catch (error) {
      console.error('Failed to load results:', error);
    } finally {
      setLoading(false);
    }
  }

  const getSeverityColor = (grade: string) => {
    switch (grade) {
      case 'PASS': return 'text-green-400';
      case 'P4': return 'text-purple-400';
      case 'P3': return 'text-blue-400';
      case 'P2': return 'text-yellow-400';
      case 'P1': return 'text-orange-400';
      case 'P0': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getSeverityBgColor = (grade: string) => {
    switch (grade) {
      case 'PASS': return 'bg-green-500/20 border-green-500/30';
      case 'P4': return 'bg-purple-500/20 border-purple-500/30';
      case 'P3': return 'bg-blue-500/20 border-blue-500/30';
      case 'P2': return 'bg-yellow-500/20 border-yellow-500/30';
      case 'P1': return 'bg-orange-500/20 border-orange-500/30';
      case 'P0': return 'bg-red-500/20 border-red-500/30';
      default: return 'bg-gray-500/20 border-gray-500/30';
    }
  };

  // Filter results by selected grade
  const filteredResults = selectedGrade === 'all' 
    ? results 
    : results.filter(r => r.final_grade === selectedGrade);

  // Count by severity
  const severityCounts = results.reduce((acc, r) => {
    acc[r.final_grade] = (acc[r.final_grade] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading evaluation results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border-b border-purple-500/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between mb-4">
            <Link 
              href="/dashboard"
              className="text-purple-400 hover:text-purple-300 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Dashboard
            </Link>
          </div>
          
          <h1 className="text-4xl font-bold text-white mb-2">
            🔍 Detailed Test Results
          </h1>
          {roundInfo && (
            <p className="text-gray-300">
              Round {roundInfo.round_number} • {roundInfo.description || 'Evaluation Round'}
            </p>
          )}
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Summary */}
        <div className="mb-8 grid grid-cols-2 md:grid-cols-7 gap-3">
          <button
            onClick={() => setSelectedGrade('all')}
            className={`p-4 rounded-xl border transition-all ${
              selectedGrade === 'all' 
                ? 'bg-purple-500/30 border-purple-500' 
                : 'bg-card/30 border-purple-500/20 hover:border-purple-500/40'
            }`}
          >
            <div className="text-2xl font-bold text-white">{results.length}</div>
            <div className="text-xs text-gray-400">All Tests</div>
          </button>
          
          {['PASS', 'P4', 'P3', 'P2', 'P1', 'P0'].map(grade => (
            <button
              key={grade}
              onClick={() => setSelectedGrade(grade)}
              className={`p-4 rounded-xl border transition-all ${
                selectedGrade === grade 
                  ? getSeverityBgColor(grade)
                  : 'bg-card/30 border-purple-500/20 hover:border-purple-500/40'
              }`}
            >
              <div className={`text-2xl font-bold ${getSeverityColor(grade)}`}>
                {severityCounts[grade] || 0}
              </div>
              <div className="text-xs text-gray-400">{grade}</div>
            </button>
          ))}
        </div>

        {/* Results List */}
        <div className="space-y-4">
          <AnimatePresence mode="popLayout">
            {filteredResults.map((result, index) => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.03 }}
                className={`p-6 rounded-2xl border backdrop-blur-sm ${getSeverityBgColor(result.final_grade)}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`text-2xl font-bold ${getSeverityColor(result.final_grade)}`}>
                        {result.final_grade}
                      </span>
                      {result.scenario && (
                        <>
                          <span className="text-white font-semibold text-lg">
                            {result.scenario.category}
                          </span>
                          <span className="text-gray-400">→</span>
                          <span className="text-gray-300">{result.scenario.sub_category}</span>
                        </>
                      )}
                    </div>
                    {result.scenario && (
                      <p className="text-sm text-gray-400 mb-3">
                        <strong className="text-gray-300">Methodology:</strong> {result.scenario.methodology}
                      </p>
                    )}
                  </div>
                  
                  <button
                    onClick={() => setExpandedResult(expandedResult === result.id ? null : result.id)}
                    className="text-purple-400 hover:text-purple-300 transition-colors"
                  >
                    <svg 
                      className={`w-6 h-6 transition-transform ${expandedResult === result.id ? 'rotate-180' : ''}`}
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>

                {/* Test Prompt */}
                {result.scenario && (
                  <div className="mb-4 p-4 rounded-xl bg-background/50">
                    <p className="text-xs text-gray-400 mb-2 font-semibold">TEST PROMPT</p>
                    <p className="text-gray-300 text-sm">{result.scenario.input_prompt}</p>
                  </div>
                )}

                {/* System Response */}
                <div className="mb-4 p-4 rounded-xl bg-background/50">
                  <p className="text-xs text-gray-400 mb-2 font-semibold">SYSTEM RESPONSE</p>
                  <p className="text-white text-sm">{result.system_response}</p>
                </div>

                {/* Judge Grades */}
                <div className="flex gap-3 mb-3">
                  <div className="flex-1 text-center p-2 rounded-lg bg-background/30">
                    <div className={`text-sm font-bold ${getSeverityColor(result.judge_1_grade)}`}>
                      {result.judge_1_grade}
                    </div>
                    <div className="text-xs text-gray-400">Judge 1</div>
                  </div>
                  <div className="flex-1 text-center p-2 rounded-lg bg-background/30">
                    <div className={`text-sm font-bold ${getSeverityColor(result.judge_2_grade)}`}>
                      {result.judge_2_grade}
                    </div>
                    <div className="text-xs text-gray-400">Judge 2</div>
                  </div>
                  <div className="flex-1 text-center p-2 rounded-lg bg-background/30">
                    <div className={`text-sm font-bold ${getSeverityColor(result.judge_3_grade)}`}>
                      {result.judge_3_grade}
                    </div>
                    <div className="text-xs text-gray-400">Judge 3</div>
                  </div>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {expandedResult === result.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-4 space-y-4"
                    >
                      {/* Expected Behavior */}
                      {result.scenario && (
                        <div className="p-4 rounded-xl bg-background/50">
                          <p className="text-xs text-gray-400 mb-2 font-semibold">EXPECTED BEHAVIOR</p>
                          <p className="text-gray-300 text-sm">{result.scenario.expected_behavior}</p>
                        </div>
                      )}

                      {/* Judge Details */}
                      <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-white">Judge Evaluations</h4>
                        
                        {[
                          { grade: result.judge_1_grade, reasoning: result.judge_1_reasoning, recommendation: result.judge_1_recommendation, model: result.judge_1_model, num: 1 },
                          { grade: result.judge_2_grade, reasoning: result.judge_2_reasoning, recommendation: result.judge_2_recommendation, model: result.judge_2_model, num: 2 },
                          { grade: result.judge_3_grade, reasoning: result.judge_3_reasoning, recommendation: result.judge_3_recommendation, model: result.judge_3_model, num: 3 },
                        ].map(judge => (
                          <div key={judge.num} className="p-4 rounded-xl bg-background/30 border border-purple-500/10">
                            <div className="flex items-center justify-between mb-3">
                              <span className="text-sm font-semibold text-white">Judge {judge.num}</span>
                              <div className="flex items-center gap-3">
                                <span className="text-xs text-gray-400">{judge.model}</span>
                                <span className={`text-sm font-bold ${getSeverityColor(judge.grade)}`}>
                                  {judge.grade}
                                </span>
                              </div>
                            </div>
                            <div className="space-y-2">
                              <div>
                                <p className="text-xs text-gray-400 mb-1">Reasoning:</p>
                                <p className="text-sm text-gray-300">{judge.reasoning}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-400 mb-1">Recommendation:</p>
                                <p className="text-sm text-gray-300">{judge.recommendation}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>

          {filteredResults.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">
                No results found for {selectedGrade} tests.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

