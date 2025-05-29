// services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods
export const projectsApi = {
  getAll: () => apiClient.get('/projects'),
  getTestcasesByAuthor: (projectId) => 
    apiClient.get(`/project/${projectId}/testcases-by-author`),
  getAuthors: (projectId) => 
    apiClient.get(`/project/${projectId}/authors`),
};

export const authorsApi = {
  getTestcases: (author) => 
    apiClient.get(`/author/${author}/testcases`),
  getMetrics: (author, testcase = null) => {
    const url = testcase 
      ? `/author/${author}/metrics?testcase=${testcase}`
      : `/author/${author}/metrics`;
    return apiClient.get(url);
  },
  getWorkMetrics: (author) => 
    apiClient.get(`/author/${author}/work-metrics`),
};

// Error handling helper
export const handleApiError = (error, context = '') => {
  const message = error.response?.data?.message || error.message || 'An error occurred';
  console.error(`${context} Error:`, message);
  return message;
};

export default apiClient;