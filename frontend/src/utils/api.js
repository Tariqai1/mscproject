/**
 * API utility module for communicating with backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
api.interceptors.request.use(
  config => {
    // Add any auth headers here if needed
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Predict sentiment and sarcasm for a single review
 */
export const predictSentiment = async (text) => {
  try {
    const response = await api.post('/predict', { text });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Predict for multiple reviews
 */
export const batchPredict = async (texts) => {
  try {
    const response = await api.post('/batch-predict', { texts });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Upload a file (.txt or .csv) for batch prediction
 */
export const uploadFilePredict = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload-predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get prediction history
 */
export const getHistory = async (limit = 50) => {
  try {
    const response = await api.get('/history', { params: { limit } });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get model statistics
 */
export const getStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Health check
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Submit feedback on a prediction
 */
export const submitFeedback = async (predictionId, feedback) => {
  try {
    const response = await api.post('/feedback', {
      prediction_id: predictionId,
      ...feedback
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Export predictions as CSV
 */
export const exportAsCSV = async (limit = 500) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/export/csv`, {
      params: { limit },
      responseType: 'blob'
    });
    
    // Create blob and download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `predictions_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    throw error;
  }
};

/**
 * Export predictions as JSON
 */
export const exportAsJSON = async (limit = 500) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/export/json`, {
      params: { limit },
      responseType: 'blob'
    });
    
    // Create blob and download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `predictions_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    throw error;
  }
};

/**
 * Export predictions as PDF
 */
export const exportAsPDF = async (limit = 100) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/export/pdf`, {
      params: { limit },
      responseType: 'blob'
    });
    
    // Create blob and download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `predictions_report_${new Date().toISOString().split('T')[0]}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    throw error;
  }
};

/**
 * Fetch time-series analytics data
 */
export const fetchTimelineAnalytics = async (period = 'daily', days = 30) => {
  try {
    const response = await api.get('/analytics/timeline', {
      params: { period, days }
    });
    return response;
  } catch (error) {
    throw error;
  }
};

/**
 * Compare predictions from different models
 */
export const compareModels = async (text) => {
  try {
    const response = await api.post('/compare-models', { text });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;
