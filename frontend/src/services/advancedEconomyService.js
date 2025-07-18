import api from './api';

class AdvancedEconomyService {
  // ===== MARKETPLACE SERVICES =====
  
  async createServiceListing(serviceData) {
    try {
      const response = await api.post('/api/advanced-economy/marketplace/services/create', serviceData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async searchServices(searchData) {
    try {
      const response = await api.post('/api/advanced-economy/marketplace/services/search', searchData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async purchaseService(purchaseData) {
    try {
      const response = await api.post('/api/advanced-economy/marketplace/services/purchase', purchaseData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMarketplaceStats() {
    try {
      const response = await api.get('/api/advanced-economy/marketplace/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== STAKING SERVICES =====
  
  async createStakingPool(poolData) {
    try {
      const response = await api.post('/api/advanced-economy/staking/pools/create', poolData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getStakingPools() {
    try {
      const response = await api.get('/api/advanced-economy/staking/pools');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async stakeTokens(stakeData) {
    try {
      const response = await api.post('/api/advanced-economy/staking/stake', stakeData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async unstakeTokens(unstakeData) {
    try {
      const response = await api.post('/api/advanced-economy/staking/unstake', unstakeData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getStakingDashboard() {
    try {
      const response = await api.get('/api/advanced-economy/staking/dashboard');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== LOAN SERVICES =====
  
  async createLoanRequest(loanData) {
    try {
      const response = await api.post('/api/advanced-economy/loans/create', loanData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async fundLoan(fundData) {
    try {
      const response = await api.post('/api/advanced-economy/loans/fund', fundData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== INSURANCE SERVICES =====
  
  async createInsurancePool(poolData) {
    try {
      const response = await api.post('/api/advanced-economy/insurance/pools/create', poolData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async purchaseInsurance(insuranceData) {
    try {
      const response = await api.post('/api/advanced-economy/insurance/purchase', insuranceData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== ASSET TOKENIZATION SERVICES =====
  
  async tokenizeAsset(assetData) {
    try {
      const response = await api.post('/api/advanced-economy/tokenization/assets/create', assetData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async buyAssetTokens(purchaseData) {
    try {
      const response = await api.post('/api/advanced-economy/tokenization/assets/buy', purchaseData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getTokenizedAssets() {
    try {
      const response = await api.get('/api/advanced-economy/tokenization/assets');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAssetOwnerships(userId) {
    try {
      const response = await api.get(`/api/advanced-economy/tokenization/ownerships/${userId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== DASHBOARD SERVICES =====
  
  async getEconomyDashboard() {
    try {
      const response = await api.get('/api/advanced-economy/dashboard');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRecommendations() {
    try {
      const response = await api.get('/api/advanced-economy/recommendations');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getHealthCheck() {
    try {
      const response = await api.get('/api/advanced-economy/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new AdvancedEconomyService();