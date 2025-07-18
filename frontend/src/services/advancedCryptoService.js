/**
 * Service pour la cryptographie post-quantique avancée
 */

import api from './api';

export const advancedCryptoService = {
  // Obtenir les algorithmes supportés
  async getSupportedAlgorithms() {
    try {
      const response = await api.get('/advanced-crypto/supported-algorithms');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des algorithmes:', error);
      throw error;
    }
  },

  // Générer une paire de clés multi-algorithmes
  async generateMultiAlgorithmKeypair(encryptionAlgorithm = 'Kyber-768', signatureAlgorithm = 'Dilithium-3') {
    try {
      const response = await api.post('/advanced-crypto/generate-multi-algorithm-keypair', {
        encryption_algorithm: encryptionAlgorithm,
        signature_algorithm: signatureAlgorithm
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la génération des clés:', error);
      throw error;
    }
  },

  // Chiffrement hybride
  async hybridEncrypt(message, keypairId) {
    try {
      const response = await api.post('/advanced-crypto/hybrid-encrypt', {
        message,
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du chiffrement hybride:', error);
      throw error;
    }
  },

  // Déchiffrement hybride
  async hybridDecrypt(encryptedData, keypairId) {
    try {
      const response = await api.post('/advanced-crypto/hybrid-decrypt', {
        encrypted_data: encryptedData,
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du déchiffrement hybride:', error);
      throw error;
    }
  },

  // Chiffrement par lots
  async batchEncrypt(messages, keypairId) {
    try {
      const response = await api.post('/advanced-crypto/batch-encrypt', {
        messages,
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du chiffrement par lots:', error);
      throw error;
    }
  },

  // Déchiffrement par lots
  async batchDecrypt(encryptedMessages, keypairId) {
    try {
      const response = await api.post('/advanced-crypto/batch-decrypt', {
        encrypted_messages: encryptedMessages,
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du déchiffrement par lots:', error);
      throw error;
    }
  },

  // Signature avec Dilithium
  async signWithDilithium(message, keypairId) {
    try {
      const response = await api.post('/advanced-crypto/sign-dilithium', {
        message,
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la signature Dilithium:', error);
      throw error;
    }
  },

  // Vérification signature Dilithium
  async verifyDilithiumSignature(message, signature, keypairId) {
    try {
      const response = await api.post('/advanced-crypto/verify-dilithium', {
        message,
        signature,
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification Dilithium:', error);
      throw error;
    }
  },

  // Configurer la rotation des clés
  async setupKeyRotation(keypairId, policy = 'time_based', rotationInterval = 24) {
    try {
      const response = await api.post('/advanced-crypto/setup-key-rotation', {
        keypair_id: keypairId,
        policy,
        rotation_interval: rotationInterval
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la configuration de la rotation:', error);
      throw error;
    }
  },

  // Effectuer la rotation des clés
  async rotateKeys(keypairId) {
    try {
      const response = await api.post('/advanced-crypto/rotate-keys', {
        keypair_id: keypairId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la rotation des clés:', error);
      throw error;
    }
  },

  // Obtenir le statut de rotation des clés
  async getKeyRotationStatus(keypairId) {
    try {
      const response = await api.get(`/advanced-crypto/key-rotation-status/${keypairId}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du statut de rotation:', error);
      throw error;
    }
  },

  // Obtenir la comparaison des performances
  async getPerformanceComparison() {
    try {
      const response = await api.get('/advanced-crypto/performance-comparison');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des performances:', error);
      throw error;
    }
  },

  // Obtenir les recommandations d'algorithmes
  async getAlgorithmRecommendations() {
    try {
      const response = await api.get('/advanced-crypto/algorithm-recommendations');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des recommandations:', error);
      throw error;
    }
  }
};

export default advancedCryptoService;