import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (sessionId, message) => {
    const response = await api.post('/api/chat', {
      session_id: sessionId,
      message: message,
    });
    return response.data;
  },
};

export const analyticsService = {
  getDashboard: async (hours = 24) => {
    const response = await api.get(`/api/analytics/dashboard?hours=${hours}`);
    return response.data;
  },
  
  getSession: async (sessionId) => {
    const response = await api.get(`/api/analytics/session/${sessionId}`);
    return response.data;
  },
  
  getRateLimits: async (sessionId) => {
    const response = await api.get(`/api/analytics/rate-limits/${sessionId}`);
    return response.data;
  },
  
  submitRating: async (sessionId, rating) => {
    const response = await api.post('/api/feedback/rating', {
      session_id: sessionId,
      rating: rating,
    });
    return response.data;
  },
};

export default api;
