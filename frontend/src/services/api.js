import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Get session results by ID
 * @param {string} sessionId - Session UUID
 * @returns {Promise<object>} Session data with candidates, stats, etc.
 */
export const getSession = async (sessionId) => {
  const response = await api.get(`/sessions/${sessionId}`);
  return response.data;
};

/**
 * Analyze resumes for a role
 * @param {FormData} formData - Form data with role_title, job_description, weights, thresholds, files
 * @returns {Promise<object>} Analysis results
 */
export const analyzeResumes = async (formData) => {
  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

/**
 * Compare two candidates side by side
 * @param {string} sessionId - Session UUID
 * @param {string} candidateId1 - First candidate UUID
 * @param {string} candidateId2 - Second candidate UUID
 * @returns {Promise<object>} Comparison data with AI explanation
 */
export const compareCandidates = async (sessionId, candidateId1, candidateId2) => {
  const response = await api.post('/compare', {
    session_id: sessionId,
    candidate_id_1: candidateId1,
    candidate_id_2: candidateId2
  });
  return response.data;
};

/**
 * Send interview invitation emails to candidates
 * @param {object} data - Email data
 * @param {string} data.session_id - Session UUID
 * @param {Array} data.candidate_emails - Array of {name, email} objects
 * @param {Array} data.interview_slots - Array of {date, time} objects
 * @param {string} data.message_template - Email template with placeholders
 * @param {string} data.job_title - Job title for email
 * @param {string} data.company - Company name for email
 * @returns {Promise<object>} Send results with sent/failed counts
 */
export const sendEmails = async (data) => {
  const response = await api.post('/send-emails', data);
  return response.data;
};

/**
 * Get all roles with candidate counts
 * @returns {Promise<object>} Roles list
 */
export const getRoles = async () => {
  const response = await api.get('/roles');
  return response.data;
};

/**
 * Get all sessions with role info
 * @returns {Promise<object>} Sessions list
 */
export const getSessions = async () => {
  const response = await api.get('/sessions');
  return response.data;
};

/**
 * Get candidates for a specific role pool
 * @param {string} roleId - Role UUID
 * @returns {Promise<object>} Candidates list
 */
export const getRoleCandidates = async (roleId) => {
  const response = await api.get(`/roles/${roleId}/candidates`);
  return response.data;
};

/**
 * Create or get existing role
 * @param {string} title - Role title
 * @param {object} weights - Optional weight configuration
 * @returns {Promise<object>} Role data
 */
export const createRole = async (title, weights = null) => {
  const response = await api.post('/roles', { title, weights });
  return response.data;
};

export default api;
