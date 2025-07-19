import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || '/api',
  timeout: 15000,  // Timeout augmenté à 15 secondes
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
    // Log l'erreur pour debugging avec plus de détails
    console.error('API Error Details:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method
    });
    
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