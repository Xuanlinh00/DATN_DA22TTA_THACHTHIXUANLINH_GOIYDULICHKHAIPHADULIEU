import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Services
export const destinationsApi = {
  getAll: (params = {}) => api.get('/destinations', { params }),
  getByName: (name) => api.get(`/destinations/${encodeURIComponent(name)}`),
  search: (query) => api.get('/destinations/search', { params: { q: query } }),
  getSimilar: (name) => api.get(`/destinations/${encodeURIComponent(name)}/similar`),
};

export const recommendationsApi = {
  getFiltered: (filters) => api.post('/recommendations', filters),
  getSeasonal: (season, limit = 6) => api.get(`/recommendations/seasonal/${season}`, { params: { limit } }),
};

export const filtersApi = {
  getOptions: () => api.get('/filters/options'),
};

export const chatApi = {
  sendMessage: (message, history = []) => api.post('/chat', { message, conversation_history: history }),
};

export const dataApi = {
  getSummary: () => api.get('/data/summary'),
};

export default api;
