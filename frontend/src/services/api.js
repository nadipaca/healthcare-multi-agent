import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE}/api/patient/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const response = await axios.post(`${API_BASE}/api/patient/login`, {
      email,
      password,
    });

    // Store tokens
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return response.data;
  },

  register: async (userData) => {
    const response = await axios.post(`${API_BASE}/api/patient/register`, userData);

    // Store tokens
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/patient/me');
    return response.data;
  },
};

export const fileService = {
  uploadPrescription: async (file, rxId, notes) => {
    const formData = new FormData();
    formData.append('file', file);
    if (rxId) formData.append('rx_id', rxId);
    if (notes) formData.append('notes', notes);

    const response = await api.post('/api/patient/upload/prescription', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  uploadLabResult: async (file, testName, notes) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('test_name', testName);
    if (notes) formData.append('notes', notes);

    const response = await api.post('/api/patient/upload/lab-result', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getPatientFiles: async (patientId, fileType = null) => {
    const params = fileType ? { file_type: fileType } : {};
    const response = await api.get(`/api/patient/files/${patientId}`, { params });
    return response.data;
  },

  deleteFile: async (fileId) => {
    const response = await api.delete(`/api/patient/file/${fileId}`);
    return response.data;
  },
};


export const chatService = {
  sendMessage: async (sessionId, message, patientContext = {}) => {
    const payload = {
      session_id: sessionId,
      message: message,
    };

    // Include patient_id if available
    if (patientContext && patientContext.patient_id) {
      payload.patient_id = patientContext.patient_id;
    }

    const response = await api.post('/api/chat', payload);
    return response.data;
  },
};

export const analyticsService = {
  getDashboard: async (timeRange = 24) => {
    const response = await api.get('/api/analytics/dashboard', {
      params: { hours: timeRange },
    });
    return response.data;
  },

  getAnalytics: async () => {
    const response = await api.get('/api/analytics');
    return response.data;
  },

  getSessionHistory: async (limit = 10) => {
    const response = await api.get('/api/analytics/sessions', {
      params: { limit },
    });
    return response.data;
  },

  getAgentMetrics: async () => {
    const response = await api.get('/api/analytics/agents');
    return response.data;
  },
};

export default api;