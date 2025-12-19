import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// AUTHENTICATION API
// ============================================================================

export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),

  login: (credentials) => {
    // OAuth2PasswordRequestForm expects form data
    const formData = new FormData();
    formData.append('username', credentials.email);  // username field contains email
    formData.append('password', credentials.password);

    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getCurrentUser: () => api.get('/auth/me'),

  logout: () => {
    localStorage.removeItem('token');
  },
};

// ============================================================================
// ANALYTICS API
// ============================================================================

export const analyticsAPI = {
  // Dashboard - get all analytics in one call
  getDashboard: (days = 30) =>
    api.get(`/analytics/dashboard?days=${days}`),

  // Booking statistics
  getBookingStats: (startDate, endDate) =>
    api.get('/analytics/bookings/stats', {
      params: { start_date: startDate, end_date: endDate }
    }),

  // Revenue statistics
  getRevenueStats: (startDate, endDate) =>
    api.get('/analytics/revenue/stats', {
      params: { start_date: startDate, end_date: endDate }
    }),

  // Popular routes
  getPopularRoutes: (limit = 10, startDate, endDate) =>
    api.get('/analytics/popular-routes', {
      params: { limit, start_date: startDate, end_date: endDate }
    }),

  // Daily trends
  getDailyTrends: (days = 30) =>
    api.get(`/analytics/daily-trends?days=${days}`),

  // Class distribution
  getClassDistribution: (startDate, endDate) =>
    api.get('/analytics/class-distribution', {
      params: { start_date: startDate, end_date: endDate }
    }),

  // Top spending passengers
  getTopSpenders: (limit = 10) =>
    api.get(`/analytics/passengers/top-spenders?limit=${limit}`),

  // Journey performance
  getJourneyPerformance: (limit = 10) =>
    api.get(`/analytics/journeys/performance?limit=${limit}`),
};

export default api;
