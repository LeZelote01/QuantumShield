import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { 
  KeyIcon, 
  LockClosedIcon, 
  LockOpenIcon,
  DocumentDuplicateIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import cryptoService from '../../services/cryptoService';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Cryptography = () => {
  const [activeTab, setActiveTab] = useState('keygen');
  const [keyPair, setKeyPair] = useState(null);
  const [encryptData, setEncryptData] = useState({ message: '', publicKey: '' });
  const [decryptData, setDecryptData] = useState({ encryptedData: '', privateKey: '' });
  const [signData, setSignData] = useState({ message: '', privateKey: '' });
  const [verifyData, setVerifyData] = useState({ message: '', signature: '', publicKey: '' });

  const { showSuccess, showError } = useToast();

  // Queries
  const { data: algorithmInfo } = useQuery('algorithmInfo', cryptoService.getAlgorithmInfo);
  const { data: comparison } = useQuery('comparison', cryptoService.getAlgorithmComparison);
  const { data: performance } = useQuery('performance', cryptoService.getPerformanceMetrics);

  // Mutations
  const generateKeysMutation = useMutation(cryptoService.generateKeys, {
    onSuccess: (data) => {
      setKeyPair(data);
      showSuccess('Paire de clés générée avec succès !');
    },
    onError: () => showError('Erreur lors de la génération des clés')
  });

  const encryptMutation = useMutation(
    ({ data, publicKey }) => cryptoService.encryptMessage(data, publicKey),
    {
      onSuccess: () => showSuccess('Message chiffré avec succès !'),
      onError: () => showError('Erreur lors du chiffrement')
    }
  );

  const decryptMutation = useMutation(
    ({ encryptedData, privateKey }) => cryptoService.decryptMessage(encryptedData, privateKey),
    {
      onSuccess: () => showSuccess('Message déchiffré avec succès !'),
      onError: () => showError('Erreur lors du déchiffrement')
    }
  );

  const signMutation = useMutation(
    ({ message, privateKey }) => cryptoService.signMessage(message, privateKey),
    {
      onSuccess: () => showSuccess('Message signé avec succès !'),
      onError: () => showError('Erreur lors de la signature')
    }
  );

  const verifyMutation = useMutation(
    ({ message, signature, publicKey }) => cryptoService.verifySignature(message, signature, publicKey),
    {
      onSuccess: () => showSuccess('Signature vérifiée avec succès !'),
      onError: () => showError('Erreur lors de la vérification')
    }
  );

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showSuccess('Copié dans le presse-papier !');
  };

  const tabs = [
    { id: 'keygen', label: 'Génération de clés', icon: KeyIcon },
    { id: 'encrypt', label: 'Chiffrement', icon: LockClosedIcon },
    { id: 'decrypt', label: 'Déchiffrement', icon: LockOpenIcon },
    { id: 'sign', label: 'Signature', icon: DocumentDuplicateIcon },
    { id: 'verify', label: 'Vérification', icon: CheckCircleIcon },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cryptographie NTRU++</h1>
        <p className="text-gray-600">
          Cryptographie post-quantique optimisée pour les dispositifs IoT
        </p>
      </div>

      {/* Algorithm Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Algorithme NTRU++">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Type</span>
              <span className="text-sm font-medium">Post-Quantum</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Taille clé</span>
              <span className="text-sm font-medium">2048 bits</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Sécurité</span>
              <span className="text-sm font-medium text-green-600">Résistant quantique</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Performance</span>
              <span className="text-sm font-medium text-blue-600">Optimisé IoT</span>
            </div>
          </div>
        </Card>

        <Card title="Comparaison RSA">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Vitesse</span>
              <span className="text-sm font-medium text-green-600">+300%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Mémoire</span>
              <span className="text-sm font-medium text-green-600">-50%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Énergie</span>
              <span className="text-sm font-medium text-green-600">-70%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Résistance quantique</span>
              <span className="text-sm font-medium text-green-600">Oui</span>
            </div>
          </div>
        </Card>

        <Card title="Métriques">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Chiffrement</span>
              <span className="text-sm font-medium">Rapide</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Déchiffrement</span>
              <span className="text-sm font-medium">Rapide</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Signature</span>
              <span className="text-sm font-medium">Rapide</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Vérification</span>
              <span className="text-sm font-medium">Rapide</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id 
                  ? 'border-indigo-500 text-indigo-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div>
        {activeTab === 'keygen' && (
          <Card title="Génération de clés NTRU++">
            <div className="space-y-6">
              <div className="text-center">
                <Button
                  onClick={() => generateKeysMutation.mutate()}
                  loading={generateKeysMutation.isLoading}
                  className="mb-4"
                >
                  Générer une nouvelle paire de clés
                </Button>
                <p className="text-sm text-gray-600">
                  Génère une paire de clés NTRU++ sécurisée (2048 bits)
                </p>
              </div>

              {keyPair && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clé publique
                    </label>
                    <div className="relative">
                      <textarea
                        value={keyPair.public_key}
                        readOnly
                        className="w-full h-32 p-3 border border-gray-300 rounded-lg bg-gray-50 text-sm font-mono"
                      />
                      <button
                        onClick={() => copyToClipboard(keyPair.public_key)}
                        className="absolute top-2 right-2 p-1 text-gray-500 hover:text-gray-700"
                      >
                        <DocumentDuplicateIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clé privée
                    </label>
                    <div className="relative">
                      <textarea
                        value={keyPair.private_key}
                        readOnly
                        className="w-full h-32 p-3 border border-gray-300 rounded-lg bg-gray-50 text-sm font-mono"
                      />
                      <button
                        onClick={() => copyToClipboard(keyPair.private_key)}
                        className="absolute top-2 right-2 p-1 text-gray-500 hover:text-gray-700"
                      >
                        <DocumentDuplicateIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Important :</strong> Conservez votre clé privée en sécurité. 
                      Elle ne peut pas être récupérée si elle est perdue.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {activeTab === 'encrypt' && (
          <Card title="Chiffrement de message">
            <div className="space-y-4">
              <Input
                label="Message à chiffrer"
                value={encryptData.message}
                onChange={(e) => setEncryptData({...encryptData, message: e.target.value})}
                placeholder="Entrez votre message..."
              />

              <Input
                label="Clé publique"
                value={encryptData.publicKey}
                onChange={(e) => setEncryptData({...encryptData, publicKey: e.target.value})}
                placeholder="Collez la clé publique..."
              />

              <Button
                onClick={() => encryptMutation.mutate(encryptData)}
                loading={encryptMutation.isLoading}
                disabled={!encryptData.message || !encryptData.publicKey}
              >
                Chiffrer le message
              </Button>

              {encryptMutation.data && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message chiffré
                  </label>
                  <div className="relative">
                    <textarea
                      value={encryptMutation.data.encrypted_data}
                      readOnly
                      className="w-full h-32 p-3 border border-gray-300 rounded-lg bg-gray-50 text-sm font-mono"
                    />
                    <button
                      onClick={() => copyToClipboard(encryptMutation.data.encrypted_data)}
                      className="absolute top-2 right-2 p-1 text-gray-500 hover:text-gray-700"
                    >
                      <DocumentDuplicateIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Autres onglets similaires... */}
      </div>
    </div>
  );
};

export default Cryptography;