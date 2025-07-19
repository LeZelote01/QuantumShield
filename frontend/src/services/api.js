import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001') + '/api',
  timeout: 5000,  // Timeout réduit à 5 secondes
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Log l'erreur pour debugging
    console.error('API Error:', error.message);
    
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      // Ne pas rediriger automatiquement si on n'est pas sur une page protégée
      if (window.location.pathname.startsWith('/dashboard')) {
        window.location.href = '/login';
      }
    }
    
    // Pour les erreurs de réseau, ne pas bloquer l'application
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.warn('Request timeout - continuing with fallback behavior');
    }
    
    return Promise.reject(error);
  }
);

export default api;