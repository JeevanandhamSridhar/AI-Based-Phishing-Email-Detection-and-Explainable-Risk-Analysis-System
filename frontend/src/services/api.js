/**
 * API Service Client for PhishGuard SOC
 * Connects to local FastAPI backend via Vite reverse-proxy (/api)
 */

const BASE_URL = '/api';

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || JSON.stringify(errorJson);
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export const api = {
  // Health & System status
  async getHealth() {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse(res);
  },

  // Analysis endpoints
  async analyzeEmail(rawEmail, fileName = 'manual_input.eml') {
    const res = await fetch(`${BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        raw_email: rawEmail,
        file_name: fileName,
      }),
    });
    return handleResponse(res);
  },

  async analyzeUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/analyze/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  // Presets & Samples
  async getSamples() {
    const res = await fetch(`${BASE_URL}/samples`);
    return handleResponse(res);
  },

  // Investigation History
  async getHistory(page = 1, limit = 20, severity = null) {
    let url = `${BASE_URL}/history?page=${page}&limit=${limit}`;
    if (severity && severity !== 'ALL') {
      url += `&severity=${encodeURIComponent(severity)}`;
    }
    const res = await fetch(url);
    return handleResponse(res);
  },

  async getHistoryDetail(analysisId) {
    const res = await fetch(`${BASE_URL}/history/${analysisId}`);
    return handleResponse(res);
  },

  // Model & Experimental Telemetry
  async getModelPerformance() {
    const res = await fetch(`${BASE_URL}/models/performance`);
    return handleResponse(res);
  },

  async getAuthorshipEvaluation() {
    const res = await fetch(`${BASE_URL}/authorship/evaluate`);
    return handleResponse(res);
  },

  async getAdversarialEvaluation() {
    const res = await fetch(`${BASE_URL}/adversarial/evaluate`);
    return handleResponse(res);
  },

  // PDF Report Download URL
  getPdfDownloadUrl(analysisId) {
    return `${BASE_URL}/reports/download/${analysisId}`;
  },
};
