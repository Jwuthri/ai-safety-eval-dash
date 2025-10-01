export interface Organization {
  id: string;
  name: string;
  slug: string;
  business_type_id: string;
  contact_email?: string;
  contact_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessType {
  id: string;
  name: string;
  industry: string;
  use_cases: string[];
  context?: string;
  created_at: string;
}

export interface EvaluationRound {
  id: string;
  organization_id: string;
  round_number: number;
  description?: string;
  status: 'running' | 'completed' | 'under_review' | 'failed';
  started_at: string;
  completed_at?: string;
}

export interface RoundStatistics {
  round_id: string;
  total_tests: number;
  pass_count: number;
  pass_rate: number;
  severity_breakdown: {
    PASS: number;
    P0: number;
    P1: number;
    P2: number;
    P3: number;
    P4: number;
  };
}

export interface EvaluationResult {
  id: string;
  evaluation_round_id: string;
  scenario_id: string;
  system_response: string;
  final_grade: 'PASS' | 'P0' | 'P1' | 'P2' | 'P3' | 'P4';
  
  // Judge 1 (Claude Sonnet 4.5)
  judge_1_grade: string;
  judge_1_reasoning: string;
  judge_1_recommendation: string;
  judge_1_model: string;
  
  // Judge 2 (GPT-5)
  judge_2_grade: string;
  judge_2_reasoning: string;
  judge_2_recommendation: string;
  judge_2_model: string;
  
  // Judge 3 (Grok-4 Fast)
  judge_3_grade: string;
  judge_3_reasoning: string;
  judge_3_recommendation: string;
  judge_3_model: string;
  
  created_at: string;
}

export type SeverityGrade = 'PASS' | 'P0' | 'P1' | 'P2' | 'P3' | 'P4';

export const SEVERITY_COLORS: Record<SeverityGrade, string> = {
  PASS: '#10b981',
  P4: '#fbbf24',
  P3: '#f97316',
  P2: '#f59e0b',
  P1: '#dc2626',
  P0: '#7f1d1d',
};

export const SEVERITY_LABELS: Record<SeverityGrade, string> = {
  PASS: 'Pass',
  P4: 'P4 - Trivial',
  P3: 'P3 - Moderate',
  P2: 'P2 - Serious',
  P1: 'P1 - Critical',
  P0: 'P0 - Catastrophic',
};
