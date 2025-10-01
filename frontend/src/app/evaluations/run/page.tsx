'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useOrganization } from '@/contexts/OrganizationContext';

export default function RunEvaluationPage() {
  const router = useRouter();
  const { currentOrganization, loading: orgLoading } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [latestRound, setLatestRound] = useState<number>(0);
  const [roundNumber, setRoundNumber] = useState<number>(1);
  const [description, setDescription] = useState<string>('');
  const [useFakeJudges, setUseFakeJudges] = useState(true);
  const [progress, setProgress] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [currentScenario, setCurrentScenario] = useState<string>('');
  const [percentage, setPercentage] = useState<number>(0);
  const [currentTest, setCurrentTest] = useState<number>(0);
  const [totalTests, setTotalTests] = useState<number>(0);
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [eligibilityResult, setEligibilityResult] = useState<any>(null);
  const [showEligibilityModal, setShowEligibilityModal] = useState(false);

  useEffect(() => {
    if (currentOrganization) {
      loadRoundData();
    }
  }, [currentOrganization]);

  async function loadRoundData() {
    if (!currentOrganization) return;
    
    try {
      // Get latest round number
      const roundsResponse = await fetch(`http://localhost:8000/api/v1/evaluations/organizations/${currentOrganization.id}/rounds`);
      const rounds = await roundsResponse.json();
      
      if (rounds.length > 0) {
        const maxRound = Math.max(...rounds.map((r: any) => r.round_number));
        setLatestRound(maxRound);
        setRoundNumber(maxRound + 1);
        setDescription(`Round ${maxRound + 1} - Continued safety improvements`);
      } else {
        setRoundNumber(1);
        setDescription('Round 1 - Initial safety evaluation');
      }
    } catch (error) {
      console.error('Failed to load rounds:', error);
      setError('Failed to load round data');
    } finally {
      setLoading(false);
    }
  }

  async function checkEligibility() {
    if (!currentOrganization) return;
    
    setCheckingEligibility(true);
    setError('');
    
    try {
      // Get latest completed round
      console.log('Fetching rounds for org:', currentOrganization.id);
      const roundsResponse = await fetch(`http://localhost:8000/api/v1/evaluations/organizations/${currentOrganization.id}/rounds`);
      
      if (!roundsResponse.ok) {
        throw new Error(`Failed to fetch rounds: ${roundsResponse.status} ${roundsResponse.statusText}`);
      }
      
      const rounds = await roundsResponse.json();
      console.log('Rounds:', rounds);
      
      const completedRounds = rounds.filter((r: any) => r.status === 'completed');
      console.log('Completed rounds:', completedRounds);
      
      if (completedRounds.length === 0) {
        setError('No completed evaluation rounds found. Please run an evaluation first.');
        setCheckingEligibility(false);
        return;
      }
      
      // Get the latest round
      const latestRound = completedRounds.sort((a: any, b: any) => b.round_number - a.round_number)[0];
      console.log('Latest round:', latestRound);
      
      // Check eligibility
      const eligibilityUrl = `http://localhost:8000/api/v1/certifications/organizations/${currentOrganization.id}/eligibility?evaluation_round_id=${latestRound.id}`;
      console.log('Checking eligibility at:', eligibilityUrl);
      
      const eligibilityResponse = await fetch(eligibilityUrl);
      
      if (!eligibilityResponse.ok) {
        const errorText = await eligibilityResponse.text();
        console.error('Eligibility check failed:', errorText);
        throw new Error(`Failed to check eligibility: ${eligibilityResponse.status} - ${errorText}`);
      }
      
      const eligibility = await eligibilityResponse.json();
      console.log('Eligibility result:', eligibility);
      
      setEligibilityResult(eligibility);
      setShowEligibilityModal(true);
    } catch (error: any) {
      console.error('Failed to check eligibility:', error);
      setError(error.message || 'Failed to check AIUC-1 eligibility');
    } finally {
      setCheckingEligibility(false);
    }
  }

  async function startEvaluation() {
    if (!currentOrganization) return;
    
    setRunning(true);
    setError('');
    setProgress('🚀 Connecting to evaluation service...');
    setPercentage(0);
    setCurrentTest(0);
    setTotalTests(0);
    setCurrentScenario('');

    try {
      // Connect to WebSocket
      const ws = new WebSocket('ws://localhost:8000/api/v1/evaluations/ws/run');

      ws.onopen = () => {
        setProgress('✅ Connected! Starting evaluation...');
        
        // Send evaluation request
        ws.send(JSON.stringify({
          organization_id: currentOrganization.id,
          round_number: roundNumber,
          description: description,
          use_fake_judges: useFakeJudges
        }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Ignore keepalive pings
        if (data.type === 'ping') {
          return;
        }
        
        if (data.type === 'started') {
          setProgress(`🚀 Evaluation Round ${data.round_number} started`);
        } 
        else if (data.type === 'progress') {
          setCurrentTest(data.current);  // Backend already sends 1-indexed value
          setTotalTests(data.total);
          setPercentage(data.percentage);
          setCurrentScenario(data.current_scenario);
          
          if (data.status === 'evaluating') {
            setProgress(`🔍 Evaluating: ${data.current_scenario}...`);
          } else if (data.status === 'completed' && data.current_grade) {
            const gradeEmoji = data.current_grade === 'PASS' ? '✅' : 
                              data.current_grade === 'P0' ? '🔴' :
                              data.current_grade === 'P1' ? '🟠' :
                              data.current_grade === 'P2' ? '🟡' :
                              data.current_grade === 'P3' ? '🟢' : '🔵';
            setProgress(`${gradeEmoji} ${data.current_scenario}: ${data.current_grade}`);
          }
        }
        else if (data.type === 'complete') {
          setProgress('✅ Evaluation complete!');
          setPercentage(100);
          ws.close();
          
          // Redirect to dashboard after 2 seconds
          setTimeout(() => {
            router.push('/dashboard');
          }, 2000);
        }
        else if (data.type === 'error') {
          throw new Error(data.message);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error occurred');
        setRunning(false);
        ws.close();
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
      };

    } catch (error: any) {
      console.error('Evaluation failed:', error);
      setError(error.message || 'Failed to run evaluation');
      setRunning(false);
    }
  }

  if (orgLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!currentOrganization) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🏢</div>
          <h3 className="text-2xl font-bold text-white mb-2">No Organization Selected</h3>
          <p className="text-gray-400 mb-6">Please select an organization from the dashboard first.</p>
          <Link
            href="/dashboard"
            className="inline-block px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all font-semibold"
          >
            Go to Dashboard
          </Link>
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
                <Link href="/evaluations/run" className="text-purple-400 font-medium">
                  Run Evaluation
                </Link>
                <Link href="/taxonomy" className="text-gray-400 hover:text-purple-400 transition-colors">
                  Taxonomy
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">{currentOrganization?.name}</span>
              <div className="w-2 h-2 rounded-full bg-green-500" />
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 lg:px-8 py-12">
        {/* Page Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold gradient-text mb-4">Run New Evaluation</h1>
          <p className="text-xl text-gray-400">
            Execute comprehensive AI safety testing across all scenarios
          </p>
        </div>

        {/* Configuration Form */}
        <div className="p-8 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/20 mb-8">
          <h2 className="text-2xl font-semibold text-white mb-6">⚙️ Configuration</h2>
          
          <div className="space-y-6">
            {/* Organization */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Organization
              </label>
              <div className="p-4 rounded-xl bg-background/50 border border-purple-500/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{currentOrganization?.name}</p>
                    <p className="text-sm text-gray-400">ID: {currentOrganization?.id.slice(0, 8)}...</p>
                  </div>
                  <div className="px-3 py-1 rounded-lg bg-purple-500/20 text-purple-300 text-sm">
                    Active
                  </div>
                </div>
              </div>
            </div>

            {/* Round Number */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Round Number
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="number"
                  min="1"
                  value={roundNumber}
                  onChange={(e) => setRoundNumber(parseInt(e.target.value))}
                  disabled={running}
                  className="flex-1 px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50"
                />
                {latestRound > 0 && (
                  <span className="text-sm text-gray-400">
                    Latest: Round {latestRound}
                  </span>
                )}
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={running}
                rows={3}
                placeholder="Describe what changes or improvements were made..."
                className="w-full px-4 py-3 bg-background border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50 resize-none"
              />
            </div>

            {/* Use Fake Judges Toggle */}
            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30">
              <div className="flex items-start gap-4">
                <div className="flex items-center h-6">
                  <input
                    type="checkbox"
                    id="fake-judges"
                    checked={useFakeJudges}
                    onChange={(e) => setUseFakeJudges(e.target.checked)}
                    disabled={running}
                    className="w-5 h-5 rounded border-purple-500/50 bg-background text-purple-600 focus:ring-purple-500 focus:ring-offset-0 disabled:opacity-50"
                  />
                </div>
                <div className="flex-1">
                  <label htmlFor="fake-judges" className="text-white font-medium cursor-pointer">
                    Demo Mode (Fake Judges)
                  </label>
                  <p className="text-sm text-gray-400 mt-1">
                    Use simulated judge responses instead of real LLM API calls. Perfect for testing and demos - completely free!
                  </p>
                  {!useFakeJudges && (
                    <p className="text-sm text-yellow-400 mt-2">
                      ⚠️ Real mode will use OpenRouter API credits (Gemini 2.5 Flash Lite, GPT-5, Grok-4)
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress/Error Display */}
        {(progress || error) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            {progress && (
              <div className="p-6 rounded-2xl bg-purple-500/10 border border-purple-500/30">
                {/* Progress Bar */}
                {running && percentage > 0 && (
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-300">
                        {currentTest > 0 && totalTests > 0 && `Test ${currentTest} of ${totalTests}`}
                      </span>
                      <span className="text-sm font-bold text-purple-400">
                        {percentage.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-background/50 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 0.3 }}
                        className="h-full bg-gradient-to-r from-purple-600 via-purple-500 to-pink-500 rounded-full"
                      />
                    </div>
                    {currentScenario && (
                      <p className="text-xs text-gray-400 mt-2">
                        Currently testing: <span className="text-purple-300 font-medium">{currentScenario}</span>
                      </p>
                    )}
                  </div>
                )}
                <div className="flex items-center gap-4">
                  {running && (
                    <div className="w-6 h-6 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
                  )}
                  <p className="text-white font-medium">{progress}</p>
                </div>
              </div>
            )}
            
            {error && (
              <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30">
                <div className="flex items-center gap-4">
                  <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-red-300 font-medium">{error}</p>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={startEvaluation}
            disabled={running || !currentOrganization}
            className="flex-1 inline-flex items-center justify-center gap-3 px-8 py-4 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all shadow-lg hover:shadow-purple-glow disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg"
          >
            {running ? (
              <>
                <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
                Running Evaluation...
              </>
            ) : (
              <>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Start Evaluation
              </>
            )}
          </button>

          <button
            onClick={checkEligibility}
            disabled={checkingEligibility || !currentOrganization}
            className="flex-1 inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg"
          >
            {checkingEligibility ? (
              <>
                <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
                Checking...
              </>
            ) : (
              <>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Check AIUC-1 Eligibility
              </>
            )}
          </button>
          
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-card/50 border border-purple-500/20 text-white rounded-xl hover:border-purple-500/40 transition-all"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Cancel
          </Link>
        </div>

        {/* Info Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-card/20 border border-purple-500/10">
            <div className="text-3xl mb-2">🎯</div>
            <h3 className="text-white font-medium mb-1">Comprehensive Testing</h3>
            <p className="text-sm text-gray-400">Runs all test scenarios for your organization</p>
          </div>
          
          <div className="p-4 rounded-xl bg-card/20 border border-purple-500/10">
            <div className="text-3xl mb-2">⚖️</div>
            <h3 className="text-white font-medium mb-1">3 LLM Judges</h3>
            <p className="text-sm text-gray-400">Claude, GPT, and Grok evaluate in parallel</p>
          </div>
          
          <div className="p-4 rounded-xl bg-card/20 border border-purple-500/10">
            <div className="text-3xl mb-2">📊</div>
            <h3 className="text-white font-medium mb-1">Detailed Results</h3>
            <p className="text-sm text-gray-400">Get P0-P4 severity breakdown and insights</p>
          </div>
        </div>

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
                        Evaluation Round {eligibilityResult.evaluation_round_id.slice(0, 8)}...
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
                        <div className={`text-2xl font-bold ${
                          severity === 'PASS' ? 'text-green-400' :
                          severity === 'P0' ? 'text-red-500' :
                          severity === 'P1' ? 'text-orange-500' :
                          severity === 'P2' ? 'text-yellow-500' :
                          severity === 'P3' ? 'text-blue-400' : 'text-purple-400'
                        }`}>
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
      </main>
    </div>
  );
}

