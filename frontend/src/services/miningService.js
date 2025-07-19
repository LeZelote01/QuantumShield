import api from './api';

class MiningService {
  async getMiningStats() {
    try {
      const response = await api.get('/api/mining/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiningTask() {
    try {
      const response = await api.get('/api/mining/task');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async submitMiningResult(resultData) {
    try {
      const response = await api.post('/api/mining/submit', resultData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiningHistory() {
    try {
      const response = await api.get('/api/mining/history');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async registerMiner(registrationData) {
    try {
      const response = await api.post('/api/mining/register', registrationData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getCurrentDifficulty() {
    try {
      const response = await api.get('/api/mining/difficulty');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiningRewards() {
    try {
      const response = await api.get('/api/mining/rewards');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiningPoolInfo() {
    try {
      const response = await api.get('/api/mining/pool-info');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiningCalculator(hashRate = 1000) {
    try {
      const response = await api.get(`/api/mining/calculator?hash_rate=${hashRate}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiningLeaderboard(limit = 50) {
    try {
      const response = await api.get(`/api/mining/leaderboard?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new MiningService();