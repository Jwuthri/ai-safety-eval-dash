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

  // Organizations
  async getOrganizations() {
    const response = await fetch(`${API_BASE_URL}/organizations`);
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
};