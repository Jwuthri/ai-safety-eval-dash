/**
 * Types for Safety Story Dashboard
 * 
 * Maps: Incidents → Safeguards → Tests → Residual Risk
 */

export type SeverityLevel = 'P0' | 'P1' | 'P2' | 'P3' | 'P4' | 'PASS';

export type HarmType = 
  | 'financial_loss'
  | 'reputation_damage'
  | 'privacy_breach'
  | 'safety_risk'
  | 'compliance_violation'
  | 'service_disruption';

export interface AIIncident {
  id: string;
  incident_name: string;
  company: string;
  date_occurred?: string;
  harm_type: HarmType;
  severity: SeverityLevel;
  description: string;
  root_cause?: string;
  impact_description?: string;
  estimated_cost?: number;
  affected_users?: number;
  source_url?: string;
  incident_reference?: string;
  business_type_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface SafetyStoryData {
  // Real-world incidents
  incidents: AIIncident[];
  incident_count_by_severity: Record<SeverityLevel, number>;
  incident_count_by_harm_type: Record<HarmType, number>;
  
  // Safeguards (AIUC-1)
  aiuc_compliance: {
    is_eligible: boolean;
    pass_rate: number;
    requirements: Record<string, boolean>;
  };
  
  // Tests (evaluation coverage)
  test_coverage: {
    total_scenarios: number;
    scenarios_mapped_to_incidents: number;
    coverage_percentage: number;
  };
  
  // Residual risk
  residual_risk: {
    unmitigated_incidents: number;
    risk_score: number;  // 0-100, lower is better
    open_p0_failures: number;
    open_p1_failures: number;
  };
}

export interface IncidentCardProps {
  incident: AIIncident;
  showDetails?: boolean;
  onViewDetails?: (incident: AIIncident) => void;
}

export interface GeneratedScenario {
  id: string;
  organization_id: string;
  business_type_id: string;
  category: string | null;
  sub_category: string | null;
  input_topic: string | null;
  methodology: string | null;
  input_prompt: string;
  expected_behavior: string | null;
  tactics: string[];
  use_case: string | null;
  incident_reference: string | null;
  generation_prompt: string | null;
  model_used: string | null;
  created_at: string;
}

export interface GenerateScenarioRequest {
  organization_id: string;
  count: number;
}

export interface GenerateScenarioResponse {
  organization_id: string;
  scenarios_generated: number;
  scenarios: GeneratedScenario[];
}

