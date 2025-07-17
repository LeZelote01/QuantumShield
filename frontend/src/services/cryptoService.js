import api from './api';

class CryptoService {
  async generateKeys(keySize = 2048) {
    try {
      const response = await api.post('/api/crypto/generate-keys', { key_size: keySize });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async encryptMessage(data, publicKey) {
    try {
      const response = await api.post('/api/crypto/encrypt', {
        data,
        public_key: publicKey,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async decryptMessage(encryptedData, privateKey) {
    try {
      const response = await api.post('/api/crypto/decrypt', {
        encrypted_data: encryptedData,
        private_key: privateKey,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async signMessage(message, privateKey) {
    try {
      const response = await api.post('/api/crypto/sign', {
        message,
        private_key: privateKey,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async verifySignature(message, signature, publicKey) {
    try {
      const response = await api.post('/api/crypto/verify', {
        message,
        signature,
        public_key: publicKey,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getPerformanceMetrics() {
    try {
      const response = await api.get('/api/crypto/performance');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAlgorithmInfo() {
    try {
      const response = await api.get('/api/crypto/algorithm-info');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAlgorithmComparison() {
    try {
      const response = await api.get('/api/crypto/comparison');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new CryptoService();