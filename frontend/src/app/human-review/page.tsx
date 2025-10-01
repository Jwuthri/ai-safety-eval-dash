'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'

export const dynamic = 'force-dynamic';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface LowConfidenceResult {
  id: string
  evaluation_round_id: string
  scenario_id: string
  final_grade: string
  confidence_score: number
  judge_1_grade: string
  judge_2_grade: string
  judge_3_grade: string
  has_human_review: boolean
  created_at: string
}

const SEVERITY_GRADES = ['PASS', 'P4', 'P3', 'P2', 'P1', 'P0']

const SEVERITY_COLORS: Record<string, string> = {
  PASS: 'text-green-500',
  P4: 'text-yellow-400',
  P3: 'text-orange-500',
  P2: 'text-red-500',
  P1: 'text-red-700',
  P0: 'text-red-900',
}

function HumanReviewContent() {
  const searchParams = useSearchParams()
  const roundId = searchParams?.get('round_id')
  
  const [results, setResults] = useState<LowConfidenceResult[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedResult, setSelectedResult] = useState<LowConfidenceResult | null>(null)
  const [selectedGrade, setSelectedGrade] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchLowConfidenceResults()
  }, [roundId])

  const fetchLowConfidenceResults = async () => {
    try {
      const url = roundId 
        ? `${API_URL}/human-reviews/low-confidence?round_id=${roundId}&min_confidence=99`
        : `${API_URL}/human-reviews/low-confidence?min_confidence=99`
      
      const response = await fetch(url)
      if (!response.ok) throw new Error('Failed to fetch results')
      
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Error fetching low-confidence results:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitReview = async () => {
    if (!selectedResult || !selectedGrade) return

    setSubmitting(true)
    try {
      const response = await fetch(`${API_URL}/human-reviews/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evaluation_result_id: selectedResult.id,
          reviewed_grade: selectedGrade,
          review_notes: notes || null,
          reviewer_name: 'Admin' // TODO: Get from auth
        })
      })

      if (!response.ok) throw new Error('Failed to submit review')

      // Refresh results and close modal
      await fetchLowConfidenceResults()
      setSelectedResult(null)
      setSelectedGrade('')
      setNotes('')
    } catch (error) {
      console.error('Error submitting review:', error)
      alert('Failed to submit review')
    } finally {
      setSubmitting(false)
    }
  }

  const unreviewed = results.filter(r => !r.has_human_review)
  const reviewed = results.filter(r => r.has_human_review)

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard" className="text-purple-400 hover:text-purple-300 mb-4 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Human in the Loop Review</h1>
          <p className="text-gray-400">
            Review evaluation results where judges disagreed (confidence &lt; 100%)
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-card/30 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="text-3xl font-bold text-white mb-1">{unreviewed.length}</div>
            <div className="text-sm text-gray-400">Needs Review</div>
          </div>
          <div className="bg-card/30 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="text-3xl font-bold text-green-500 mb-1">{reviewed.length}</div>
            <div className="text-sm text-gray-400">Reviewed</div>
          </div>
          <div className="bg-card/30 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="text-3xl font-bold text-white mb-1">{results.length}</div>
            <div className="text-sm text-gray-400">Total</div>
          </div>
        </div>

        {/* Results List */}
        <div className="bg-card/30 backdrop-blur-sm border border-purple-500/20 rounded-2xl p-6">
          <h2 className="text-2xl font-semibold text-white mb-6">Results Needing Review</h2>
          
          {unreviewed.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              All low-confidence results have been reviewed! 🎉
            </div>
          ) : (
            <div className="space-y-4">
              {unreviewed.map(result => (
                <div 
                  key={result.id}
                  className="bg-background/50 rounded-xl p-6 border border-purple-500/10"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-3">
                        <div className="text-sm text-gray-500">
                          Confidence: <span className="text-amber-500 font-semibold">{result.confidence_score}%</span>
                        </div>
                        <div className="text-sm text-gray-500">
                          Current Grade: <span className={`font-semibold ${SEVERITY_COLORS[result.final_grade]}`}>
                            {result.final_grade}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex gap-4 text-sm">
                        <div>Judge 1: <span className={SEVERITY_COLORS[result.judge_1_grade]}>{result.judge_1_grade}</span></div>
                        <div>Judge 2: <span className={SEVERITY_COLORS[result.judge_2_grade]}>{result.judge_2_grade}</span></div>
                        <div>Judge 3: <span className={SEVERITY_COLORS[result.judge_3_grade]}>{result.judge_3_grade}</span></div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => {
                        setSelectedResult(result)
                        setSelectedGrade(result.final_grade)
                      }}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      Review
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Review Modal */}
      {selectedResult && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-card border border-purple-500/20 rounded-2xl p-8 max-w-2xl w-full">
            <h3 className="text-2xl font-bold text-white mb-6">Review Evaluation Result</h3>
            
            <div className="mb-6">
              <div className="text-sm text-gray-400 mb-2">Judge Grades:</div>
              <div className="flex gap-4 mb-4">
                <div className={`px-4 py-2 rounded-lg ${SEVERITY_COLORS[selectedResult.judge_1_grade]}`}>
                  Judge 1: {selectedResult.judge_1_grade}
                </div>
                <div className={`px-4 py-2 rounded-lg ${SEVERITY_COLORS[selectedResult.judge_2_grade]}`}>
                  Judge 2: {selectedResult.judge_2_grade}
                </div>
                <div className={`px-4 py-2 rounded-lg ${SEVERITY_COLORS[selectedResult.judge_3_grade]}`}>
                  Judge 3: {selectedResult.judge_3_grade}
                </div>
              </div>
              <div className="text-sm text-gray-400">
                Current Confidence: <span className="text-amber-500">{selectedResult.confidence_score}%</span>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Your Grade Decision
              </label>
              <div className="grid grid-cols-6 gap-2">
                {SEVERITY_GRADES.map(grade => (
                  <button
                    key={grade}
                    onClick={() => setSelectedGrade(grade)}
                    className={`px-4 py-2 rounded-lg border ${
                      selectedGrade === grade
                        ? 'border-purple-500 bg-purple-600/20'
                        : 'border-gray-600 hover:border-gray-500'
                    } ${SEVERITY_COLORS[grade]} transition-colors`}
                  >
                    {grade}
                  </button>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Review Notes (Optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full px-4 py-3 bg-background border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                rows={4}
                placeholder="Add your reasoning for this grade..."
              />
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleSubmitReview}
                disabled={!selectedGrade || submitting}
                className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Submitting...' : 'Submit Review'}
              </button>
              <button
                onClick={() => {
                  setSelectedResult(null)
                  setSelectedGrade('')
                  setNotes('')
                }}
                className="px-6 py-3 bg-gray-600 text-white rounded-xl hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function HumanReviewPage() {
  return (
    <Suspense fallback={<div className="container mx-auto p-8">Loading...</div>}>
      <HumanReviewContent />
    </Suspense>
  )
}
