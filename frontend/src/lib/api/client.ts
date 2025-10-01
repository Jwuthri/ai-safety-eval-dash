/**
 * API Client for AI Safety Evaluation Dashboard
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiError {
  detail: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Helper to get the base URL (useful for direct fetch calls)
  getBaseUrl: () => API_BASE_URL,

  // Evaluations
  async getEvaluationRound(roundId: string) {
    const response = await fetch(`${API_BASE_URL}/evaluations/rounds/${roundId}`);
    return handleResponse(response);
  },

  async getRoundStatistics(roundId: string) {
    const response = await fetch(`${API_BASE_URL}/evaluations/rounds/${roundId}/stats`);
    return handleResponse(response);
  },

  async getRoundResults(roundId: string, limit = 100, offset = 0) {
    const response = await fetch(
      `${API_BASE_URL}/evaluations/rounds/${roundId}/results?limit=${limit}&offset=${offset}`
    );
    return handleResponse(response);
  },

  async getOrganizationRounds(orgId: string, limit = 10) {
    const response = await fetch(
      `${API_BASE_URL}/evaluations/organizations/${orgId}/rounds?limit=${limit}`
    );
    return handleResponse(response);
  },

  async getLatestRound(orgId: string) {
    const response = await fetch(
      `${API_BASE_URL}/evaluations/organizations/${orgId}/latest-round`
    );
    return handleResponse(response);
  },

  async startEvaluation(params: {
    organization_id: string;
    round_number: number;
    description?: string;
  }) {
    const response = await fetch(`${API_BASE_URL}/evaluations/rounds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return handleResponse(response);
  },

  async getCertificationEligibility(orgId: string, roundId: string) {
    const response = await fetch(
      `${API_BASE_URL}/certifications/organizations/${orgId}/eligibility?evaluation_round_id=${roundId}`
    );
    return handleResponse(response);
  },

  async getRoundsComparison(orgId: string) {
    const response = await fetch(
      `${API_BASE_URL}/comparisons/organizations/${orgId}/rounds-comparison`
    );
    return handleResponse(response);
  },

  // Organizations
  async getOrganizations() {
    const response = await fetch(`${API_BASE_URL}/organizations`);
    return handleResponse(response);
  },

  async createOrganization(data: any) {
    const response = await fetch(`${API_BASE_URL}/organizations/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async getOrganization(orgId: string) {
    const response = await fetch(`${API_BASE_URL}/organizations/${orgId}`);
    return handleResponse(response);
  },

  // Business Types
  async getBusinessTypes() {
    const response = await fetch(`${API_BASE_URL}/business-types`);
    return handleResponse(response);
  },

  // Scenarios
  async getScenarios(businessTypeId?: number) {
    const url = businessTypeId
      ? `${API_BASE_URL}/scenarios?business_type_id=${businessTypeId}`
      : `${API_BASE_URL}/scenarios`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  // Incidents
  async getIncidents(params?: Record<string, string>) {
    const queryParams = params ? `?${new URLSearchParams(params).toString()}` : '';
    const response = await fetch(`${API_BASE_URL}/incidents${queryParams}`);
    return handleResponse(response);
  },

  async getIncidentStatsSeverity(params?: Record<string, string>) {
    const queryParams = params ? `?${new URLSearchParams(params).toString()}` : '';
    const response = await fetch(`${API_BASE_URL}/incidents/stats/severity${queryParams}`);
    return handleResponse(response);
  },

  async getIncidentStatsHarmTypes(params?: Record<string, string>) {
    const queryParams = params ? `?${new URLSearchParams(params).toString()}` : '';
    const response = await fetch(`${API_BASE_URL}/incidents/stats/harm-types${queryParams}`);
    return handleResponse(response);
  },

  // Safeguards
  async getSafeguardsForIncident(incidentId: number) {
    const response = await fetch(`${API_BASE_URL}/safeguards/for-incident/${incidentId}`);
    return handleResponse(response);
  },
};