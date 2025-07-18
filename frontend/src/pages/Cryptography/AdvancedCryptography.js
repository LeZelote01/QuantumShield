import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from 'react-query';
import { 
  ShieldCheckIcon, 
  KeyIcon, 
  CpuChipIcon, 
  ArrowPathIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import advancedCryptoService from '../../services/advancedCryptoService';

const AdvancedCryptography = () => {
  const [selectedEncryptionAlg, setSelectedEncryptionAlg] = useState('Kyber-768');
  const [selectedSignatureAlg, setSelectedSignatureAlg] = useState('Dilithium-3');
  const [currentKeypair, setCurrentKeypair] = useState(null);
  const [testMessage, setTestMessage] = useState('');
  const [encryptedData, setEncryptedData] = useState(null);
  const [batchMessages, setBatchMessages] = useState(['']);
  const [rotationInterval, setRotationInterval] = useState(24);
  const [activeTab, setActiveTab] = useState('algorithms');

  // Récupérer les algorithmes supportés
  const { data: supportedAlgorithms, isLoading: algorithmsLoading } = useQuery(
    'supportedAlgorithms',
    advancedCryptoService.getSupportedAlgorithms
  );

  // Récupérer les recommandations
  const { data: recommendations } = useQuery(
    'algorithmRecommendations',
    advancedCryptoService.getAlgorithmRecommendations
  );

  // Récupérer la comparaison des performances
  const { data: performanceComparison } = useQuery(
    'performanceComparison',
    advancedCryptoService.getPerformanceComparison
  );

  // Mutations
  const generateKeypairMutation = useMutation(
    ({ encryptionAlg, signatureAlg }) => 
      advancedCryptoService.generateMultiAlgorithmKeypair(encryptionAlg, signatureAlg),
    {
      onSuccess: (data) => {
        setCurrentKeypair(data.keypair);
        toast.success('Paire de clés générée avec succès !');
      },
      onError: (error) => {
        toast.error(`Erreur: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const encryptMutation = useMutation(
    ({ message, keypairId }) => 
      advancedCryptoService.hybridEncrypt(message, keypairId),
    {
      onSuccess: (data) => {
        setEncryptedData(data.encrypted_data);
        toast.success('Message chiffré avec succès !');
      },
      onError: (error) => {
        toast.error(`Erreur de chiffrement: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const decryptMutation = useMutation(
    ({ encryptedData, keypairId }) => 
      advancedCryptoService.hybridDecrypt(encryptedData, keypairId),
    {
      onSuccess: (data) => {
        toast.success(`Message déchiffré: ${data.decrypted_message}`);
      },
      onError: (error) => {
        toast.error(`Erreur de déchiffrement: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const batchEncryptMutation = useMutation(
    ({ messages, keypairId }) => 
      advancedCryptoService.batchEncrypt(messages, keypairId),
    {
      onSuccess: (data) => {
        const { successful, failed } = data.summary;
        toast.success(`Chiffrement par lots terminé: ${successful} réussis, ${failed} échoués`);
      },
      onError: (error) => {
        toast.error(`Erreur de chiffrement par lots: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const rotationMutation = useMutation(
    ({ keypairId, policy, interval }) => 
      advancedCryptoService.setupKeyRotation(keypairId, policy, interval),
    {
      onSuccess: () => {
        toast.success('Rotation des clés configurée avec succès !');
      },
      onError: (error) => {
        toast.error(`Erreur de configuration: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const handleGenerateKeypair = () => {
    generateKeypairMutation.mutate({
      encryptionAlg: selectedEncryptionAlg,
      signatureAlg: selectedSignatureAlg
    });
  };

  const handleEncrypt = () => {
    if (!currentKeypair || !testMessage) {
      toast.error('Veuillez générer une paire de clés et saisir un message');
      return;
    }
    encryptMutation.mutate({
      message: testMessage,
      keypairId: currentKeypair.keypair_id
    });
  };

  const handleDecrypt = () => {
    if (!currentKeypair || !encryptedData) {
      toast.error('Veuillez d\'abord chiffrer un message');
      return;
    }
    decryptMutation.mutate({
      encryptedData: encryptedData,
      keypairId: currentKeypair.keypair_id
    });
  };

  const handleBatchEncrypt = () => {
    if (!currentKeypair || batchMessages.filter(msg => msg.trim()).length === 0) {
      toast.error('Veuillez générer une paire de clés et saisir des messages');
      return;
    }
    const validMessages = batchMessages.filter(msg => msg.trim());
    batchEncryptMutation.mutate({
      messages: validMessages,
      keypairId: currentKeypair.keypair_id
    });
  };

  const handleSetupRotation = () => {
    if (!currentKeypair) {
      toast.error('Veuillez générer une paire de clés');
      return;
    }
    rotationMutation.mutate({
      keypairId: currentKeypair.keypair_id,
      policy: 'time_based',
      interval: rotationInterval
    });
  };

  const addBatchMessage = () => {
    setBatchMessages([...batchMessages, '']);
  };

  const removeBatchMessage = (index) => {
    setBatchMessages(batchMessages.filter((_, i) => i !== index));
  };

  const updateBatchMessage = (index, value) => {
    const newMessages = [...batchMessages];
    newMessages[index] = value;
    setBatchMessages(newMessages);
  };

  const getSecurityLevel = (algorithm) => {
    const levels = {
      'Kyber-512': 1,
      'Kyber-768': 3,
      'Kyber-1024': 5,
      'Dilithium-2': 2,
      'Dilithium-3': 3,
      'Dilithium-5': 5
    };
    return levels[algorithm] || 1;
  };

  const getSecurityLevelColor = (level) => {
    const colors = {
      1: 'bg-yellow-100 text-yellow-800',
      2: 'bg-green-100 text-green-800',
      3: 'bg-blue-100 text-blue-800',
      4: 'bg-indigo-100 text-indigo-800',
      5: 'bg-purple-100 text-purple-800'
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  const tabs = [
    { id: 'algorithms', name: 'Algorithmes', icon: ShieldCheckIcon },
    { id: 'keygen', name: 'Génération de clés', icon: KeyIcon },
    { id: 'encryption', name: 'Chiffrement', icon: CpuChipIcon },
    { id: 'batch', name: 'Chiffrement par lots', icon: CpuChipIcon },
    { id: 'rotation', name: 'Rotation des clés', icon: ArrowPathIcon },
    { id: 'performance', name: 'Performance', icon: InformationCircleIcon }
  ];

  if (algorithmsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Cryptographie Post-Quantique Avancée</h1>
        <p className="text-gray-600">
          Explorez les algorithmes Kyber et Dilithium avec fonctionnalités avancées
        </p>
      </div>

      {/* Navigation par onglets */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'algorithms' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Algorithmes Supportés</h2>
            {supportedAlgorithms?.algorithms && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(supportedAlgorithms.algorithms).map(([name, info]) => (
                  <div key={name} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{name}</h3>
                      <span className={`px-2 py-1 text-xs rounded ${
                        info.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {info.available ? 'Disponible' : 'Indisponible'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{info.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">Type: {info.type}</span>
                      {info.security_level && (
                        <span className={`px-2 py-1 text-xs rounded ${
                          getSecurityLevelColor(info.security_level)
                        }`}>
                          Niveau {info.security_level}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recommandations */}
          {recommendations && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-4">Recommandations par Cas d'Usage</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(recommendations.recommendations).map(([useCase, rec]) => (
                  <div key={useCase} className="border rounded-lg p-4">
                    <h3 className="font-medium mb-2">{rec.description}</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Chiffrement:</span>
                        <span className="text-sm font-medium">{rec.encryption}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Signature:</span>
                        <span className="text-sm font-medium">{rec.signature}</span>
                      </div>
                      <div className="mt-2">
                        <span className="text-xs text-gray-500">Avantages:</span>
                        <ul className="text-xs text-gray-600 mt-1">
                          {rec.benefits.map((benefit, index) => (
                            <li key={index} className="flex items-center">
                              <CheckCircleIcon className="h-3 w-3 text-green-500 mr-1" />
                              {benefit}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'keygen' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Génération de Clés Multi-Algorithmes</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Algorithme de Chiffrement
                </label>
                <select
                  value={selectedEncryptionAlg}
                  onChange={(e) => setSelectedEncryptionAlg(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="Kyber-512">Kyber-512</option>
                  <option value="Kyber-768">Kyber-768</option>
                  <option value="Kyber-1024">Kyber-1024</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Algorithme de Signature
                </label>
                <select
                  value={selectedSignatureAlg}
                  onChange={(e) => setSelectedSignatureAlg(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="Dilithium-2">Dilithium-2</option>
                  <option value="Dilithium-3">Dilithium-3</option>
                  <option value="Dilithium-5">Dilithium-5</option>
                </select>
              </div>
            </div>
            
            <button
              onClick={handleGenerateKeypair}
              disabled={generateKeypairMutation.isLoading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {generateKeypairMutation.isLoading ? 'Génération...' : 'Générer Paire de Clés'}
            </button>

            {currentKeypair && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium mb-2">Paire de Clés Générée</h3>
                <div className="space-y-2 text-sm">
                  <div><strong>ID:</strong> {currentKeypair.keypair_id}</div>
                  <div><strong>Chiffrement:</strong> {currentKeypair.encryption_algorithm}</div>
                  <div><strong>Signature:</strong> {currentKeypair.signature_algorithm}</div>
                  <div><strong>Créé le:</strong> {new Date(currentKeypair.created_at).toLocaleString()}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'encryption' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Chiffrement Hybride</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message à chiffrer
              </label>
              <textarea
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                rows={3}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="Entrez votre message..."
              />
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={handleEncrypt}
                disabled={encryptMutation.isLoading || !currentKeypair}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {encryptMutation.isLoading ? 'Chiffrement...' : 'Chiffrer'}
              </button>
              <button
                onClick={handleDecrypt}
                disabled={decryptMutation.isLoading || !encryptedData}
                className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50"
              >
                {decryptMutation.isLoading ? 'Déchiffrement...' : 'Déchiffrer'}
              </button>
            </div>

            {encryptedData && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium mb-2">Données Chiffrées</h3>
                <div className="text-xs text-gray-600 space-y-1">
                  <div><strong>Algorithme:</strong> {encryptedData.algorithm}</div>
                  <div><strong>Ciphertext KEM:</strong> {encryptedData.kem_ciphertext.substring(0, 50)}...</div>
                  <div><strong>Message chiffré:</strong> {encryptedData.encrypted_message.substring(0, 50)}...</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'batch' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Chiffrement par Lots</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Messages à chiffrer
              </label>
              {batchMessages.map((message, index) => (
                <div key={index} className="flex items-center space-x-2 mb-2">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => updateBatchMessage(index, e.target.value)}
                    className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder={`Message ${index + 1}...`}
                  />
                  {batchMessages.length > 1 && (
                    <button
                      onClick={() => removeBatchMessage(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <XCircleIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={addBatchMessage}
                className="text-blue-600 hover:text-blue-700 text-sm"
              >
                + Ajouter un message
              </button>
            </div>
            
            <button
              onClick={handleBatchEncrypt}
              disabled={batchEncryptMutation.isLoading || !currentKeypair}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {batchEncryptMutation.isLoading ? 'Chiffrement par lots...' : 'Chiffrer par Lots'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'rotation' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Rotation des Clés</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Intervalle de rotation (heures)
              </label>
              <input
                type="number"
                value={rotationInterval}
                onChange={(e) => setRotationInterval(Number(e.target.value))}
                min="1"
                max="8760"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            
            <button
              onClick={handleSetupRotation}
              disabled={rotationMutation.isLoading || !currentKeypair}
              className="w-full bg-orange-600 text-white py-2 px-4 rounded-md hover:bg-orange-700 disabled:opacity-50"
            >
              {rotationMutation.isLoading ? 'Configuration...' : 'Configurer la Rotation'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'performance' && performanceComparison && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Comparaison des Performances</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Algorithme
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Génération
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Chiffrement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Signature
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mémoire
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Post-Quantique
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(performanceComparison.performance_comparison.algorithms).map(([name, perf]) => (
                  <tr key={name}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {perf.key_generation}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {perf.encryption}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {perf.signature}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {perf.memory_usage}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {perf.quantum_resistant ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-500" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedCryptography;