import api from './api';

class BlockchainService {
  async getBlockchainStats() {
    try {
      const response = await api.get('/api/blockchain/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getBlock(blockNumber) {
    try {
      const response = await api.get(`/api/blockchain/blocks/${blockNumber}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRecentBlocks(limit = 10) {
    try {
      const response = await api.get(`/api/blockchain/blocks?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getTransaction(txHash) {
    try {
      const response = await api.get(`/api/blockchain/transactions/${txHash}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRecentTransactions(limit = 50) {
    try {
      const response = await api.get(`/api/blockchain/transactions?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async createTransaction(transactionData) {
    try {
      const response = await api.post('/api/blockchain/transactions', transactionData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getPendingTransactions() {
    try {
      const response = await api.get('/api/blockchain/pending-transactions');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async registerFirmwareUpdate(firmwareData) {
    try {
      const response = await api.post('/api/blockchain/firmware-update', firmwareData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async validateChain() {
    try {
      const response = await api.get('/api/blockchain/validate-chain');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getBlockchainExplorer() {
    try {
      const response = await api.get('/api/blockchain/explorer');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAddressInfo(address) {
    try {
      const response = await api.get(`/api/blockchain/address/${address}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new BlockchainService();