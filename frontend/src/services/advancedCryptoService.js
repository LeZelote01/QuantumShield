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
  },

  // ==================== NOUVELLES MÉTHODES GESTION AVANCÉE ====================

  // Configurer la gestion avancée des clés
  async setupAdvancedKeyManagement(keypairId, expirationDays = 365, archiveAfterDays = 30) {
    try {
      const response = await api.post('/advanced-crypto/setup-advanced-key-management', {
        keypair_id: keypairId,
        expiration_days: expirationDays,
        archive_after_days: archiveAfterDays
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la configuration de la gestion avancée:', error);
      throw error;
    }
  },

  // Vérifier l'expiration des clés
  async checkKeyExpiration() {
    try {
      const response = await api.get('/advanced-crypto/check-key-expiration');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification d\'expiration:', error);
      throw error;
    }
  },

  // Opérations en masse sur les clés
  async bulkKeyOperations(operation, keypairIds) {
    try {
      const response = await api.post('/advanced-crypto/bulk-key-operations', {
        operation,
        keypair_ids: keypairIds
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'opération en masse:', error);
      throw error;
    }
  },

  // Obtenir le dashboard avancé
  async getAdvancedCryptoDashboard() {
    try {
      const response = await api.get('/advanced-crypto/advanced-crypto-dashboard');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du dashboard:', error);
      throw error;
    }
  },

  // Obtenir le trail d'audit
  async getAuditTrail(limit = 100) {
    try {
      const response = await api.get(`/advanced-crypto/audit-trail?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'audit:', error);
      throw error;
    }
  },

  // Vérifier l'intégrité d'un événement d'audit
  async verifyAuditIntegrity(auditId) {
    try {
      const response = await api.get(`/advanced-crypto/verify-audit-integrity/${auditId}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification d\'intégrité:', error);
      throw error;
    }
  },

  // Obtenir les statistiques cryptographiques
  async getCryptoStatistics() {
    try {
      const response = await api.get('/advanced-crypto/crypto-statistics');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques:', error);
      throw error;
    }
  },

  // Obtenir le check de santé cryptographique
  async getCryptoHealthCheck() {
    try {
      const response = await api.get('/advanced-crypto/crypto-health-check');
      return response.data;
    } catch (error) {
      console.error('Erreur lors du check de santé:', error);
      throw error;
    }
  },

  // Obtenir les informations de compatibilité HSM
  async getHSMCompatibility() {
    try {
      const response = await api.get('/advanced-crypto/hsm-compatibility');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des infos HSM:', error);
      throw error;
    }
  },

  // Obtenir les informations de conformité export
  async getExportCompliance() {
    try {
      const response = await api.get('/advanced-crypto/export-compliance');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des infos de conformité:', error);
      throw error;
    }
  },

  // ==================== ZERO-KNOWLEDGE PROOFS ====================

  // Générer une preuve zero-knowledge
  async generateZKProof(proofType, secretValue, publicParameters) {
    try {
      const response = await api.post('/advanced-crypto/generate-zk-proof', {
        proof_type: proofType,
        secret_value: secretValue,
        public_parameters: publicParameters
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la génération de la preuve ZK:', error);
      throw error;
    }
  },

  // Vérifier une preuve zero-knowledge
  async verifyZKProof(proofId) {
    try {
      const response = await api.post('/advanced-crypto/verify-zk-proof', {
        proof_id: proofId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification de la preuve ZK:', error);
      throw error;
    }
  },

  // ==================== SIGNATURE À SEUIL ====================

  // Configurer un schéma de signature à seuil
  async setupThresholdSignature(threshold, totalParties) {
    try {
      const response = await api.post('/advanced-crypto/setup-threshold-signature', {
        threshold,
        total_parties: totalParties
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la configuration du schéma à seuil:', error);
      throw error;
    }
  },

  // Effectuer une signature à seuil
  async thresholdSign(schemeId, message, signingParties) {
    try {
      const response = await api.post('/advanced-crypto/threshold-sign', {
        scheme_id: schemeId,
        message,
        signing_parties: signingParties
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la signature à seuil:', error);
      throw error;
    }
  },

  // Vérifier une signature à seuil
  async verifyThresholdSignature(signatureId) {
    try {
      const response = await api.post('/advanced-crypto/verify-threshold-signature', {
        signature_id: signatureId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification de la signature à seuil:', error);
      throw error;
    }
  }
};

export default advancedCryptoService;