import api from './api';

class DashboardService {
  async getDashboardOverview() {
    try {
      const response = await api.get('/api/dashboard/overview');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDashboardStats(timeframe = '24h') {
    try {
      const response = await api.get(`/api/dashboard/stats?timeframe=${timeframe}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDevicesOverview() {
    try {
      const response = await api.get('/api/dashboard/devices-overview');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getNetworkStatus() {
    try {
      const response = await api.get('/api/dashboard/network-status');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRecentActivity(limit = 20) {
    try {
      const response = await api.get(`/api/dashboard/recent-activity?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getPerformanceMetrics() {
    try {
      const response = await api.get('/api/dashboard/performance');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAlerts() {
    try {
      const response = await api.get('/api/dashboard/alerts');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new DashboardService();