import api from './api';

class AuthService {
  async login(credentials) {
    try {
      const response = await api.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async register(userData) {
    try {
      const response = await api.post('/api/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async logout() {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async getProfile() {
    try {
      const response = await api.get('/api/auth/profile');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await api.put('/api/auth/profile', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async changePassword(passwordData) {
    try {
      const response = await api.post('/api/auth/change-password', passwordData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getUserStats() {
    try {
      const response = await api.get('/api/auth/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async verifyToken() {
    try {
      const response = await api.get('/api/auth/verify-token');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new AuthService();
export const authService = new AuthService();