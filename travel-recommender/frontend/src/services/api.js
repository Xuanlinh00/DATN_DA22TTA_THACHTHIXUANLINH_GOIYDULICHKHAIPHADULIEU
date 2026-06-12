import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Helper: get or create anonymous user ID (stored in localStorage) ─────────
export const getOrCreateUserId = () => {
  let uid = localStorage.getItem('nomadai_user_id');
  if (!uid) {
    uid = 'user_' + Math.random().toString(36).substring(2, 11);
    localStorage.setItem('nomadai_user_id', uid);
  }
  return uid;
};

export const authApi = {
  register: (username, password, fullName, email) => api.post('/auth/register', { username, password, full_name: fullName, email }),
  login:    (username, password)           => api.post('/auth/login', { username, password }),
  forgotPassword: (email)                  => api.post('/auth/forgot-password', { email }),
  resetPassword: (email, token, newPassword) => api.post('/auth/reset-password', { email, token, new_password: newPassword }),
};

// ── API Services ─────────────────────────────────────────────────────────────
export const destinationsApi = {
  getAll:          (params = {})          => api.get('/destinations', { params }),
  getByName:       (name)                 => api.get(`/destinations/${encodeURIComponent(name)}`),
  search:          (query)                => api.get('/destinations/search', { params: { q: query } }),
  getSimilar:      (name)                 => api.get(`/destinations/${encodeURIComponent(name)}/similar`),
  getWeather:      (name)                 => api.get(`/destinations/${encodeURIComponent(name)}/weather`),
  getClimate:      (name)                 => api.get(`/destinations/${encodeURIComponent(name)}/climate`),
  rateDestination: (name, rating, userId) => api.post(`/destinations/${encodeURIComponent(name)}/rate`, { user_id: userId, rating }),
  getMyRating:     (name, userId)         => api.get(`/destinations/${encodeURIComponent(name)}/my-rating`, { params: { user_id: userId } }),
};

export const recommendationsApi = {
  getFiltered: (filters)              => api.post('/recommendations', filters),
  getSeasonal: (season, limit = 6)    => api.get(`/recommendations/seasonal/${season}`, { params: { limit } }),
};

export const filtersApi = {
  getOptions: () => api.get('/filters/options'),
};

export const chatApi = {
  sendMessage: (message, history = [], recommendationContext = null, sessionId = 'default') =>
    api.post('/chat', { message, conversation_history: history, recommendation_context: recommendationContext, session_id: sessionId }),
  getSessions: (userId) => api.get('/chat/sessions', { params: { user_id: userId } }),
  getSession: (sessionId) => api.get(`/chat/sessions/${sessionId}`),
  saveSession: (sessionId, userId, title, messages) => api.post('/chat/sessions', { session_id: sessionId, user_id: userId, title, messages }),
  deleteSession: (sessionId) => api.delete(`/chat/sessions/${sessionId}`),
};

export const dataApi = {
  getSummary: () => api.get('/data/summary'),
  getStats:   () => api.get('/stats'),
};

export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  getRules: () => api.get('/admin/rules'),
  getRatings: (limit = 150) => api.get('/admin/ratings', { params: { limit } }),
  deleteRating: (userId, destinationName) => api.delete('/admin/ratings', { params: { user_id: userId, destination_name: destinationName } }),
  runApriori: (minSupport, minConfidence, minLift) => api.post('/admin/mine-apriori', { min_support: minSupport, min_confidence: minConfidence, min_lift: minLift }),
  runClustering: (nClusters) => api.post('/admin/run-clustering', { n_clusters: nClusters }),
  refreshCF: () => api.post('/admin/refresh-cf'),
};

export default api;
