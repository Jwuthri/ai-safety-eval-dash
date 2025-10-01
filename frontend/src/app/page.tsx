'use client';

import { useEffect, useState } from 'react';
import Link from "next/link";
import { useRouter } from 'next/navigation';
import { useOrganization } from '@/contexts/OrganizationContext';
import { motion, AnimatePresence } from 'framer-motion';

export default function Home() {
  const router = useRouter();
  const { organizations, selectedOrg, setSelectedOrg, currentOrganization, loading } = useOrganization();
  const [showOrgSelector, setShowOrgSelector] = useState(false);

  useEffect(() => {
    // If org is already selected, could redirect to dashboard
    // For now, just show the selector option
  }, [selectedOrg]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-hero-gradient pt-20 pb-12">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(139,92,246,0.1),transparent_50%)]" />
        
        <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
          {/* Logo/Brand */}
          <div className="text-center mb-8">
            <h1 className="text-sm font-semibold tracking-[0.3em] text-gray-400 uppercase">
              AIUC-1 Certified Platform
            </h1>
          </div>

          {/* Main Headline */}
          <div className="text-center">
            <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6">
              <span className="bg-gradient-to-r from-purple-400 via-violet-400 to-purple-600 bg-clip-text text-transparent">
                Prevent the Next
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-violet-400 to-purple-600 bg-clip-text text-transparent">
                AirCanada Disaster
              </span>
            </h1>
            
            <p className="mt-6 text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
              Multi-round AI safety evaluation platform. Test, improve, and certify your AI agents 
              before they reach production.
            </p>
          </div>

          {/* Terminal Demo */}
          <div className="mt-16 mx-auto max-w-4xl">
            <div className="rounded-2xl bg-card/50 backdrop-blur-sm border border-purple-500/20 shadow-purple-glow overflow-hidden">
              {/* Terminal Header */}
              <div className="flex items-center gap-2 px-4 py-3 bg-card/80 border-b border-purple-500/20">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className="flex-1 text-center">
                  <span className="text-sm text-gray-400 font-mono">ai-safety-terminal</span>
                </div>
              </div>

              {/* Terminal Content */}
              <div className="p-6 font-mono text-sm md:text-base">
                <div className="flex items-center gap-2 text-green-400">
                  <span>$</span>
                  <span className="text-purple-400">evaluate</span>
                  <span className="text-gray-300">--organization</span>
                  <span className="text-blue-400">"AirCanada"</span>
                  <span className="text-gray-300">--round</span>
                  <span className="text-blue-400">1</span>
                  <span className="animate-pulse">▊</span>
                </div>
                <div className="mt-4 text-gray-400 space-y-1">
                  <div>✓ Running 314 safety scenarios...</div>
                  <div>✓ 3 LLM judges: Claude Sonnet 4.5, GPT-5, Grok-4</div>
                  <div className="text-purple-400">→ Pass Rate: 77.9% → 94.1% → 97.4%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Organization Selector */}
          <div className="mt-12 mx-auto max-w-lg">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-white mb-2">Select Your Organization</h3>
              <p className="text-gray-400">Choose which organization to evaluate</p>
            </div>

            {organizations.length === 0 ? (
              <div className="p-8 rounded-2xl bg-card/50 border border-purple-500/20 text-center">
                <p className="text-gray-400 mb-4">No organizations found</p>
                <Link
                  href="/dashboard"
                  className="text-purple-400 hover:text-purple-300 font-medium"
                >
                  Create one in Dashboard →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {organizations.map((org) => (
                  <motion.button
                    key={org.id}
                    onClick={() => {
                      setSelectedOrg(org.id);
                      setTimeout(() => router.push('/dashboard'), 300);
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full p-6 rounded-xl border-2 text-left transition-all ${
                      selectedOrg === org.id
                        ? 'bg-purple-600/20 border-purple-500 shadow-lg shadow-purple-500/20'
                        : 'bg-card/30 border-purple-500/20 hover:border-purple-500/50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-xl font-semibold text-white mb-1">{org.name}</h4>
                        <p className="text-sm text-gray-400">{org.slug}</p>
                      </div>
                      {selectedOrg === org.id && (
                        <div className="flex items-center gap-2 text-green-400">
                          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            )}

            {currentOrganization && (
              <div className="mt-6 text-center">
                <Link
                  href="/dashboard"
                  className="group relative inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-purple-600 rounded-xl hover:bg-purple-700 transition-all duration-200 shadow-lg hover:shadow-purple-glow"
                >
                  Continue to Dashboard
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              </div>
            )}
          </div>

          {/* Trust Badges */}
          <div className="mt-16 flex flex-wrap justify-center items-center gap-8 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span>AIUC-1 Certified</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-purple-500" />
              <span>10,000+ Evaluations</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span>Fortune 1000 Trusted</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 bg-background">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group relative p-8 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/10 hover:border-purple-500/30 transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6 group-hover:bg-purple-500/20 transition-colors">
                <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Multi-Turn Testing</h3>
              <p className="text-gray-400 leading-relaxed">
                Comprehensive conversational red-teaming with 3 parallel LLM judges for diverse evaluation perspectives.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group relative p-8 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/10 hover:border-purple-500/30 transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6 group-hover:bg-purple-500/20 transition-colors">
                <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Real Incidents</h3>
              <p className="text-gray-400 leading-relaxed">
                Tests grounded in real-world failures like AirCanada. Map incidents to preventive measures and comprehensive testing.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group relative p-8 rounded-2xl bg-card/30 backdrop-blur-sm border border-purple-500/10 hover:border-purple-500/30 transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6 group-hover:bg-purple-500/20 transition-colors">
                <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Track Progress</h3>
              <p className="text-gray-400 leading-relaxed">
                Visual dashboards show improvement trajectory across rounds. From 77.9% to 100% pass rate with AIUC-1 certification.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-card/20">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-violet-600 bg-clip-text text-transparent mb-2">
                10K+
              </div>
              <div className="text-gray-400">Evaluations Run</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-violet-600 bg-clip-text text-transparent mb-2">
                97.4%
              </div>
              <div className="text-gray-400">Peak Pass Rate</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-violet-600 bg-clip-text text-transparent mb-2">
                50+
              </div>
              <div className="text-gray-400">Incident Types</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-violet-600 bg-clip-text text-transparent mb-2">
                3
              </div>
              <div className="text-gray-400">LLM Judges</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-purple-500/10 py-12 bg-background">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-gray-400 text-sm">
              © 2025 AI Safety Evaluation Dashboard. Built for enterprise trust.
            </div>
            <div className="flex gap-6">
              <Link href="/docs" className="text-gray-400 hover:text-purple-400 transition-colors text-sm">
                Documentation
              </Link>
              <Link href="/api" className="text-gray-400 hover:text-purple-400 transition-colors text-sm">
                API
              </Link>
              <Link href="/certification" className="text-gray-400 hover:text-purple-400 transition-colors text-sm">
                AIUC-1
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}