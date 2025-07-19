import api from './api';

class TokenService {
  async getBalance() {
    try {
      const response = await api.get('/tokens/balance');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async transferTokens(transferData) {
    try {
      const response = await api.post('/tokens/transfer', transferData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getTransactions(limit = 100) {
    try {
      const response = await api.get(`/tokens/transactions?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRewards(limit = 100) {
    try {
      const response = await api.get(`/tokens/rewards?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getTokenStats() {
    try {
      const response = await api.get('/tokens/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getUserScore() {
    try {
      const response = await api.get('/tokens/score');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getLeaderboard(limit = 50) {
    try {
      const response = await api.get(`/tokens/leaderboard?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRewardRates() {
    try {
      const response = await api.get('/tokens/reward-rates');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async claimReward(rewardData) {
    try {
      const response = await api.post('/tokens/claim-reward', rewardData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getPortfolio() {
    try {
      const response = await api.get('/tokens/portfolio');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMarketInfo() {
    try {
      const response = await api.get('/tokens/market-info');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new TokenService();